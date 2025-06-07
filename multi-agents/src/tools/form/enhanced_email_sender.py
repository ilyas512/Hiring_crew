"""
Enhanced Email Sender with better templating and error handling
"""

from crewai.tools import BaseTool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class EnhancedEmailSender(BaseTool):
    name: str = "Enhanced Email Sender"
    description: str = """
    Sends personalized assessment emails to candidates with Google Form links.
    Supports batch sending, email templates, and delivery tracking.
    """

    def __init__(self):
        super().__init__()
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")
        
        # Validate email configuration
        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            raise ValueError("Email configuration incomplete. Check SMTP environment variables.")

    def _create_email_template(self, candidate_name: str, job_title: str, form_url: str) -> str:
        """Create a professional email template."""
        template = f"""
Dear {candidate_name},

Thank you for your interest in the {job_title} position with our company. We have reviewed your application and would like to invite you to complete a technical assessment as the next step in our recruitment process.

📋 Assessment Details:
• Position: {job_title}
• Assessment Type: Technical Skills Evaluation
• Estimated Time: 30-45 minutes
• Deadline: 48 hours from receipt of this email

🔗 Access Your Assessment:
Please click the following link to begin your assessment:
{form_url}

📝 Important Instructions:
• Complete all questions to the best of your ability
• You may take your time, but please submit within the deadline
• Ensure you have a stable internet connection
• Contact us immediately if you experience any technical issues

We appreciate your time and effort in this process. Your responses will help us better understand your technical expertise and determine the best fit for our team.

If you have any questions or concerns, please don't hesitate to reach out to us.

Best regards,
The Recruitment Team

---
This is an automated message. Please do not reply directly to this email.
For questions, contact: {self.sender_email}
"""
        return template.strip()

    def _send_single_email(self, recipient_email: str, candidate_name: str, 
                          job_title: str, form_url: str) -> Dict[str, Any]:
        """Send email to a single candidate."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Technical Assessment Invitation - {job_title} Position"
            
            # Create email body
            body = self._create_email_template(candidate_name, job_title, form_url)
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return {
                "email": recipient_email,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            return {
                "email": recipient_email,
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _parse_input_data(self, input_data: str) -> Dict[str, Any]:
        """Parse input data for email sending."""
        try:
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            required_fields = ['form_url', 'job_title', 'candidates']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def _run(self, input_data: str) -> str:
        """Main execution method for sending emails."""
        try:
            # Parse input data
            data = self._parse_input_data(input_data)
            
            form_url = data['form_url']
            job_title = data['job_title']
            candidates = data['candidates']
            
            if not form_url or not form_url.startswith('http'):
                return json.dumps({
                    "status": "failed",
                    "error": "Invalid or missing form URL"
                })
            
            # Send emails to candidates
            results = []
            successful_sends = []
            failed_sends = []
            
            for candidate in candidates:
                email = candidate.get('email', '')
                name = candidate.get('full_name', candidate.get('name', 'Candidate'))
                
                if not email:
                    failed_sends.append({
                        "candidate": name,
                        "error": "Missing email address"
                    })
                    continue
                
                result = self._send_single_email(email, name, job_title, form_url)
                results.append(result)
                
                if result['status'] == 'success':
                    successful_sends.append(email)
                else:
                    failed_sends.append({
                        "email": email,
                        "error": result.get('error', 'Unknown error')
                    })
            
            # Prepare summary
            summary = {
                "status": "completed",
                "total_candidates": len(candidates),
                "emails_sent": len(successful_sends),
                "emails_failed": len(failed_sends),
                "successful_emails": successful_sends,
                "failed_emails": failed_sends,
                "detailed_results": results,
                "form_url": form_url,
                "job_title": job_title
            }
            
            print(f"📧 Email Summary: {len(successful_sends)}/{len(candidates)} emails sent successfully")
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ Email sending failed: {str(e)}")
            return json.dumps(error_result)

    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async implementation - not supported for this tool."""
        raise NotImplementedError("EnhancedEmailSender does not support async execution")