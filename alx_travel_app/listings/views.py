from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.urls import reverse
from django.conf import settings
from django_chapa import api as chapa_api
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email, send_payment_confirmation_email, send_payment_checkout_email


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
        responses={200: ListingSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new property listing",
        request_body=ListingSerializer,
        responses={201: ListingSerializer()}
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
        if getattr(self, 'swagger_fake_view', False):  # for schema generation
            return Booking.objects.none()
        
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Send booking confirmation email asynchronously
        send_booking_confirmation_email.delay(
            booking_id=str(booking.booking_id),
            user_email=booking.user.email,
            listing_title=booking.property.name
        )

    @swagger_auto_schema(
        operation_description="List all bookings for the authenticated user",
        responses={200: BookingSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new booking",
        request_body=BookingSerializer,
        responses={201: BookingSerializer()}
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
    """
    ViewSet for managing payments.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter payments based on user role"""
        if getattr(self, 'swagger_fake_view', False):  # for schema generation
            return Payment.objects.none()
            
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__user=user)

    @swagger_auto_schema(
        operation_description="Verify payment status with Chapa",
        responses={
            200: openapi.Response(
                description="Payment status verified",
                schema=PaymentSerializer()
            )
        }
    )
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify payment status with Chapa"""
        payment = self.get_object()
        
        try:
            # Prepare headers with Chapa secret key
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET}',
                'Content-Type': 'application/json'
            }

            # Make verification request to Chapa API
            import requests
            response = requests.get(
                f'{settings.CHAPA_API_URL}/v1/transaction/verify/{payment.id}',
                headers=headers
            )
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status') == 'success':
                # Update payment status
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.response_dump = response_data
                payment.save()

                # Send payment confirmation email
                send_payment_confirmation_email.delay(
                    payment_id=str(payment.id),
                    user_email=payment.booking.user.email
                )

                # Update booking status
                booking = payment.booking
                booking.status = Booking.BookingStatus.CONFIRMED
                booking.save()

            return Response(PaymentSerializer(payment).data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def initialize(self, request, pk=None):
        """Initialize payment for a booking"""
        payment = self.get_object()
        booking = payment.booking
        user = booking.user

        # Update payment with user details
        payment.email = user.email
        payment.first_name = user.first_name or 'Guest'
        payment.last_name = user.last_name or 'User'
        payment.payment_title = 'Booking Payment'
        payment.description = f'Booking from {booking.start_date} to {booking.end_date}'
        payment.save()

        callback_url = request.build_absolute_uri('/api/chapa-webhook/')
        return_url = request.build_absolute_uri(
            reverse('payment-complete', args=[payment.id])
        )

        try:
            # Prepare headers with Chapa secret key
            headers = {
                'Authorization': f'Bearer {settings.CHAPA_SECRET}',
                'Content-Type': 'application/json'
            }

            # Prepare payload for Chapa API
            payload = {
                'amount': str(payment.amount),
                'currency': payment.currency,
                'email': payment.email,
                'first_name': payment.first_name,
                'last_name': payment.last_name,
                'phone_number': payment.phone_number,
                'tx_ref': str(payment.id),
                'callback_url': callback_url,
                'return_url': return_url,
                'customization': {
                    'title': 'Booking Payment',
                    'description': payment.description
                }
            }

            # Make direct request to Chapa API
            import requests
            response = requests.post(
                f'{settings.CHAPA_API_URL}/v1/transaction/initialize',
                json=payload,
                headers=headers
            )
            response_data = response.json()

            if response.status_code != 200:
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                raise Exception(f"Chapa API error: {response_data.get('message', str(response_data))}")

            # Update payment with checkout URL and response
            payment.checkout_url = response_data['data']['checkout_url']
            payment.response_dump = response_data
            payment.save()

            # Send checkout URL to user's email
            send_payment_checkout_email.delay(
                payment_id=str(payment.id),
                user_email=payment.email,
                checkout_url=payment.checkout_url
            )

            return Response({
                'checkout_url': payment.checkout_url,
                'transaction_ref': str(payment.id),
                'message': 'Payment checkout link has been sent to your email'
            })

        except Exception as e:
            # Update payment status on failure
            payment.status = Payment.PaymentStatus.FAILED
            payment.save()
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Create a new payment for a booking",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['booking', 'amount', 'currency', 'email', 'phone_number', 'first_name', 'last_name'],
            properties={
                'booking': openapi.Schema(type=openapi.TYPE_STRING, description='Booking UUID'),
                'amount': openapi.Schema(type=openapi.TYPE_STRING, description='Amount to be paid (e.g., "1250.00")'),
                'currency': openapi.Schema(type=openapi.TYPE_STRING, description='Currency code (e.g., "ETB")'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Customer email address'),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Customer phone number'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Customer first name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Customer last name'),
                'payment_title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the payment'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Payment description')
            }
        ),
        responses={
            201: PaymentSerializer(),
            400: "Bad Request - Invalid input data",
            404: "Not Found - Booking not found"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PaymentCompleteView(views.APIView):
    """Handle payment completion redirect"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get payment details after completion",
        responses={
            200: PaymentSerializer(),
            403: "Forbidden",
            404: "Not Found"
        }
    )
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Verify the payment belongs to the user
        if not request.user.is_staff and payment.booking.user != request.user:
            return Response(
                {'error': 'Not authorized to view this payment'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
