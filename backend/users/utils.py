from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_email_safely(subject, message, recipient_list, html_message=None, fail_silently=False):
    """
    Safely send emails with proper error handling and logging
    """
    try:
        # Ensure we have required email settings
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.warning("Email credentials not configured. Email not sent.")
            return False
        
        # Send the email
        result = send_mail(
            subject=subject,
            message=strip_tags(message) if html_message else message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=fail_silently
        )
        
        if result:
            logger.info(f"Email sent successfully to {recipient_list}")
        else:
            logger.error(f"Failed to send email to {recipient_list}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending email to {recipient_list}: {str(e)}")
        if not fail_silently:
            raise
        return False

def send_welcome_email(user):
    """
    Send welcome email to newly registered users
    """
    subject = "Welcome to Client-Nest!"
    html_message = render_to_string('users/email/welcome.html', {
        'user': user,
        'site_name': 'Client-Nest'
    })
    
    return send_email_safely(
        subject=subject,
        message="Welcome to Client-Nest!",
        recipient_list=[user.email],
        html_message=html_message
    )

def send_password_reset_email(user, reset_url):
    """
    Send password reset email
    """
    subject = "Password Reset Request - Client-Nest"
    html_message = render_to_string('users/email/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'Client-Nest'
    })
    
    return send_email_safely(
        subject=subject,
        message="Password reset requested",
        recipient_list=[user.email],
        html_message=html_message
    ) 