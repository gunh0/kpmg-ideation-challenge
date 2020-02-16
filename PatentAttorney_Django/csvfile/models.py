from django.db import models

# Create your models here.

class PatentData(models.Model):
    patent_id = models.CharField(max_length=150,unique=True)
    title = models.TextField()
    assignee = models.TextField()
    inventor_author = models.TextField()
    priority_date = models.TextField()
    filing_creation_date = models.TextField()
    publication_date = models.TextField()
    grant_date = models.TextField()
    result_link = models.TextField()
    representative_figure_link = models.TextField()

    def __str__(self):
        return self.patent_id