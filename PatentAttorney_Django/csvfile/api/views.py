from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView

from csvfile.models import PatentData
from .serializers import PatentSerializer

class PatentListView(ListAPIView):
    queryset = PatentData.objects.all()
    serializer_class = PatentSerializer

class PatentDetailView(RetrieveAPIView):
    queryset = PatentData.objects.all()
    serializer_class = PatentSerializer