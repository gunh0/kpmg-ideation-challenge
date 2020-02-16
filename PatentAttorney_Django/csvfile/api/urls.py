from django.urls import path

from .views import PatentListView, PatentDetailView

urlpatterns = [
    path('',PatentListView.as_view()),
    path('<pk>',PatentDetailView.as_view())
]