from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.urls import reverse
from django.conf import settings
from django_chapa import api as chapa_api
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email, send_payment_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing property listings.
    """

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @swagger_auto_schema(
        operation_description="List all property listings",
        responses={200: ListingSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new property listing",
        request_body=ListingSerializer,
        responses={201: ListingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing bookings.
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Send booking confirmation email asynchronously
        send_booking_confirmation_email.delay(
            booking_id=booking.id,
            user_email=booking.user.email,
            listing_title=booking.listing.title
        )

    @swagger_auto_schema(
        operation_description="List all bookings for the authenticated user",
        responses={200: BookingSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new booking",
        request_body=BookingSerializer,
        responses={201: BookingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing reviews.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter payments based on user role"""
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__user=user)

    @action(detail=True, methods=['post'])
    def initialize(self, request, pk=None):
        """Initialize payment for a booking"""
        payment = self.get_object()
        booking = payment.booking
        user = booking.user

        callback_url = request.build_absolute_uri('/api/chapa-webhook/')
        return_url = request.build_absolute_uri(
            reverse('payment-complete', args=[payment.payment_id])
        )

        try:
            # Initialize payment using django-chapa
            response = chapa_api.initialize_payment(
                amount=str(payment.amount),
                email=user.email,
                first_name=user.first_name or 'Guest',
                last_name=user.last_name or 'User',
                tx_ref=str(payment.payment_id),
                callback_url=callback_url,
                return_url=return_url,
                currency=payment.currency
            )

            # Update payment with checkout URL
            payment.checkout_url = response['data']['checkout_url']
            payment.save()

            return Response({
                'checkout_url': payment.checkout_url,
                'transaction_ref': payment.tx_ref
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentCompleteView(views.APIView):
    """Handle payment completion redirect"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, payment_id=payment_id)
        
        # Verify the payment belongs to the user
        if not request.user.is_staff and payment.booking.user != request.user:
            return Response(
                {'error': 'Not authorized to view this payment'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
