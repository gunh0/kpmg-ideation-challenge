from django.contrib import admin

from .models import Dataset, Patent


class PatentInline(admin.TabularInline):
    model = Patent
    fields = ("patent_id", "title", "assignee", "publication_date", "grant_date")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "imported_at", "patent_count")
    search_fields = ("name", "search_url")
    inlines = [PatentInline]

    @admin.display(description="patents")
    def patent_count(self, obj):
        return obj.patents.count()


@admin.register(Patent)
class PatentAdmin(admin.ModelAdmin):
    list_display = ("patent_id", "title", "assignee", "publication_date", "grant_date", "dataset")
    list_filter = ("dataset",)
    search_fields = ("patent_id", "title", "assignee", "inventors")
    date_hierarchy = "publication_date"
