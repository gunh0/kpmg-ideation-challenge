from rest_framework import serializers

from .models import Dataset, Patent


class PatentSerializer(serializers.ModelSerializer):
    inventors = serializers.ListField(source="inventor_list", child=serializers.CharField(), read_only=True)
    is_granted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Patent
        fields = (
            "id",
            "dataset",
            "patent_id",
            "title",
            "assignee",
            "inventors",
            "priority_date",
            "filing_date",
            "publication_date",
            "grant_date",
            "is_granted",
            "result_link",
            "figure_link",
            "thumbnail_link",
        )


class DatasetSerializer(serializers.ModelSerializer):
    patent_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = ("id", "name", "search_url", "imported_at", "patent_count")
        read_only_fields = ("search_url", "imported_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("The name cannot be empty.")
        return value


class DatasetUploadSerializer(serializers.Serializer):
    MAX_SIZE = 10 * 1024 * 1024

    file = serializers.FileField()
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_file(self, upload):
        if upload.size > self.MAX_SIZE:
            raise serializers.ValidationError("The file is larger than 10 MB.")
        try:
            return upload.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            raise serializers.ValidationError("The file is not UTF-8 text.")


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


class ConfigSerializer(serializers.Serializer):
    read_only = serializers.BooleanField()


class FigureSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    thumbnail = serializers.CharField(source="thumbnail_link")
    figure = serializers.CharField(source="figure_link")
    checked = serializers.SerializerMethodField()

    def get_checked(self, patent) -> bool:
        return patent.figure_checked_at is not None
