from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import PatentFilter
from .models import Patent
from .serializers import PatentSerializer


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.select_related("dataset")
    serializer_class = PatentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PatentFilter
    search_fields = ["patent_id", "title", "assignee", "inventors"]
