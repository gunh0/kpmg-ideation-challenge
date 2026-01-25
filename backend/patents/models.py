from django.db import models


class Dataset(models.Model):
    """One Google Patents search result export, or one collected topic."""

    name = models.CharField(max_length=200)
    search_url = models.URLField(max_length=2000, blank=True)
    imported_at = models.DateTimeField(auto_now_add=True)
    # Collected topics (patents.topics) are known by their slug.
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    pattern = models.CharField(max_length=500, blank=True)
    source_revision = models.CharField(max_length=64, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-imported_at"]

    def __str__(self):
        return self.name


class Patent(models.Model):
    """A patent or application as listed in a Google Patents export."""

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="patents")
    patent_id = models.CharField(max_length=64)
    application_number = models.CharField(max_length=64, blank=True)
    family_id = models.CharField(max_length=32, blank=True)
    title = models.TextField()
    assignee = models.CharField(max_length=500, blank=True)
    inventors = models.TextField(blank=True)
    priority_date = models.DateField(null=True, blank=True)
    filing_date = models.DateField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    grant_date = models.DateField(null=True, blank=True)
    result_link = models.URLField(max_length=500, blank=True)
    figure_link = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ["-publication_date", "patent_id"]
        constraints = [
            models.UniqueConstraint(fields=["dataset", "patent_id"], name="unique_patent_per_dataset"),
        ]
        indexes = [
            # default ordering and the year filters
            models.Index(fields=["-publication_date", "patent_id"], name="patent_publication_idx"),
            models.Index(fields=["assignee"], name="patent_assignee_idx"),
        ]

    def __str__(self):
        return f"{self.patent_id} {self.title}"

    @property
    def is_granted(self):
        return self.grant_date is not None

    @property
    def inventor_list(self):
        return [name.strip() for name in self.inventors.split(",") if name.strip()]
