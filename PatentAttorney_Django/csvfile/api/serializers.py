from rest_framework import serializers

from csvfile.models import PatentData

class PatentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatentData
        fields = (
            'id',
            'patent_id',
            'title',
            'assignee',
            'inventor_author',
            'priority_date',
            'filing_creation_date',
            'publication_date', 
            'grant_date', 
            'result_link', 
            'representative_figure_link', 
        )