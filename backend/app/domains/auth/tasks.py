"""
Celery tasks for authentication domain
"""
from app.celery_app import celery
from app.core.email import EmailService
import logging

logger = logging.getLogger(__name__)


@celery.task(name="auth.send_verification_email")
def send_verification_email_task(email: str, name: str, verification_token: str):
    """
    Celery task to send verification email asynchronously
    
    Args:
        email: User's email address
        name: User's name
        verification_token: Verification token
    """
    try:
        logger.info(f"Sending verification email to {email}")
        EmailService.send_verification_email(
            to_email=email,
            name=name,
            verification_token=verification_token
        )
        logger.info(f"Verification email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        raise


@celery.task(name="auth.send_password_reset_email")
def send_password_reset_email_task(email: str, name: str, reset_token: str):
    """
    Celery task to send password reset email asynchronously
    
    Args:
        email: User's email address
        name: User's name
        reset_token: Password reset token
    """
    try:
        logger.info(f"Sending password reset email to {email}")
        EmailService.send_password_reset_email(
            to_email=email,
            name=name,
            reset_token=reset_token
        )
        logger.info(f"Password reset email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        raise


@celery.task(name="auth.send_welcome_email")
def send_welcome_email_task(email: str, name: str):
    """
    Celery task to send welcome email asynchronously
    
    Args:
        email: User's email address
        name: User's name
    """
    try:
        logger.info(f"Sending welcome email to {email}")
        EmailService.send_welcome_email(
            to_email=email,
            name=name
        )
        logger.info(f"Welcome email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        raise

