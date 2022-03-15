from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .csv_import import CSVFormatError
from .filters import NullsLastOrderingFilter, PatentFilter
from .importer import import_export
from .models import Dataset, Patent
from .pagination import PatentPagination
from .serializers import DatasetSerializer, DatasetUploadSerializer, PatentSerializer
from .stats import summary


class DatasetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Imported Google Patents exports. POST a CSV file to import a new one."""

    queryset = Dataset.objects.annotate(patent_count=Count("patents"))
    serializer_class = DatasetSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request):
        upload = DatasetUploadSerializer(data=request.data)
        upload.is_valid(raise_exception=True)
        try:
            result = import_export(upload.validated_data["file"], name=upload.validated_data.get("name", ""))
        except CSVFormatError as exc:
            return Response({"file": [f"Not a Google Patents export: {exc}."]}, status=status.HTTP_400_BAD_REQUEST)

        dataset = self.get_queryset().get(pk=result.dataset.pk)
        body = DatasetSerializer(dataset).data
        body["import"] = {"imported": result.imported, "duplicates": result.duplicates, "skipped": result.skipped}
        return Response(body, status=status.HTTP_201_CREATED)


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.select_related("dataset")
    serializer_class = PatentSerializer
    pagination_class = PatentPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, NullsLastOrderingFilter]
    filterset_class = PatentFilter
    search_fields = ["patent_id", "title", "assignee", "inventors"]
    ordering_fields = ["publication_date", "priority_date", "filing_date", "grant_date", "patent_id", "title"]
    ordering = ["-publication_date", "patent_id"]


class StatsView(APIView):
    """Dashboard aggregates. Accepts the same filters and search as /api/patents/,
    plus ?top=N (1-50, default 10) for the length of the ranking lists."""

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PatentFilter
    search_fields = PatentViewSet.search_fields

    def get(self, request):
        queryset = Patent.objects.all()
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)
        try:
            limit = min(max(int(request.query_params.get("top", 10)), 1), 50)
        except ValueError:
            limit = 10
        return Response(summary(queryset, limit=limit))
