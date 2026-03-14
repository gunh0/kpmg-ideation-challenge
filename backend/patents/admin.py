from django.contrib import admin

from .models import Patent, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "collected_at", "source_revision", "patent_count")
    search_fields = ("name", "slug")

    @admin.display(description="patents")
    def patent_count(self, obj):
        return obj.patents.count()


@admin.register(Patent)
class PatentAdmin(admin.ModelAdmin):
    list_display = ("patent_id", "title", "assignee", "assignee_country", "publication_date", "grant_date", "cited_by")
    list_filter = ("topics", "assignee_country")
    search_fields = ("patent_id", "title", "assignee", "inventors")
    filter_horizontal = ("topics",)
    date_hierarchy = "publication_date"
