"""A command to update OWASP entities from owasp.org data."""

import logging
import os
import time

import github
import requests
from django.core.management.base import BaseCommand
from github.GithubException import UnknownObjectException
from lxml import etree, html

from apps.github.constants import GITHUB_ITEMS_PER_PAGE, GITHUB_USER_RE
from apps.github.utils import normalize_url
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Updates OWASP entities based on their owasp.org data."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        active_projects = Project.objects.filter(is_active=True).order_by(
            "owasp_repository__created_at"
        )
        active_projects_count = active_projects.count()
        gh = github.Github(os.getenv("GITHUB_TOKEN"), per_page=GITHUB_ITEMS_PER_PAGE)

        offset = options["offset"]
        projects = []
        for idx, project in enumerate(active_projects[offset:]):
            prefix = f"{idx + offset + 1} of {active_projects_count - offset}"
            print(f"{prefix:<10} {project.owasp_url}")

            page_response = requests.get(project.owasp_url, timeout=10)
            if page_response.status_code == requests.codes.not_found:
                project.deactivate()
                continue

            try:
                page_tree = html.fromstring(page_response.content)
            except etree.ParserError:
                project.deactivate()
                continue

            # Get GitHub URLs.
            scraped_urls = sorted(
                {
                    normalize_url(repository_url)
                    for url in set(
                        page_tree.xpath(
                            "//div[@class='sidebar']//a[contains(@href, 'github.com')]/@href"
                        )
                    )
                    if (repository_url := project.get_related_url(url))
                }
            )

            invalid_urls = set()
            related_urls = set()
            for scraped_url in scraped_urls:
                # Check for redirects.
                github_response = requests.get(scraped_url, allow_redirects=False, timeout=10)
                github_url = None
                if github_response.status_code == requests.codes.ok:
                    github_url = scraped_url
                elif github_response.status_code in {
                    requests.codes.moved_permanently,  # 301
                    requests.codes.found,  # 302
                    requests.codes.see_other,  # 303
                    requests.codes.temporary_redirect,  # 307
                    requests.codes.permanent_redirect,  # 308
                }:
                    github_url = github_response.headers["Location"]

                if not github_url:
                    invalid_urls.add(scraped_url)
                    logger.warning("Couldn't verify URL %s", scraped_url)
                    continue

                github_url = project.get_related_url(normalize_url(github_url))
                if github_url:
                    if GITHUB_USER_RE.match(github_url):
                        try:
                            gh_organization = gh.get_organization(github_url.split("/")[-1])
                            related_urls.update(
                                f"https://github.com/{gh_repository.full_name.lower()}"
                                for gh_repository in gh_organization.get_repos()
                            )
                        except UnknownObjectException:
                            logger.info(
                                "Couldn't get GitHub organization repositories for %s", github_url
                            )
                    else:
                        related_urls.add(github_url)
                else:
                    logger.info("Skipped related URL %s", github_url)

            project.invalid_urls = sorted(invalid_urls)
            project.related_urls = sorted(related_urls)

            # Get leaders.
            leaders_header = page_tree.xpath("//div[@class='sidebar']//*[@id='leaders']")
            if leaders_header:
                leaders_ul = leaders_header[0].getnext()
                if leaders_ul is not None and leaders_ul.tag == "ul":
                    leaders = sorted(name.strip() for name in leaders_ul.xpath(".//li/a/text()"))
                    if leaders:
                        project.leaders_raw = leaders

            projects.append(project)

            time.sleep(0.5)

        # Bulk save data.
        Project.bulk_save(projects)
