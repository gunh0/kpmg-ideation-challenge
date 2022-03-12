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
        )


class DatasetSerializer(serializers.ModelSerializer):
    patent_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = ("id", "name", "search_url", "imported_at", "patent_count")
        read_only_fields = ("search_url", "imported_at")


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
