"""
Email service using Resend API with Jinja2 templates
"""
import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Resend API key
resend.api_key = settings.RESEND_API_KEY

# Setup Jinja2 environment for email templates
template_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    """Service for sending emails using Resend"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email using Resend API
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email (defaults to settings.RESEND_FROM_EMAIL)
            
        Returns:
            Response from Resend API
        """
        if from_email is None:
            from_email = settings.RESEND_FROM_EMAIL
            
        try:
            params = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to_email}: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise
    
    @staticmethod
    def render_template(template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template with context
        
        Args:
            template_name: Name of the template file (e.g., 'verify_email.html')
            context: Dictionary of variables to pass to the template
            
        Returns:
            Rendered HTML string
        """
        try:
            template = jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise
    
    @classmethod
    def send_verification_email(cls, to_email: str, name: str, verification_token: str) -> Dict[str, Any]:
        """
        Send email verification email
        
        Args:
            to_email: User's email address
            name: User's name
            verification_token: Verification token
            
        Returns:
            Response from Resend API
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        context = {
            "name": name,
            "verification_url": verification_url,
            "app_name": "TaskFlow"
        }
        
        html_content = cls.render_template("verify_email.html", context)
        
        return cls.send_email(
            to_email=to_email,
            subject="Verify your TaskFlow account",
            html_content=html_content
        )
    
    @classmethod
    def send_password_reset_email(cls, to_email: str, name: str, reset_token: str) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            to_email: User's email address
            name: User's name
            reset_token: Password reset token
            
        Returns:
            Response from Resend API
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        context = {
            "name": name,
            "reset_url": reset_url,
            "app_name": "TaskFlow"
        }
        
        html_content = cls.render_template("reset_password.html", context)
        
        return cls.send_email(
            to_email=to_email,
            subject="Reset your TaskFlow password",
            html_content=html_content
        )
    
    @classmethod
    def send_welcome_email(cls, to_email: str, name: str) -> Dict[str, Any]:
        """
        Send welcome email after successful verification
        
        Args:
            to_email: User's email address
            name: User's name
            
        Returns:
            Response from Resend API
        """
        context = {
            "name": name,
            "app_name": "TaskFlow",
            "login_url": f"{settings.FRONTEND_URL}/login"
        }
        
        html_content = cls.render_template("welcome_email.html", context)
        
        return cls.send_email(
            to_email=to_email,
            subject="Welcome to TaskFlow!",
            html_content=html_content
        )

