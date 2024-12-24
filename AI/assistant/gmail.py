import os.path
import base64
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import re

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_inbox_contents(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])
    if not messages:
        return
    
    data = []

    for msg in messages:
        msg = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

        headers = msg['payload']['headers']
        subject = None
        sender = None

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']

        body = ''
        if 'data' in msg['payload']['body']:
            body = msg['payload']['body']['data']
        elif 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if 'data' in part['body']:
                    body = part['body']['data']

        decoded_body = base64.urlsafe_b64decode(body.encode('UTF-8')).decode('UTF-8')

        data.append({"id":msg["id"], "sender":sender, "subject":subject, "body":decoded_body})
        # print(f'From: {sender}')
        # print(f'Subject: {subject}')
        # print(f'Body: {decoded_body[:100]}...')  # Show a snippet of the body
        # print('-----------------------------------')
    return data

def clean_email_body(html_content):
    # Parse the email body as HTML
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove <style> and <script> tags and their content
    for element in soup(['style', 'script']):
        element.decompose()

    # Remove all links (anchor tags)
    for a_tag in soup.find_all('a'):
        a_tag.decompose()

    # Remove all image tags
    for img_tag in soup.find_all('img'):
        img_tag.decompose()

    # Get the plain text, stripped of HTML tags
    clean_text = soup.get_text(separator="\n").strip()

    # Use regex to remove lines that don't contain any alphanumeric characters
    clean_text = re.sub(r'^[^a-zA-Z0-9]+$', '', clean_text, flags=re.MULTILINE)

    # Remove any leftover multiple newlines
    clean_text = re.sub(r'\n+', '\n', clean_text)
    
    return clean_text

def init():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    emails = {}
    data = get_inbox_contents(service)
    for message in data:
        emails[message["id"]] = parse_email(message)
    return service, emails

def parse_email(message):
  return { "sender": message["sender"], 
           "subject": message["subject"],
           "body":clean_email_body(message["body"])[0:1024] }

def get_new_emails(service, emails):
    new_emails = []
    data = get_inbox_contents(service)
    for message in data:
        if emails.keys().__contains__(message["id"]):
            continue

        parsed_email = parse_email(message)
        emails[message["id"]] = parsed_email
        new_emails.append(parsed_email)

    return emails, new_emails

def main():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    emails = {}
    is_first_loop = True

    print('Monitoring inbox for new emails...')

    while True:
      data = get_inbox_contents(service)
      for message in data:
        if emails.keys().__contains__(message["id"]):
          continue
        emails[message["id"]] = message
        if is_first_loop:
          continue

      is_first_loop = False
      time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    main()
