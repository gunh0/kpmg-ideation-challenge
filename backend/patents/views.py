from django.conf import settings
from django.db.models import Count
from django.http import StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .csv_import import CSVFormatError
from .export import export_rows
from .filters import NullsLastOrderingFilter, PatentFilter
from .importer import import_export
from .models import Dataset, Patent
from .pagination import PatentPagination
from .serializers import DatasetSerializer, DatasetUploadSerializer, PatentSerializer
from .stats import summary


class ReadOnlyInstance(permissions.BasePermission):
    message = "This instance is read-only: uploads and deletions are disabled."

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or not settings.PATENTS_READ_ONLY


class DatasetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Imported Google Patents exports. POST a CSV file to import a new one,
    PATCH {"name": ...} to rename one."""

    queryset = Dataset.objects.annotate(patent_count=Count("patents"))
    serializer_class = DatasetSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [ReadOnlyInstance]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

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

    @action(detail=False, url_path="export")
    def export(self, request):
        """The filtered, ordered list as CSV (Google Patents columns, no pagination)."""
        queryset = self.filter_queryset(self.get_queryset())
        response = StreamingHttpResponse(export_rows(queryset), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="patents.csv"'
        return response


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


class AssigneeView(APIView):
    """Assignee names with their patent counts, for filter suggestions.

    ?dataset=<id> limits to one dataset, ?search= matches part of the name.
    """

    def get(self, request):
        queryset = Patent.objects.exclude(assignee="")
        dataset = request.query_params.get("dataset")
        if dataset and dataset.isdigit():
            queryset = queryset.filter(dataset_id=dataset)
        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(assignee__icontains=search)
        rows = queryset.values("assignee").annotate(count=Count("id")).order_by("-count", "assignee")[:20]
        return Response([{"name": row["assignee"], "count": row["count"]} for row in rows])


class ConfigView(APIView):
    """Instance settings the dashboard adapts to."""

    def get(self, request):
        return Response({"read_only": settings.PATENTS_READ_ONLY})
