from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ListingViewSet, BookingViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"listings", ListingViewSet)
router.register(r"bookings", BookingViewSet)
router.register(r"reviews", ReviewViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
