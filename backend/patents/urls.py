from rest_framework.routers import DefaultRouter

from .views import DatasetViewSet, PatentViewSet

router = DefaultRouter()
router.register("datasets", DatasetViewSet)
router.register("patents", PatentViewSet)

urlpatterns = router.urls
