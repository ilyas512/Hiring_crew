from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from src.config import settings
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/drive'
]

def authenticate_google():
    """Handles the complete Google OAuth2 authentication flow."""
    creds = None
    
    # Check if token.json exists
    if os.path.exists(settings.GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(settings.GOOGLE_TOKEN_PATH, SCOPES)

    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(settings.GOOGLE_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
    return creds

if __name__ == "__main__":
    print("Starting Google authentication process...")
    try:
        creds = authenticate_google()
        print("Authentication successful! Token saved to:", settings.GOOGLE_TOKEN_PATH)
    except Exception as e:
        print("Authentication failed:", str(e)) 