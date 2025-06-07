from crewai.tools import BaseTool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import os
from typing import Optional, List, Any

class GoogleFormCreator(BaseTool):
    name: str = "Google Form Creator"
    description: str = "Creates a Google Form with quiz questions and returns the form URL"

    # Google API Settings from environment variables
    CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "src/config/credentials.json")
    TOKEN_PATH: str = os.getenv("GOOGLE_TOKEN_PATH", "src/config/token.json")
    SCOPES: List[str] = [
        'https://www.googleapis.com/auth/forms',
        'https://www.googleapis.com/auth/drive'
    ]

    def _load_credentials(self):
        """Load or refresh Google credentials."""
        creds = None
        if os.path.exists(self.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, self.SCOPES)
        
        if not creds or not creds.valid:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_PATH, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        return creds

    def _run(self, quiz_data: str) -> str:
        """Creates a Google Form with the provided quiz questions."""
        try:
            quiz_json = json.loads(quiz_data)
            creds = self._load_credentials()
            
            if not creds:
                return "Error: No valid credentials found"

            forms_service = build('forms', 'v1', credentials=creds)
            
            # Create form
            form_body = {
                'info': {
                    'title': f"Technical Assessment: {quiz_json.get('job_title', 'Position')}",
                    'description': 'Please complete this technical assessment. Your responses will be evaluated as part of the recruitment process.'
                }
            }
            
            created_form = forms_service.forms().create(body=form_body).execute()
            form_id = created_form['formId']

            # Add questions
            questions_body = {
                'requests': []
            }

            for idx, question in enumerate(quiz_json.get('questions', [])):
                question_item = {
                    'createItem': {
                        'item': {
                            'title': question['question'],
                            'questionItem': {
                                'question': {
                                    'required': True,
                                    'choiceQuestion': {
                                        'type': 'RADIO',
                                        'options': [
                                            {'value': option} for option in question['options']
                                        ],
                                    }
                                }
                            }
                        },
                        'location': {'index': idx}
                    }
                }
                questions_body['requests'].append(question_item)

            forms_service.forms().batchUpdate(formId=form_id, body=questions_body).execute()

            # Get the form URL
            form_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
            
            return form_url

        except Exception as e:
            return f"Error creating form: {str(e)}"

    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async implementation of the tool - not needed for this tool."""
        raise NotImplementedError("GoogleFormCreator does not support async") 