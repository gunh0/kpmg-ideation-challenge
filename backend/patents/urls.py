from django.urls import path
from rest_framework.routers import DefaultRouter

from .health import health
from .views import DatasetViewSet, PatentViewSet, StatsView

router = DefaultRouter()
router.register("datasets", DatasetViewSet)
router.register("patents", PatentViewSet)

urlpatterns = router.urls + [
    path("stats/", StatsView.as_view(), name="stats"),
    path("health/", health, name="health"),
]
