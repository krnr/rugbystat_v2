from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from clippings.views import import_from_dropbox
from clippings.viewsets import DocumentViewSet, SourceViewSet, SourceObjectViewSet
from main import views
from matches.views import (
    import_seasons,
    import_table,
    SeasonCreateView,
    SeasonDetailView,
    SeasonYearView,
    MatchDetailView,
    TournamentListView,
    TournamentDetailView,
    TournamentAutocomplete,
    SeasonAutocomplete,
)
from teams.views import (
    import_teams,
    PersonCreateView,
    PersonUpdateView,
    TeamUpdateView,
    TeamSeasonView,
    TeamAllYearView,
    TagAutocomplete,
    CityAutocomplete,
    TeamAutocomplete,
    TeamSeasonAutocomplete,
    PersonSeasonAutocomplete,
    TeamBySeasonAutocomplete,
    PersonBySeasonAutocomplete,
)
from teams.viewsets import (
    TeamViewSet,
    TeamSeasonViewSet,
    PersonViewSet,
    PersonSeasonViewSet,
)
from matches.viewsets import MatchViewSet, SeasonViewSet
from users.viewsets import UserViewSet

# ----------------------------
# Routers
# ----------------------------
router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"teams", TeamViewSet)
router.register(r"teams-seasons", TeamSeasonViewSet)
router.register(r"persons", PersonViewSet)
router.register(r"personseasons", PersonSeasonViewSet)
router.register(r"documents", DocumentViewSet, basename="document")
router.register(
    r"teams/(?P<team_id>\d+)/documents", DocumentViewSet, basename="team-documents"
)
router.register(r"sources", SourceViewSet)
router.register(r"issues", SourceObjectViewSet)
router.register(r"seasons", SeasonViewSet)
router.register(r"matches", MatchViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/v1/", include(router.urls)),
    path("api/v1/", include("authentication.urls")),
    path("markdownx/", include("markdownx.urls")),
    path("import-teams/", import_teams),
    path("import-seasons/", import_seasons, name="import_seasons"),
    path("import-table/", import_table, name="import_table"),
    path("dropbox-webhook/", import_from_dropbox),
    # --- Autocompletes ---
    path("autocomplete-tags/", TagAutocomplete.as_view(), name="autocomplete-tags"),
    path(
        "autocomplete-cities/", CityAutocomplete.as_view(), name="autocomplete-cities"
    ),
    path(
        "autocomplete-tournaments/",
        TournamentAutocomplete.as_view(),
        name="autocomplete-tournaments",
    ),
    path(
        "autocomplete-seasons/",
        SeasonAutocomplete.as_view(),
        name="autocomplete-seasons",
    ),
    path("autocomplete-teams/", TeamAutocomplete.as_view(), name="autocomplete-teams"),
    path(
        "autocomplete-teamseasons/",
        TeamSeasonAutocomplete.as_view(),
        name="autocomplete-teamseasons",
    ),
    path(
        "autocomplete-personseasons/",
        PersonSeasonAutocomplete.as_view(),
        name="autocomplete-personseasons",
    ),
    path(
        "autocomplete-teambyseasons/",
        TeamBySeasonAutocomplete.as_view(),
        name="autocomplete-teamseasons",
    ),
    path(
        "autocomplete-personbyseasons/",
        PersonBySeasonAutocomplete.as_view(),
        name="autocomplete-personseasons",
    ),
    # --- Teams ---
    path("teams/", views.teams_view, name="teams"),
    re_path(r"^teams/(?P<pk>\d+)/$", TeamUpdateView.as_view(), name="teams_detail"),
    re_path(
        r"^teams/(?P<pk>\d+)/(?P<year>\d{4})/all/$",
        TeamAllYearView.as_view(),
        name="team_year_all",
    ),
    re_path(
        r"^teams/(?P<team_pk>\d+)/(?P<year>\d{4})/(?P<pk>\d+)/$",
        TeamSeasonView.as_view(),
        name="teamseason_detail",
    ),
    # --- Tournaments / Matches / Seasons ---
    path("tournaments/", TournamentListView.as_view(), name="tournaments"),
    re_path(
        r"^tournaments/(?P<pk>\d+)/$",
        TournamentDetailView.as_view(),
        name="tournament_detail",
    ),
    re_path(
        r"^tournaments/(?P<tourn_pk>\d+)/(?P<lap>[\d\-]{4,7})/(?P<season_pk>\d+)/matches/(?P<pk>\d+)/$",
        MatchDetailView.as_view(),
        name="match_detail",
    ),
    re_path(
        r"^tournaments/(?P<tourn_pk>\d+)/(?P<lap>[\d\-]{4,7})/(?P<pk>\d+)/$",
        SeasonDetailView.as_view(),
        name="season_detail",
    ),
    re_path(
        r"^seasons/(?P<year>\d{4})/$", SeasonYearView.as_view(), name="seasons_year"
    ),
    path("seasons/new/", SeasonCreateView.as_view(), name="seasons_new"),
    # --- Other Views ---
    path("persons/", views.persons_view, name="persons"),
    re_path(
        r"^persons/(?P<pk>\d+)/$", PersonUpdateView.as_view(), name="persons_detail"
    ),
    path("persons/new/", PersonCreateView.as_view(), name="persons_new"),
    path("clippings/", views.clippings_view, name="clippings"),
    path("contacts/", views.contacts_view, name="contacts"),
    # --- Redirects ---
    path("", RedirectView.as_view(url=reverse_lazy("tournaments"), permanent=False)),
    # optional API root redirect
    # path('', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
