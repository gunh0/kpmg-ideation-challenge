from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import DefaultRouter

from .health import health
from .views import AssigneeView, ConfigView, FigureView, PatentViewSet, StatsView, TopicViewSet

router = DefaultRouter()
router.register("topics", TopicViewSet)
# the name of 2.0, until the dashboard has moved to /api/topics/
router.register("datasets", TopicViewSet, basename="dataset")
router.register("patents", PatentViewSet)

urlpatterns = router.urls + [
    path("stats/", StatsView.as_view(), name="stats"),
    path("assignees/", AssigneeView.as_view(), name="assignees"),
    path("figures/", FigureView.as_view(), name="figures"),
    path("config/", ConfigView.as_view(), name="config"),
    path("health/", health, name="health"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
