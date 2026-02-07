from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import DefaultRouter

from .health import health
from .views import AssigneeView, ConfigView, DatasetViewSet, FigureView, PatentViewSet, StatsView

router = DefaultRouter()
router.register("datasets", DatasetViewSet)
router.register("patents", PatentViewSet)

urlpatterns = router.urls + [
    path("stats/", StatsView.as_view(), name="stats"),
    path("assignees/", AssigneeView.as_view(), name="assignees"),
    path("figures/", FigureView.as_view(), name="figures"),
    path("health/", health, name="health"),
    path("config/", ConfigView.as_view(), name="config"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
