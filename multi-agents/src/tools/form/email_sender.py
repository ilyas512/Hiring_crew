from crewai.tools import BaseTool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional, Any

class EmailSender(BaseTool):
    name: str = "Email Sender"
    description: str = "Sends emails to candidates with their Google Form assessment link"

    # SMTP Settings from environment variables
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL: Optional[str] = os.getenv("SENDER_EMAIL")

    def _run(self, input_data: str) -> str:
        """Sends assessment emails to candidates."""
        try:
            data = eval(input_data)  # Convert string to dict
            candidate_email = data['email']
            candidate_name = data['name']
            form_url = data['form_url']
            job_title = data['job_title']

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.SENDER_EMAIL
            msg['To'] = candidate_email
            msg['Subject'] = f"Technical Assessment for {job_title} Position"

            body = f"""Dear {candidate_name},

We hope this email finds you well. As part of our recruitment process for the {job_title} position, we invite you to complete a technical assessment.

Please access the assessment using the following link:
{form_url}

Important Notes:
- Please complete the assessment within 48 hours
- Ensure you answer all questions
- Take your time to provide thoughtful responses

If you encounter any technical issues, please don't hesitate to contact us.

Best regards,
The Recruitment Team"""

            msg.attach(MIMEText(body, 'plain'))

            # Setup SMTP server
            server = smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT)
            server.starttls()
            server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
            
            # Send email
            server.send_message(msg)
            server.quit()

            return f"Successfully sent assessment email to {candidate_email}"

        except Exception as e:
            return f"Error sending email: {str(e)}"

    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async implementation of the tool - not needed for this tool."""
        raise NotImplementedError("EmailSender does not support async") 