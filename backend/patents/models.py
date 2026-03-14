from django.db import models


class Topic(models.Model):
    """A technology field: the patents whose title or abstract match its keywords."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    pattern = models.CharField(max_length=500, blank=True)
    source_revision = models.CharField(max_length=64, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Patent(models.Model):
    """A patent application, known by its grant number once it is granted."""

    # A patent is stored once and belongs to every topic it matches.
    topics = models.ManyToManyField(Topic, related_name="patents")
    patent_id = models.CharField(max_length=64)
    application_number = models.CharField(max_length=64, blank=True)
    family_id = models.CharField(max_length=32, blank=True)
    title = models.TextField()
    abstract = models.TextField(blank=True)
    assignee = models.CharField(max_length=500, blank=True)
    # ISO country of the first assignee, as harmonised by Google (US, CN, KR, ...)
    assignee_country = models.CharField(max_length=2, blank=True)
    inventors = models.TextField(blank=True)
    priority_date = models.DateField(null=True, blank=True)
    filing_date = models.DateField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    grant_date = models.DateField(null=True, blank=True)
    result_link = models.URLField(max_length=500, blank=True)
    figure_link = models.URLField(max_length=500, blank=True)
    thumbnail_link = models.URLField(max_length=500, blank=True)
    # All publications of the application (its A1 and B2 ...), comma-separated;
    # citations name publications, so counting them needs every number.
    publication_numbers = models.TextField(blank=True)
    # How many publications cite this patent (any of its publication numbers).
    cited_by = models.PositiveIntegerField(default=0)
    # When the figure was looked up on Google Patents; set even if none was found.
    figure_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-publication_date", "patent_id"]
        constraints = [
            models.UniqueConstraint(fields=["patent_id"], name="unique_patent_id"),
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
