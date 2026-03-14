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
from .models import Patent, Topic
from .pagination import PatentPagination
from .serializers import (
    FigureSerializer,
    NameCountSerializer,
    PatentSerializer,
    StatsSerializer,
    TopicSerializer,
)
from .stats import summary


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """The topics with their patent counts and the revision of the public data
    they were collected from."""

    queryset = Topic.objects.annotate(patent_count=Count("patents"))
    serializer_class = TopicSerializer


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.prefetch_related("topics")
    serializer_class = PatentSerializer
    pagination_class = PatentPagination
    # Search first: it combines querysets, which the topic filter's grouping
    # does not survive.
    filter_backends = [PatentSearchFilter, DjangoFilterBackend, NullsLastOrderingFilter]
    filterset_class = PatentFilter
    search_fields = ["patent_id", "title", "abstract", "assignee", "inventors"]
    ordering_fields = [
        "matched", "publication_date", "priority_date", "filing_date", "grant_date", "patent_id", "title", "cited_by",
    ]
    ordering = ["-publication_date", "patent_id"]

    @action(detail=False, url_path="export")
    def export(self, request):
        """The filtered, ordered list as CSV (Google Patents columns, no pagination)."""
        queryset = self.filter_queryset(self.get_queryset())
        response = StreamingHttpResponse(export_rows(queryset), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{self.export_name()}"'
        return response


    def export_name(self):
        """patents-drones-cybersecurity-2026-03-14.csv: the topics and the day,
        so downloads of different selections do not overwrite each other."""
        parts = ["patents"]
        ids = self.request.query_params.get("topics") or self.request.query_params.get("dataset") or ""
        ids = [int(item) for item in ids.split(",") if item.strip().isdigit()]
        for topic in Topic.objects.filter(pk__in=ids).order_by("name"):
            parts.append(slugify(topic.name) or f"topic-{topic.pk}")
        parts.append(timezone.localdate().isoformat())
        return "-".join(parts) + ".csv"


class StatsView(generics.GenericAPIView):
    """Dashboard aggregates. Accepts the same filters and search as /api/patents/,
    plus ?top=N (1-50, default 10) for the length of the ranking lists."""

    queryset = Patent.objects.all()
    serializer_class = StatsSerializer
    pagination_class = None
    filter_backends = [PatentSearchFilter, DjangoFilterBackend]
    filterset_class = PatentFilter
    search_fields = PatentViewSet.search_fields

    @extend_schema(
        responses=StatsSerializer,
        filters=True,  # a single object, but filtered like a list
        parameters=[OpenApiParameter("top", int, description="length of the ranking lists, 1-50 (default 10)")],
    )
    def get(self, request):
        # The aggregates group by other columns than the topic filter does;
        # select the filtered patents by key instead of stacking the groupings.
        queryset = Patent.objects.filter(pk__in=self.filter_queryset(self.get_queryset()).values("pk"))
        try:
            limit = min(max(int(request.query_params.get("top", 10)), 1), 50)
        except ValueError:
            limit = 10
        return Response(summary(queryset, limit=limit))


class AssigneeView(APIView):
    """Assignee names with their patent counts, for filter suggestions.

    ?topics=1,2 limits to patents of these topics, ?search= matches part of the name.
    """

    @extend_schema(
        responses=NameCountSerializer(many=True),
        parameters=[OpenApiParameter("topics", str), OpenApiParameter("search", str)],
    )
    def get(self, request):
        queryset = Patent.objects.exclude(assignee="")
        ids = request.query_params.get("topics") or request.query_params.get("dataset") or ""
        ids = [int(item) for item in ids.split(",") if item.strip().isdigit()]
        if ids:
            queryset = queryset.filter(pk__in=Patent.objects.filter(topics__in=ids).values("pk"))
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
