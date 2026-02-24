import django_filters
from django.db.models import F, Value
from django.db.models.functions import Replace
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Patent


class PatentFilter(django_filters.FilterSet):
    assignee = django_filters.CharFilter(field_name="assignee", lookup_expr="iexact")
    inventor = django_filters.CharFilter(method="filter_inventor")
    granted = django_filters.BooleanFilter(field_name="grant_date", lookup_expr="isnull", exclude=True)
    year_from = django_filters.NumberFilter(field_name="publication_date", lookup_expr="year__gte")
    year_to = django_filters.NumberFilter(field_name="publication_date", lookup_expr="year__lte")
    has_figure = django_filters.BooleanFilter(field_name="thumbnail_link", lookup_expr="exact", exclude=True,
                                              method="filter_has_figure")

    class Meta:
        model = Patent
        fields = ["dataset", "assignee", "inventor", "granted", "year_from", "year_to", "has_figure"]

    def filter_has_figure(self, queryset, name, value):
        """Patents whose representative figure is known (true) or not (false)."""
        return queryset.exclude(thumbnail_link="") if value else queryset.filter(thumbnail_link="")

    def filter_inventor(self, queryset, name, value):
        """Whole names within the comma-separated inventor list, case-insensitive."""
        value = value.strip()
        if not value:
            return queryset
        target = value.casefold()
        candidates = queryset.filter(inventors__icontains=value).values_list("pk", "inventors")
        ids = [
            pk
            for pk, inventors in candidates
            if target in (name.strip().casefold() for name in inventors.split(","))
        ]
        return queryset.filter(pk__in=ids)


class NullsLastOrderingFilter(OrderingFilter):
    """Ordering that keeps patents without the sorted date at the end,
    whichever direction is requested."""

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if not ordering:
            return queryset
        expressions = []
        for field in ordering:
            if field.startswith("-"):
                expressions.append(F(field[1:]).desc(nulls_last=True))
            else:
                expressions.append(F(field).asc(nulls_last=True))
        return queryset.order_by(*expressions)


class PatentSearchFilter(SearchFilter):
    """Search that also finds patent numbers written without dashes, as they
    appear in Google Patents URLs (US10000000B2 for US-10000000-B2)."""

    def filter_queryset(self, request, queryset, view):
        matches = super().filter_queryset(request, queryset, view)
        terms = self.get_search_terms(request)
        if len(terms) != 1:
            return matches
        compact = terms[0].replace("-", "")
        by_number = queryset.annotate(compact_id=Replace(F("patent_id"), Value("-"), Value(""))).filter(
            compact_id__iexact=compact
        )
        return matches | queryset.filter(pk__in=by_number.values("pk"))
