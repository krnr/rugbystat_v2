from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .filters import TeamFullTextFilter
from .models import Team, TeamSeason, Person, PersonSeason
from .serializers import (
    TeamSerializer,
    TeamSeasonSerializer,
    PersonSerializer,
    PersonSeasonSerializer,
)

__author__ = "krnr"


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Team.objects.select_related("city", "parent")
        .prefetch_related("document_set")
        .order_by("year", "id")
    )
    serializer_class = TeamSerializer
    filter_backends = (
        TeamFullTextFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    filterset_fields = "year", "short_name"
    search_fields = ("^short_name", "^city__name", "^names__name")
    page_size_query_param = "limit"


class TeamSeasonViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = TeamSeason.objects.all()
    serializer_class = TeamSeasonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    filterset_fields = ("year",)
    search_fields = "name", "^season__name"
    page_size_query_param = "limit"


class PersonViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = Person.objects.order_by("name")
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    filterset_fields = ("year_birth", "name")
    search_fields = ("^name",)


class PersonSeasonViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    queryset = PersonSeason.objects.all()
    serializer_class = PersonSeasonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

