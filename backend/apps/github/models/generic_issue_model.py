"""Github app Generic model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import NodeModel
from apps.github.models.mixins import IssueIndexMixin


class GenericIssueModel(BulkSaveModel, IssueIndexMixin, NodeModel, TimestampedModel):
    """Generic Issue And PR model."""

    objects = models.Manager()

    class Meta:
        abstract = True

    class State(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    title = models.CharField(verbose_name="Title", max_length=1000)
    body = models.TextField(verbose_name="Body", default="")

    state = models.CharField(verbose_name="State", max_length=6, choices=State, default=State.OPEN)
    url = models.URLField(verbose_name="URL", max_length=500, default="")

    number = models.PositiveBigIntegerField(verbose_name="Number", default=0)
    sequence_id = models.PositiveBigIntegerField(verbose_name="ID", default=0)

    closed_at = models.DateTimeField(verbose_name="Closed at", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Created at")
    updated_at = models.DateTimeField(verbose_name="Updated at", db_index=True)

    def __str__(self):
        """Issue human readable representation."""
        return f"{self.title} by {self.author}"

    @property
    def is_open(self):
        """Return whether issue is open."""
        return self.state == self.State.OPEN

    @property
    def project(self):
        """Return project."""
        return self.repository.project

    @property
    def repository_id(self):
        """Return repository ID."""
        return self.repository.id
