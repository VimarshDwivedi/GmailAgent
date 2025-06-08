import os
import base64
import pickle
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_latest_unread_email(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread', maxResults=1).execute()
    messages = results.get('messages', [])
    if not messages:
        return None, None, None, None

    msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    headers = msg['payload']['headers']
    subject = sender = ''
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
        elif header['name'] == 'Subject':
            subject = header['value']

    # Try to extract email body (handle multipart)
    body = None
    payload = msg['payload']

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    else:
        if 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    if body is None:
        body = "[No readable content]"

    thread_id = msg.get('threadId')

    return sender, subject, body, thread_id


def send_email_reply(service, to_email, subject, message_text, thread_id=None):
    try:
        message = MIMEText(message_text)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}"
        if thread_id:
            message['In-Reply-To'] = thread_id
            message['References'] = thread_id

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {
            'raw': raw_message,
        }
        if thread_id:
            body['threadId'] = thread_id

        sent_message = service.users().messages().send(userId='me', body=body).execute()
        print(f"Message sent: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        print(f'An error occurred: {error}')
        raise error
