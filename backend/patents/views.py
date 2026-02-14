from django.db.models import Count
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .export import export_rows
from .figures import fill_figures
from .filters import NullsLastOrderingFilter, PatentFilter, PatentSearchFilter
from .models import Dataset, Patent
from .pagination import PatentPagination
from .serializers import (
    DatasetSerializer,
    FigureSerializer,
    NameCountSerializer,
    PatentSerializer,
    StatsSerializer,
)
from .stats import summary


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """The collected topics (patents.topics) with their patent counts and the
    revision of the public data they come from."""

    queryset = Dataset.objects.annotate(patent_count=Count("patents"))
    serializer_class = DatasetSerializer


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.select_related("dataset")
    serializer_class = PatentSerializer
    pagination_class = PatentPagination
    filter_backends = [DjangoFilterBackend, PatentSearchFilter, NullsLastOrderingFilter]
    filterset_class = PatentFilter
    search_fields = ["patent_id", "title", "assignee", "inventors"]
    ordering_fields = ["publication_date", "priority_date", "filing_date", "grant_date", "patent_id", "title"]
    ordering = ["-publication_date", "patent_id"]

    @action(detail=False, url_path="export")
    def export(self, request):
        """The filtered, ordered list as CSV (Google Patents columns, no pagination)."""
        queryset = self.filter_queryset(self.get_queryset())
        response = StreamingHttpResponse(export_rows(queryset), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{self.export_name()}"'
        return response


    def export_name(self):
        """patents-drone-delivery-2025-12-19.csv: the dataset and the day, so
        downloads of different selections do not overwrite each other."""
        parts = ["patents"]
        dataset = Dataset.objects.filter(pk=self.request.query_params.get("dataset") or None).first()
        if dataset:
            parts.append(slugify(dataset.name) or f"dataset-{dataset.pk}")
        parts.append(timezone.localdate().isoformat())
        return "-".join(parts) + ".csv"


class StatsView(generics.GenericAPIView):
    """Dashboard aggregates. Accepts the same filters and search as /api/patents/,
    plus ?top=N (1-50, default 10) for the length of the ranking lists."""

    queryset = Patent.objects.all()
    serializer_class = StatsSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, PatentSearchFilter]
    filterset_class = PatentFilter
    search_fields = PatentViewSet.search_fields

    @extend_schema(
        responses=StatsSerializer,
        filters=True,  # a single object, but filtered like a list
        parameters=[OpenApiParameter("top", int, description="length of the ranking lists, 1-50 (default 10)")],
    )
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            limit = min(max(int(request.query_params.get("top", 10)), 1), 50)
        except ValueError:
            limit = 10
        return Response(summary(queryset, limit=limit))


class AssigneeView(APIView):
    """Assignee names with their patent counts, for filter suggestions.

    ?dataset=<id> limits to one dataset, ?search= matches part of the name.
    """

    @extend_schema(
        responses=NameCountSerializer(many=True),
        parameters=[OpenApiParameter("dataset", int), OpenApiParameter("search", str)],
    )
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


class FigureView(APIView):
    """Representative figures of up to 50 patents, ?ids=1,2,3.

    Figures that were never looked up are fetched from Google Patents first
    (at most FETCH_LIMIT per request, the rest come back unchecked and can be
    asked for again)."""

    MAX_IDS = 50
    FETCH_LIMIT = 25

    @extend_schema(
        responses=FigureSerializer(many=True),
        parameters=[OpenApiParameter("ids", str, description="comma-separated patent ids", required=True)],
    )
    def get(self, request):
        ids = [int(part) for part in request.query_params.get("ids", "").split(",") if part.strip().isdigit()]
        if not ids:
            return Response({"ids": ["Give one or more patent ids, e.g. ?ids=1,2,3."]}, status=status.HTTP_400_BAD_REQUEST)
        patents = list(Patent.objects.filter(pk__in=ids[: self.MAX_IDS]))
        unchecked = [patent for patent in patents if patent.figure_checked_at is None]
        fill_figures(unchecked[: self.FETCH_LIMIT])
        order = {pk: i for i, pk in enumerate(ids)}
        patents.sort(key=lambda patent: order[patent.pk])
        return Response(FigureSerializer(patents, many=True).data)
