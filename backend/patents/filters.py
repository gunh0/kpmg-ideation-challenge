import django_filters
from django.db.models import F
from rest_framework.filters import OrderingFilter

from .models import Patent


class PatentFilter(django_filters.FilterSet):
    assignee = django_filters.CharFilter(field_name="assignee", lookup_expr="iexact")
    granted = django_filters.BooleanFilter(field_name="grant_date", lookup_expr="isnull", exclude=True)
    year_from = django_filters.NumberFilter(field_name="publication_date", lookup_expr="year__gte")
    year_to = django_filters.NumberFilter(field_name="publication_date", lookup_expr="year__lte")

    class Meta:
        model = Patent
        fields = ["dataset", "assignee", "granted", "year_from", "year_to"]


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
