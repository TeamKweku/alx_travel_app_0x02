from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

@shared_task
def send_booking_confirmation_email(booking_id, user_email, listing_title):
    """
    Send a booking confirmation email to the user.
    """
    subject = f'Booking Confirmation - {listing_title}'
    message = f'''
    Thank you for your booking!
    
    Your booking (ID: {booking_id}) for {listing_title} has been confirmed.
    
    Thank you for choosing our service!
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    
    return f"Confirmation email sent for booking {booking_id}"

@shared_task
def send_payment_confirmation_email(payment_id: str, user_email: str):
    """Send payment confirmation email to user"""
    try:
        payment = Payment.objects.get(id=payment_id)
        booking = payment.booking
        
        subject = f'Payment Confirmation - {booking.property.name}'
        message = f"""
        Dear {booking.user.get_full_name() or 'Guest'},

        Your payment of {payment.currency} {payment.amount} for booking {booking.booking_id} has been confirmed.

        Booking Details:
        - Property: {booking.property.name}
        - Check-in: {booking.start_date}
        - Check-out: {booking.end_date}
        - Total Amount: {payment.currency} {payment.amount}
        - Transaction Reference: {payment.chapa_transaction_ref}

        Thank you for choosing our service!

        Best regards,
        ALX Travel Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        return f"Payment confirmation email sent to {user_email}"
        
    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"
    except Exception as e:
        return f"Error sending payment confirmation email: {str(e)}" 