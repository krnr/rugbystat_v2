from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from main.filters import DropdownFilter
from matches.models import Group
from .forms import PersonSeasonForm
from .models import (
    Person, PersonSeason, Team, TeamName, TeamSeason, GroupSeason,
    Stadium, City, TagObject,
)


@admin.register(TagObject)
class TagAdmin(admin.ModelAdmin):
    list_select_related = ('team', 'tournament', 'season', 'match', 'person',)
    search_fields = ('name', )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', )


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', )
    list_select_related = ('city', )
    list_filter = (
        ('city__name', DropdownFilter),
    )


class TeamNameInline(admin.TabularInline):
    model = TeamName
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'city', )
    list_select_related = ('city', )
    list_filter = (
        ('city__name', DropdownFilter),
        ('year', DropdownFilter),
    )
    search_fields = ('short_name', )
    inlines = (
        TeamNameInline,
    )


@admin.register(TeamName)
class TeamNameAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'team')
    list_select_related = ('team', )
    search_fields = ('__str__', )


@admin.register(TeamSeason)
class TeamSeasonAdmin(admin.ModelAdmin):
    # form = TeamSeasonForm

    search_fields = ('team__name', )
    list_display = ('__str__', 'season', 'team')
    list_select_related = ('season', 'team')
    list_filter = (
        ('team__name', DropdownFilter),
        ('year', DropdownFilter),
        ('season__name', DropdownFilter),
    )
    raw_id_fields = ('team', 'season')
    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'year', 'display_name')
            }
        ),
        (
            None,
            {
                'fields': ('team', 'season', 'has_position', 'show_group')
            }
        ),
        (
            None,
            {
                'fields': (
                    'place', 'played', 'wins', 'draws', 'losses', 'points', 'score'
                )
            }
        ),
        (
            None,
            {
                'fields': ('story',)
            }
        ),
    )


@admin.register(GroupSeason)
class GroupSeasonAdmin(admin.ModelAdmin):
    search_fields = ('team__name', )
    list_display = ('__str__', 'group', 'team')
    list_select_related = ('group', 'team')
    list_filter = (
        ('team__name', DropdownFilter),
        ('year', DropdownFilter),
        ('group__name', DropdownFilter),
    )
    raw_id_fields = ('team', 'group')
    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'year', )
            }
        ),
        (
            None,
            {
                'fields': ('team', 'group', )
            }
        ),
        (
            None,
            {
                'fields': ('place', 'played', 'wins', 'draws', 'losses', 'points',
                           'score')
            }
        ),
        (
            None,
            {
                'fields': ('story',)
            }
        ),
    )


class GroupSeasonInline(SortableInlineAdminMixin, admin.TabularInline):
    model = GroupSeason
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
       field = super().formfield_for_foreignkey(db_field, request, **kwargs)

       pk = request.resolver_match.kwargs.get( 'object_id' )
       if db_field.name == 'team' and pk:
           # get only teams from THAT season
           group = Group.objects.get(pk=pk)
           teams_in_season = group.teams.values_list('team_id', flat=True)
           field.queryset = Team.objects.filter(pk__in=teams_in_season)
       return field


class PersonSeasonInline(admin.TabularInline):
    model = PersonSeason
    form = PersonSeasonForm
    extra = 1


@admin.register(Person)
class PersonAdmin(MarkdownxModelAdmin):
    search_fields = ('name', 'first_name', )
    list_editable = ('year_birth', 'year_death', 'is_dead')
    list_display = ('__str__', 'dob', 'dod', ) + list_editable
    list_filter = (
        ('year_birth', DropdownFilter),
        'is_dead',
    )
    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'first_name', 'middle_name', )
            }
        ),
        (
            None,
            {
                'fields': ('story',)
            }
        ),
        (
            None,
            {
                'fields': (('year_birth', 'dob',),
                           ('year_death', 'dod',), 'is_dead')
            }
        ),
    )
    inlines = [
        PersonSeasonInline,
    ]
    admin_integration_enabled = False


@admin.register(PersonSeason)
class PersonSeasonAdmin(admin.ModelAdmin):
    search_fields = ('person__name', 'person__first_name', )
    list_display = ('__str__', 'role', 'team', 'season')
    list_select_related = ('person', 'team', 'season')
    list_filter = (
        ('year', DropdownFilter),
        ('person__name', DropdownFilter),
        ('team__name', DropdownFilter),
        ('season__name', DropdownFilter),
    )
    raw_id_fields = ('person', )
    form = PersonSeasonForm

