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
