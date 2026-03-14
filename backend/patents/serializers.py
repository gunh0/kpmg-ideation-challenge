from rest_framework import serializers

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

    class Meta:
        model = Topic
        fields = ("id", "slug", "name", "description", "pattern", "source_revision", "collected_at", "patent_count")


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


class StatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    granted = serializers.IntegerField()
    by_year = YearCountSerializer(many=True)
    top_assignees = AssigneeCountSerializer(many=True)
    top_inventors = NameCountSerializer(many=True)


class FigureSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    thumbnail = serializers.CharField(source="thumbnail_link")
    figure = serializers.CharField(source="figure_link")
    checked = serializers.SerializerMethodField()

    def get_checked(self, patent) -> bool:
        return patent.figure_checked_at is not None
