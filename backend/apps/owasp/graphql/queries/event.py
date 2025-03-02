"""OWASP event GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.event import EventNode
from apps.owasp.models.event import Event


class EventQuery(BaseQuery):
    """Event queries."""

    upcoming_events = graphene.List(EventNode)

    def resolve_upcoming_events(root, info):
        """Resolve all events."""
        return Event.upcoming_events
