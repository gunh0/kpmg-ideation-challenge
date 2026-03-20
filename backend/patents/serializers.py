from rest_framework import serializers

from .keywords import parse_keywords
from .models import Patent, Topic


class PatentSerializer(serializers.ModelSerializer):
    inventors = serializers.ListField(source="inventor_list", child=serializers.CharField(), read_only=True)
    is_granted = serializers.BooleanField(read_only=True)
    topics = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    matched = serializers.SerializerMethodField()

    def get_matched(self, patent) -> int | None:
        """How many of the selected topics the patent matches (with ?topics=)."""
        return getattr(patent, "matched", None)

    class Meta:
        model = Patent
        fields = (
            "id",
            "topics",
            "matched",
            "patent_id",
            "title",
            "abstract",
            "assignee",
            "assignee_country",
            "inventors",
            "priority_date",
            "filing_date",
            "publication_date",
            "grant_date",
            "is_granted",
            "result_link",
            "figure_link",
            "thumbnail_link",
            "cited_by",
        )


class TopicSerializer(serializers.ModelSerializer):
    patent_count = serializers.IntegerField(read_only=True)
    keywords = serializers.ListField(source="keyword_list", child=serializers.CharField(), read_only=True)

    class Meta:
        model = Topic
        fields = (
            "id", "slug", "name", "description", "keywords", "pattern", "source_revision", "collected_at",
            "patent_count", "status", "progress", "progress_total", "error",
        )


class TopicInputSerializer(serializers.Serializer):
    """What the dashboard sends to add or edit a topic."""

    name = serializers.CharField(min_length=2, max_length=80)
    description = serializers.CharField(max_length=300, required=False, allow_blank=True)
    keywords = serializers.JSONField(help_text="a list of keywords, or one string separated by commas")

    def validate_name(self, value):
        value = " ".join(value.split())
        others = Topic.objects.filter(name__iexact=value)
        if self.instance is not None:
            others = others.exclude(pk=self.instance.pk)
        if others.exists():
            raise serializers.ValidationError("A topic with this name exists already.")
        return value

    def validate_keywords(self, value):
        if not isinstance(value, (str, list)):
            raise serializers.ValidationError("Give a list of keywords or a comma-separated string.")
        try:
            return parse_keywords(value)
        except ValueError as error:
            raise serializers.ValidationError(str(error))


# Shapes of the non-model responses, for the OpenAPI schema.


class YearCountSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    filed = serializers.IntegerField()
    published = serializers.IntegerField()
    granted = serializers.IntegerField()


class NameCountSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()


class AssigneeCountSerializer(NameCountSerializer):
    granted = serializers.IntegerField()


class CountryCountSerializer(serializers.Serializer):
    code = serializers.CharField()
    count = serializers.IntegerField()
    granted = serializers.IntegerField()


class TopicYearSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    published = serializers.IntegerField()


class TopicTrendSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    count = serializers.IntegerField()
    by_year = TopicYearSerializer(many=True)


class StatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    granted = serializers.IntegerField()
    by_year = YearCountSerializer(many=True)
    top_assignees = AssigneeCountSerializer(many=True)
    top_inventors = NameCountSerializer(many=True)
    top_countries = CountryCountSerializer(many=True)
    by_topic = TopicTrendSerializer(many=True)


class FigureSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    thumbnail = serializers.CharField(source="thumbnail_link")
    figure = serializers.CharField(source="figure_link")
    checked = serializers.SerializerMethodField()

    def get_checked(self, patent) -> bool:
        return patent.figure_checked_at is not None
