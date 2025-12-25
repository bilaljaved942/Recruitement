"""
Email Service for sending interview notifications.
Uses Gmail SMTP (free, up to 500 emails/day).
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from ..config import settings


class EmailService:
    """Service for sending emails via Gmail SMTP."""
    
    def __init__(self):
        self.smtp_email = settings.SMTP_EMAIL
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
    
    def is_configured(self) -> bool:
        """Check if email settings are properly configured."""
        return bool(self.smtp_email and self.smtp_password)
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an email using SMTP."""
        if not self.is_configured():
            raise ValueError("Email not configured. Set SMTP_EMAIL and SMTP_PASSWORD in .env")
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"RecruitAI <{self.smtp_email}>"
            msg['To'] = to_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.sendmail(self.smtp_email, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            raise
    
    def send_interview_invitation(
        self,
        applicant_email: str,
        applicant_name: str,
        job_title: str,
        company_name: str = "Our Company"
    ) -> bool:
        """Send interview invitation email to an applicant."""
        subject = f"🎉 Interview Invitation: {job_title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .highlight {{ background: #e0e7ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p>You've Been Selected for an Interview</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{applicant_name}</strong>,</p>
                    
                    <p>We are thrilled to inform you that after carefully reviewing your application, 
                    you have been <strong>shortlisted for an interview</strong> for the position of:</p>
                    
                    <div class="highlight">
                        <h2 style="margin: 0; color: #4f46e5;">📋 {job_title}</h2>
                    </div>
                    
                    <p>Your resume and qualifications stood out among many applicants, and we are excited 
                    to learn more about you!</p>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Our HR team will contact you shortly with interview scheduling details</li>
                        <li>Please ensure your phone and email are accessible</li>
                        <li>Prepare any questions you may have about the role</li>
                    </ul>
                    
                    <p>If you have any questions, feel free to reply to this email.</p>
                    
                    <p>Best regards,<br>
                    <strong>The {company_name} Hiring Team</strong></p>
                </div>
                <div class="footer">
                    <p>This email was sent via RecruitAI Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(applicant_email, subject, html_body)
    
    def send_hr_summary(
        self,
        hr_email: str,
        hr_name: str,
        job_title: str,
        selected_applicants: List[Dict[str, Any]],
        total_applicants: int
    ) -> bool:
        """Send summary email to HR with selected candidates."""
        subject = f"📊 Shortlist Summary: {job_title} - {len(selected_applicants)} Candidates Selected"
        
        # Build applicants table
        applicants_rows = ""
        for i, app in enumerate(selected_applicants, 1):
            applicants_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{i}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;"><strong>{app['name']}</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{app['email']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">
                    <span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold;">
                        {app['score']}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <a href="{app['resume_url']}" style="color: #6366f1; text-decoration: none;">View Resume</a>
                </td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat {{ text-align: center; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #6366f1; }}
                .stat-label {{ color: #6b7280; font-size: 14px; }}
                table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                th {{ background: #4f46e5; color: white; padding: 15px; text-align: left; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Shortlist Summary</h1>
                    <p>{job_title}</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{hr_name}</strong>,</p>
                    
                    <p>The following candidates have been automatically shortlisted based on their AI resume scores 
                    and have been sent interview invitation emails.</p>
                    
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">{total_applicants}</div>
                            <div class="stat-label">Total Applicants</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{len(selected_applicants)}</div>
                            <div class="stat-label">Selected for Interview</div>
                        </div>
                    </div>
                    
                    <h3>📋 Selected Candidates</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>AI Score</th>
                                <th>Resume</th>
                            </tr>
                        </thead>
                        <tbody>
                            {applicants_rows}
                        </tbody>
                    </table>
                    
                    <p style="margin-top: 20px;">All selected candidates have been notified via email and their 
                    application status has been updated to <strong>"Shortlisted"</strong> in the system.</p>
                    
                    <p>Best regards,<br>
                    <strong>RecruitAI Platform</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email from RecruitAI</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(hr_email, subject, html_body)


# Singleton instance
email_service = EmailService()
