import django_filters
from main.models import Game, MultiplayerGame


class GameFilter(django_filters.FilterSet):

    date = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "type": "date"}
        )
    )

    class Meta:
        model = Game
        fields = ["date"]

    def filter_by_date(self, queryset, name, value):
        return queryset.filter(date=value)


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
