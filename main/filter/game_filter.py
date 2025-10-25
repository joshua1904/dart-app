import django_filters
from django import forms

from main.models import Game, MultiplayerGame


class GameFilter(django_filters.FilterSet):
    def __init__(
        self, *args, round_choices: set[int], score_choices: set[int], **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.filters["rounds"].extra["choices"] = [
            (r, r) for r in sorted(round_choices)
        ]
        self.filters["score"].extra["choices"] = [(s, s) for s in sorted(score_choices)]

    date = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "type": "date"}
        )
    )
    rounds = django_filters.ChoiceFilter(
        choices=[],  # override by init
        method="filter_by_rounds",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    score = django_filters.ChoiceFilter(
        choices=[],  # override by init
        method="filter_by_score",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Game
        fields = ["rounds", "score", "date"]

    def filter_by_date(self, queryset, name, value):
        return queryset.filter(date=value)

    def filter_by_rounds(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(rounds=int(value))

    def filter_by_score(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(score=int(value))


class MultiplayerGameFilter(django_filters.FilterSet):

    date = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "type": "date"}
        )
    )

    class Meta:
        model = MultiplayerGame
        fields = ["date"]

    def filter_by_date(self, queryset, name, value):
        return queryset.filter(date=value)
