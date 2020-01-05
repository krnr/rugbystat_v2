from dal import autocomplete
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import (CreateView, ListView, DetailView,
                                  YearArchiveView)

from .forms import ImportForm, SeasonForm, MatchForm
from .models import Tournament, Season, Match


class TournamentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Season.objects.none()

        qs = Tournament.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class SeasonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # if not self.request.user.is_authenticated():
        #     return Season.objects.none()

        qs = Season.objects.all()

        year = self.forwarded.get('year', None)
        if year:
            qs = qs.filter(Q(date_end__year=year) |
                           Q(date_start__year=year))

        if self.q:
            for search_term in self.q.split(' '):
                qs = qs.filter(name__icontains=search_term)

        return qs


def import_seasons(request):
    obj_form = SeasonForm()
    status = None

    if request.method == 'POST':
        form = ImportForm(request.POST, request=request)

        if form.is_valid():
            status = 'OK'
            obj_form = SeasonForm(instance=form.season)
        else:
            status = 'False'
    else:
        form = ImportForm()
    return render(request,
                  'import.html',
                  {
                      'form': form,
                      'status': status,
                      'obj_form': obj_form
                  })


class SeasonCreateView(CreateView):
    model = Season
    form_class = SeasonForm
    success_url = reverse_lazy('import_seasons')


class SeasonYearView(YearArchiveView):
    model = Season
    date_field = 'date_end'
    ordering = ('tourn', 'date_start')
    make_object_list = True


class TournamentListView(ListView):
    """Base list of all Tournaments"""
    model = Tournament

    def get_context_data(self, **kwargs):
        ctx = super(TournamentListView, self).get_context_data(**kwargs)
        ctx['ends'] = Season.objects.dates('date_end', 'year')
        return ctx


class TournamentDetailView(DetailView):
    """List of all Tournament Seasons"""
    model = Tournament


class SeasonDetailView(DetailView):
    """Detail of one tournament Season"""
    model = Season

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['match_form'] = MatchForm(initial={'tourn_season': ctx['object']})

        qs = Season.objects.filter(tourn=self.object.tourn)
        ctx['prev'] = qs.filter(date_end__lt=self.object.date_end).last()
        ctx['next'] = qs.filter(date_end__gt=self.object.date_end).first()
        return ctx


class MatchDetailView(DetailView):
    """Details of one Match"""
    model = Match
