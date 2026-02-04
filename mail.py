import os
import json
import requests

from dotenv import load_dotenv
from oauth_helper import MicrosoftOAuthHelper

# Load environment variables from .env file
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# Initialize OAuth helper
oauth_helper = MicrosoftOAuthHelper()

# Microsoft Graph API endpoint
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0/me/sendMail"


def send_email(to_email: str, subject: str, body: str):
    """Send email using Microsoft Graph API with OAuth2."""
    # Get OAuth2 access token
    access_token: str = oauth_helper.get_access_token()
    
    # Create email message in Graph API format
    email_msg = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }
    
    # Send request to Graph API
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(GRAPH_API_ENDPOINT, headers=headers, json=email_msg)
    
    if response.status_code == 202:
        print(f"Email sent to {to_email}")
    else:
        raise Exception(f"Failed to send email: {response.status_code} - {response.text}")

def load_recipients(json_file: str = "recipients.json") -> dict:
    """Load recipients from JSON file."""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            recipients: dict = json.load(file)
            return recipients
    except FileNotFoundError:
        print(f"Error: {json_file} not found!")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file}: {str(e)}")
        exit(1)

if __name__ == "__main__":
    # Validate OAuth credentials
    if not SENDER_EMAIL:
        print("Error: SENDER_EMAIL environment variable must be set!")
        exit(1)
    
    if not oauth_helper.client_id:
        print("Error: Azure OAuth credentials missing!")
        print("\nYou need to set this in your .env file:")
        print("AZURE_CLIENT_ID=your_client_id")
        print("SENDER_EMAIL=your.email@hotmail.com")
        print("\nSee README.md for setup instructions.")
        exit(1)
    
    print(f"📧 Email Sender - OAuth2 Authentication")
    print(f"Sending from: {SENDER_EMAIL}\n")
    
    # Load recipients from JSON file
    recipients: dict = load_recipients()
    
    print(f"Total recipients: {len(recipients)}\n")
    
    # Iterate over all recipients and send them emails
    for name, email in recipients.items():
        subject: str = "Hello from Python"
        body: str = f"Hi {name},\n\nThis email was sent from my Python app 🚀\n\nBest regards"
        
        try:
            send_email(email, subject, body)
            print(f"✓ Sent email to {name} ({email})")
        except Exception as e:
            print(f"✗ Failed to send email to {name} ({email}): {str(e)}")
    
    print("\nDone!")
