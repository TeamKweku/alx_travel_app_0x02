from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ListingViewSet, BookingViewSet, ReviewViewSet,
    PaymentViewSet, PaymentCompleteView
)

router = DefaultRouter()
router.register(r"listings", ListingViewSet)
router.register(r"bookings", BookingViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('chapa-webhook/', include('django_chapa.urls')),
    path('payments/<uuid:payment_id>/complete/', 
         PaymentCompleteView.as_view(), name='payment-complete'),
]
