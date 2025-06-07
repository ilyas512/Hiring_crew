from typing import Dict, Any, Optional, ClassVar, List
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, PrivateAttr

# Load environment variables
load_dotenv()

class EmailSender:
    """Helper class to send emails to candidates."""
    
    def __init__(self):
        """Initialize email sender with SMTP settings from environment."""
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('SENDER_EMAIL')

    def send_assessment_email(self, recipient_email: str, form_url: str, job_title: str) -> bool:
        """Send assessment email to a candidate."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Technical Assessment for {job_title} Position"

            body = f"""
            Hello,

            Thank you for your interest in the {job_title} position. As part of our evaluation process, 
            we would like you to complete a technical assessment.

            Please click the link below to access your assessment:
            {form_url}

            Please complete this assessment at your earliest convenience. Your responses will help us 
            better understand your technical expertise.

            Best regards,
            The Recruitment Team
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")
            return False

class FormDistributionAgent:
    """Agent responsible for creating and distributing assessment forms."""
    
    def __init__(self):
        """Initialize the FormDistributionAgent."""
        self.google_form_creator = GoogleFormCreator()
        self.email_sender = EmailSender()

    def transform_quiz_data(self, quiz_data: Dict[str, Any]) -> str:
        """Transform quiz data into the format expected by Google Form Creator."""
        try:
            # Create a text representation of the quiz
            quiz_text = f"Technical Assessment for {quiz_data['offer_title']}\n\n"
            
            question_number = 1
            for skill, questions in quiz_data['quiz'].items():
                for q in questions:
                    quiz_text += f"{question_number}. {q['Question']}\n"
                    quiz_text += f"A. {q['A']}\n"
                    quiz_text += f"B. {q['B']}\n"
                    quiz_text += f"C. {q['C']}\n"
                    quiz_text += f"D. {q['D']}\n"
                    quiz_text += f"Correct Answer: {q['Answer']}\n\n"
                    question_number += 1
            
            # Format as required by the tool
            result = {"quiz_data": quiz_text}
            print("Transformed quiz data:", result)
            return json.dumps(result)
        except Exception as e:
            print(f"Error in transform_quiz_data: {str(e)}")
            raise

    def create_and_distribute_forms(self, quiz_data: Dict[str, Any], candidate_emails: List[str] = None) -> Dict[str, Any]:
        """Create and distribute assessment forms."""
        try:
            print("Input quiz data:", quiz_data)
            # Transform the quiz data into the correct format (plain text)
            formatted_quiz = self.transform_quiz_data(quiz_data)
            print("Formatted quiz:", formatted_quiz)
            
            # Create the Google Form
            form_url = self.google_form_creator._run(formatted_quiz)
            print("Form URL:", form_url)
            
            if not form_url:
                raise Exception("Failed to create Google Form")

            # Send emails if candidate_emails are provided
            emails_sent = []
            status = {}
            
            if candidate_emails:
                for email in candidate_emails:
                    success = self.email_sender.send_assessment_email(
                        email, 
                        form_url, 
                        quiz_data['offer_title']
                    )
                    if success:
                        emails_sent.append(email)
                        status[email] = "success"
                    else:
                        status[email] = "failed"

            return {
                "form_url": form_url,
                "emails_sent": emails_sent,
                "status": status
            }
            
        except Exception as e:
            print(f"Error in form creation and distribution: {str(e)}")
            return {
                "form_url": None,
                "emails_sent": [],
                "status": {}
            }

class GoogleFormCreator(BaseTool):
    """Tool for creating Google Forms using Google Forms API."""
    
    name: str = "google_form_creator"
    description: str = "Creates Google Forms for technical assessments"
    SCOPES: ClassVar[list] = [
        'https://www.googleapis.com/auth/forms',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]
    _creds: Optional[Credentials] = PrivateAttr(default=None)

    def __init__(self):
        """Initialize the GoogleFormCreator with OAuth2 credentials."""
        super().__init__()
        self._creds = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Forms API."""
        creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'src/config/credentials.json')
        token_path = os.getenv('GOOGLE_TOKEN_PATH', 'src/config/token.json')
        
        if os.path.exists(token_path):
            self._creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                self._creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(self._creds.to_json())

    def create_form(self, title: str, description: str, questions: list) -> str:
        """Create a Google Form with the given questions."""
        try:
            service = build('forms', 'v1', credentials=self._creds)
            
            # Create form with just the title
            form = {
                'info': {
                    'title': title
                }
            }
            result = service.forms().create(body=form).execute()
            form_id = result['formId']
            
            # Update form with description and questions
            updates = {
                'requests': [
                    {
                        'updateFormInfo': {
                            'info': {
                                'description': description
                            },
                            'updateMask': 'description'
                        }
                    }
                ]
            }
            
            # Add questions
            for q in questions:
                updates['requests'].append({
                    'createItem': {
                        'item': {
                            'title': q['question'],
                            'questionItem': {
                                'question': {
                                    'required': True,
                                    'choiceQuestion': {
                                        'type': 'RADIO',
                                        'options': [{'value': opt} for opt in q['options']],
                                        'shuffle': False
                                    }
                                }
                            }
                        },
                        'location': {'index': len(updates['requests']) - 1}
                    }
                })
            
            service.forms().batchUpdate(formId=form_id, body=updates).execute()
            
            return f"https://docs.google.com/forms/d/{form_id}/viewform"
            
        except Exception as e:
            print(f"Error creating Google Form: {str(e)}")
            return None

    def _run(self, quiz_data: str) -> str:
        """Required method from BaseTool. Creates a Google Form from string input."""
        try:
            print("Received quiz data:", quiz_data)
            # Parse the input string
            data = json.loads(quiz_data)
            quiz_content = data.get('quiz_data')
            
            if not quiz_content:
                raise ValueError("Quiz data is missing or empty")
            
            # Parse the quiz content into structured data
            lines = quiz_content.strip().split('\n\n')
            title = lines[0]
            questions = []
            
            current_question = None
            for line in lines[1:]:
                if not line.strip():
                    continue
                    
                lines = line.split('\n')
                if lines[0].startswith(tuple('123456789')):
                    if current_question:
                        questions.append(current_question)
                    
                    current_question = {
                        'question': lines[0].split('. ', 1)[1],
                        'options': []
                    }
                    
                    for opt in lines[1:5]:
                        current_question['options'].append(opt.split('. ', 1)[1])
            
            if current_question:
                questions.append(current_question)
            
            # Create the form using Google Forms API
            form_url = self.create_form(title, "Please answer all questions carefully.", questions)
            
            if not form_url:
                raise Exception("Failed to create Google Form")
            
            return form_url
            
        except json.JSONDecodeError as e:
            print(f"Error parsing quiz data: {str(e)}")
            return None
        except Exception as e:
            print(f"Error creating form: {str(e)}")
            return None 