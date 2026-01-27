"""
Email Notification Service for Alertix
========================================
Sends theft alert emails via Gmail SMTP with App Password authentication.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional
import base64
import io

from config import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USE_TLS,
    EMAIL_ADDRESS,
    EMAIL_APP_PASSWORD,
    RECEIVER_EMAIL,
    EMAIL_NOTIFICATIONS_ENABLED,
    EMAIL_RETRY_ATTEMPTS
)

logger = logging.getLogger(__name__)


class EmailService:
    """Handles sending email notifications for theft alerts."""

    def __init__(self):
        self.host = EMAIL_HOST
        self.port = EMAIL_PORT
        self.use_tls = EMAIL_USE_TLS
        self.sender_email = EMAIL_ADDRESS
        self.app_password = EMAIL_APP_PASSWORD
        self.receiver_email = RECEIVER_EMAIL
        self.enabled = EMAIL_NOTIFICATIONS_ENABLED

    def send_theft_alert(
        self,
        camera_name: str,
        camera_id: str,
        confidence: float,
        timestamp: str,
        image_base64: Optional[str] = None,
        detections: Optional[list] = None
    ) -> bool:
        """
        Send theft alert email notification.

        Args:
            camera_name: Name of the camera that detected theft
            camera_id: ID of the camera
            confidence: Detection confidence score
            timestamp: Time of detection
            image_base64: Base64 encoded image with bounding boxes
            detections: List of detection details

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email notifications disabled - skipping")
            return True

        if self.app_password == "your_app_password_here":
            logger.warning("⚠️ Email App Password not configured - skipping email notification")
            return False

        # Retry logic
        for attempt in range(EMAIL_RETRY_ATTEMPTS + 1):
            try:
                success = self._send_email(
                    camera_name=camera_name,
                    camera_id=camera_id,
                    confidence=confidence,
                    timestamp=timestamp,
                    image_base64=image_base64,
                    detections=detections
                )
                if success:
                    logger.info(f"✅ Theft alert email sent to {self.receiver_email}")
                    return True
            except Exception as e:
                logger.error(f"❌ Email send attempt {attempt + 1} failed: {e}")
                if attempt < EMAIL_RETRY_ATTEMPTS:
                    logger.info(f"Retrying... ({attempt + 2}/{EMAIL_RETRY_ATTEMPTS + 1})")

        logger.error(f"❌ Failed to send email after {EMAIL_RETRY_ATTEMPTS + 1} attempts")
        return False

    def _send_email(
        self,
        camera_name: str,
        camera_id: str,
        confidence: float,
        timestamp: str,
        image_base64: Optional[str] = None,
        detections: Optional[list] = None
    ) -> bool:
        """Internal method to send email via SMTP."""

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 THEFT ALERT - {camera_name} - Alertix Security"
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email

        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = timestamp

        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header .icon {{ font-size: 50px; margin-bottom: 10px; }}
                .content {{ padding: 30px; }}
                .alert-box {{ background: #ffeaea; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; color: #666; }}
                .detail-value {{ color: #333; }}
                .confidence {{ font-size: 24px; font-weight: bold; color: #e74c3c; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .image-container {{ text-align: center; margin: 20px 0; }}
                .image-container img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icon">🚨</div>
                    <h1>THEFT DETECTED</h1>
                    <p>Immediate attention required</p>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <strong>⚠️ Security Alert:</strong> Potential theft activity has been detected by your Alertix security system.
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">📷 Camera:</span>
                        <span class="detail-value">{camera_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">🆔 Camera ID:</span>
                        <span class="detail-value">{camera_id[:8]}...</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">🕐 Time:</span>
                        <span class="detail-value">{formatted_time}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📊 Confidence:</span>
                        <span class="confidence">{confidence:.1%}</span>
                    </div>

                    {"<div class='image-container'><p><strong>📸 Detection Snapshot:</strong></p><p><em>Image attached below</em></p></div>" if image_base64 else ""}

                    <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 4px;">
                        <strong>🔔 Recommended Actions:</strong>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Review the attached image immediately</li>
                            <li>Check your live camera feed</li>
                            <li>Contact security if needed</li>
                            <li>Save evidence for future reference</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>This alert was generated by <strong>Alertix Security System</strong></p>
                    <p>© 2026 Alertix - YOLO Theft Detection</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_body = f"""
🚨 THEFT ALERT - Alertix Security System

⚠️ Potential theft activity detected!

Details:
- Camera: {camera_name}
- Camera ID: {camera_id[:8]}...
- Time: {formatted_time}
- Confidence: {confidence:.1%}

Please review your security cameras immediately.

---
Alertix - YOLO Theft Detection System
        """

        # Attach text and HTML parts
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Attach image if provided
        if image_base64:
            try:
                # Remove data URL prefix if present
                if ',' in image_base64:
                    image_base64 = image_base64.split(',')[1]

                image_data = base64.b64decode(image_base64)
                image_part = MIMEBase('image', 'jpeg')
                image_part.set_payload(image_data)
                encoders.encode_base64(image_part)
                image_part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="theft_detection_{camera_id[:8]}_{formatted_time.replace(":", "-").replace(" ", "_")}.jpg"'
                )
                msg.attach(image_part)
            except Exception as e:
                logger.warning(f"Failed to attach image: {e}")

        # Send email via SMTP
        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.sender_email, self.app_password)
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())

        return True


# Global instance
email_service = EmailService()


def send_theft_alert_email(
    camera_name: str,
    camera_id: str,
    confidence: float,
    timestamp: str,
    image_base64: Optional[str] = None,
    detections: Optional[list] = None
) -> bool:
    """
    Convenience function to send theft alert email.

    This function does NOT block the prediction pipeline - it logs errors
    and returns False on failure without raising exceptions.
    """
    try:
        return email_service.send_theft_alert(
            camera_name=camera_name,
            camera_id=camera_id,
            confidence=confidence,
            timestamp=timestamp,
            image_base64=image_base64,
            detections=detections
        )
    except Exception as e:
        logger.error(f"❌ Email service error (non-blocking): {e}")
        return False
