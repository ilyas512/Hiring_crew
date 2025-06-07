"""
Enhanced Google Form Creator with better error handling and CrewAI compliance
"""

from crewai.tools import BaseTool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
from typing import Optional, List, Dict, Any

class EnhancedGoogleFormCreator(BaseTool):
    name: str = "Enhanced Google Form Creator"
    description: str = """
    Creates Google Forms with quiz questions and returns the form URL.
    Handles authentication, form creation, and question addition with proper error handling.
    """

    # Google API Configuration
    SCOPES: List[str] = [
        'https://www.googleapis.com/auth/forms',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]

    def __init__(self):
        super().__init__()
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "src/config/credentials.json")
        self.token_path = os.getenv("GOOGLE_TOKEN_PATH", "src/config/token.json")
        self.creds = None

    def _authenticate(self) -> bool:
        """Authenticate with Google APIs."""
        try:
            # Load existing credentials
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Google credentials file not found: {self.credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(self.creds.to_json())
            
            return True
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    def _parse_quiz_data(self, quiz_input: str) -> Dict[str, Any]:
        """Parse quiz data from various input formats."""
        try:
            # Try to parse as JSON
            if isinstance(quiz_input, str):
                quiz_data = json.loads(quiz_input)
            else:
                quiz_data = quiz_input
            
            # Extract questions from the quiz structure
            questions = []
            
            if 'quiz' in quiz_data:
                for skill, skill_questions in quiz_data['quiz'].items():
                    for q in skill_questions:
                        question_obj = {
                            'question': q.get('Question', ''),
                            'options': [
                                q.get('A', ''),
                                q.get('B', ''),
                                q.get('C', ''),
                                q.get('D', '')
                            ],
                            'correct_answer': q.get('Answer', 'A'),
                            'skill': skill
                        }
                        questions.append(question_obj)
            
            return {
                'title': quiz_data.get('offer_title', 'Technical Assessment'),
                'description': f"Technical assessment for {quiz_data.get('offer_title', 'this position')}",
                'questions': questions
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing quiz data: {str(e)}")

    def _create_form_structure(self, form_data: Dict[str, Any]) -> str:
        """Create the Google Form with questions."""
        try:
            service = build('forms', 'v1', credentials=self.creds)
            
            # Create the form
            form_body = {
                'info': {
                    'title': form_data['title'],
                    'description': form_data['description']
                }
            }
            
            created_form = service.forms().create(body=form_body).execute()
            form_id = created_form['formId']
            
            # Prepare batch update requests for questions
            requests = []
            
            for idx, question in enumerate(form_data['questions']):
                if not question['question'].strip():
                    continue
                
                # Create question item
                question_item = {
                    'createItem': {
                        'item': {
                            'title': question['question'],
                            'description': f"Skill: {question.get('skill', 'General')}",
                            'questionItem': {
                                'question': {
                                    'required': True,
                                    'choiceQuestion': {
                                        'type': 'RADIO',
                                        'options': [
                                            {'value': option.strip()} 
                                            for option in question['options'] 
                                            if option.strip()
                                        ],
                                        'shuffle': False
                                    }
                                }
                            }
                        },
                        'location': {'index': idx}
                    }
                }
                requests.append(question_item)
            
            # Add questions to form
            if requests:
                batch_update_body = {'requests': requests}
                service.forms().batchUpdate(formId=form_id, body=batch_update_body).execute()
            
            # Return the form URL
            form_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
            return form_url
            
        except HttpError as e:
            raise RuntimeError(f"Google API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Form creation error: {str(e)}")

    def _run(self, quiz_data: str) -> str:
        """Main execution method for the tool."""
        try:
            # Authenticate with Google
            if not self._authenticate():
                return "Error: Google authentication failed"
            
            # Parse quiz data
            form_data = self._parse_quiz_data(quiz_data)
            
            if not form_data['questions']:
                return "Error: No valid questions found in quiz data"
            
            # Create the form
            form_url = self._create_form_structure(form_data)
            
            print(f"✅ Google Form created successfully: {form_url}")
            return form_url
            
        except Exception as e:
            error_msg = f"Error creating Google Form: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async implementation - not supported for this tool."""
        raise NotImplementedError("EnhancedGoogleFormCreator does not support async execution")