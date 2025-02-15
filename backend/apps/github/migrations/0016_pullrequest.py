# Generated by Django 5.1.6 on 2025-02-15 11:03

import django.db.models.deletion
from django.db import migrations, models

import apps.github.models.mixins.issue


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0015_alter_release_author"),
    ]

    operations = [
        migrations.CreateModel(
            name="PullRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("nest_created_at", models.DateTimeField(auto_now_add=True)),
                ("nest_updated_at", models.DateTimeField(auto_now=True)),
                ("node_id", models.CharField(unique=True, verbose_name="Node ID")),
                ("title", models.CharField(max_length=1000, verbose_name="Title")),
                ("body", models.TextField(default="", verbose_name="Body")),
                (
                    "state",
                    models.CharField(
                        choices=[("open", "Open"), ("closed", "Closed")],
                        default="open",
                        max_length=20,
                        verbose_name="State",
                    ),
                ),
                ("url", models.URLField(default="", max_length=500, verbose_name="URL")),
                ("number", models.PositiveBigIntegerField(default=0, verbose_name="Number")),
                (
                    "sequence_id",
                    models.PositiveBigIntegerField(default=0, verbose_name="Pull Requests ID"),
                ),
                ("is_locked", models.BooleanField(default=False, verbose_name="Is Locked")),
                (
                    "comments_count",
                    models.PositiveIntegerField(default=0, verbose_name="Comments"),
                ),
                (
                    "closed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Closed at"),
                ),
                ("created_at", models.DateTimeField(verbose_name="Created at")),
                ("updated_at", models.DateTimeField(db_index=True, verbose_name="Updated at")),
                (
                    "merged_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Merged at"),
                ),
                (
                    "assignees",
                    models.ManyToManyField(
                        blank=True,
                        related_name="assigned_pull_requests",
                        to="github.user",
                        verbose_name="Assignees",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_pull_requests",
                        to="github.user",
                        verbose_name="Author",
                    ),
                ),
                (
                    "labels",
                    models.ManyToManyField(
                        blank=True,
                        related_name="pull_request_labels",
                        to="github.label",
                        verbose_name="Labels",
                    ),
                ),
                (
                    "repository",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pull_requests",
                        to="github.repository",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Pull Requests",
                "db_table": "github_pullrequests",
                "ordering": ("-updated_at", "-state"),
            },
            bases=(apps.github.models.mixins.issue.IssueIndexMixin, models.Model),
        ),
    ]
