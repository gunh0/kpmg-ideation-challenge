from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import NullsLastOrderingFilter, PatentFilter
from .models import Patent
from .pagination import PatentPagination
from .serializers import PatentSerializer


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.select_related("dataset")
    serializer_class = PatentSerializer
    pagination_class = PatentPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, NullsLastOrderingFilter]
    filterset_class = PatentFilter
    search_fields = ["patent_id", "title", "assignee", "inventors"]
    ordering_fields = ["publication_date", "priority_date", "filing_date", "grant_date", "patent_id", "title"]
    ordering = ["-publication_date", "patent_id"]
