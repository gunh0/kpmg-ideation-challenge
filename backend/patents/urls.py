from rest_framework.routers import DefaultRouter

from .views import PatentViewSet

router = DefaultRouter()
router.register("patents", PatentViewSet)

urlpatterns = router.urls
