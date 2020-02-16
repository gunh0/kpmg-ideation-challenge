from django.contrib import admin

# Register your models here.

from .models import PatentData

admin.site.register(PatentData)
