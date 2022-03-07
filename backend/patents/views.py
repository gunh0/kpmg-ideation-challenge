from rest_framework import viewsets

from .models import Patent
from .serializers import PatentSerializer


class PatentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patent.objects.select_related("dataset")
    serializer_class = PatentSerializer
