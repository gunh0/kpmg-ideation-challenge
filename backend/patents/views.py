from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import jobs
from .export import export_rows
from .figures import fill_figures
from .filters import NullsLastOrderingFilter, PatentFilter, PatentSearchFilter
from .matcher import match_stored
from .models import Patent, Topic
from .pagination import PatentPagination
from .serializers import (
    FigureSerializer,
    NameCountSerializer,
    PatentSerializer,
    ConfigSerializer,
    StatsSerializer,
    TopicInputSerializer,
    TopicSerializer,
)
from .store import delete_orphans
from .stats import summary


class TopicEdits(permissions.BasePermission):
    message = "Topics cannot be changed on this instance (PATENTS_ALLOW_TOPIC_EDITS is off)."

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or settings.PATENTS_ALLOW_TOPIC_EDITS


def unique_slug(name):
    base = slugify(name)[:90] or "topic"
    slug, n = base, 2
    while Topic.objects.filter(slug=slug).exists():
        slug, n = f"{base}-{n}", n + 1
    return slug


class TopicViewSet(viewsets.ModelViewSet):
    """The topics with their patent counts and collection state.

    POST {"name", "keywords", "description"} adds a topic: it is matched
    against the stored patents at once and queued for collection from the
    public data. PATCH edits one (new keywords are matched and collected
    again), DELETE removes it with the patents no other topic keeps, and
    POST /collect/ queues it again, e.g. after a failure.
    """

    queryset = Topic.objects.annotate(patent_count=Count("patents"))
    serializer_class = TopicSerializer
    permission_classes = [TopicEdits]
    # JSON only: a form on another site cannot post here without CORS consent.
    parser_classes = [JSONParser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def respond(self, topic, code=status.HTTP_200_OK):
        return Response(TopicSerializer(self.get_queryset().get(pk=topic.pk)).data, status=code)

    def collect(self, topic):
        jobs.enqueue([topic])
        transaction.on_commit(jobs.start_worker)

    @extend_schema(request=TopicInputSerializer, responses={201: TopicSerializer})
    def create(self, request):
        data = TopicInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        if Topic.objects.count() >= settings.PATENTS_MAX_TOPICS:
            return Response({"detail": f"There are {settings.PATENTS_MAX_TOPICS} topics already, the most allowed."},
                            status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            topic = Topic(name=data.validated_data["name"], slug=unique_slug(data.validated_data["name"]),
                          description=data.validated_data.get("description", ""))
            topic.set_keywords(data.validated_data["keywords"])
            topic.save()
            match_stored(topic)
            self.collect(topic)
        return self.respond(topic, status.HTTP_201_CREATED)

    @extend_schema(request=TopicInputSerializer, responses=TopicSerializer)
    def partial_update(self, request, pk=None):
        topic = self.get_object()
        data = TopicInputSerializer(topic, data=request.data, partial=True)
        data.is_valid(raise_exception=True)
        with transaction.atomic():
            for field in ("name", "description"):
                if field in data.validated_data:
                    setattr(topic, field, data.validated_data[field])
            keywords = data.validated_data.get("keywords")
            if keywords is not None and keywords != topic.keyword_list:
                topic.set_keywords(keywords)
                topic.save()
                match_stored(topic)
                self.collect(topic)
            else:
                topic.save()
        return self.respond(topic)

    def destroy(self, request, pk=None):
        with transaction.atomic():
            self.get_object().delete()
            delete_orphans()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses=TopicSerializer)
    @action(detail=True, methods=["post"], url_path="collect")
    def collect_again(self, request, pk=None):
        """Queue the topic for collection again."""
        topic = self.get_object()
        with transaction.atomic():
            self.collect(topic)
        return self.respond(topic)


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


class ConfigView(APIView):
    """What this instance allows, for the dashboard to adapt to."""

    @extend_schema(responses=ConfigSerializer)
    def get(self, request):
        return Response({"topic_edits": settings.PATENTS_ALLOW_TOPIC_EDITS, "max_topics": settings.PATENTS_MAX_TOPICS})
