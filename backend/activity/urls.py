from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet, SubActivityViewSet

router = DefaultRouter()
router.register(r'activities', ActivityViewSet)
router.register(r'subactivities', SubActivityViewSet)

urlpatterns = router.urls