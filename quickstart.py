from __future__ import print_function
import httplib2
import os
import sys

from apiclient import errors, discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import smtplib
from email import encoders
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

phone="##########"
email_addr="####@gmail.com"

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
# SCOPES = ['https://www.googleapis.com/auth/gmail.send',
#             'https://www.googleapis.com/auth/gmail.readonly']
SCOPES='https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gmail email sender'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# def compat_urlsafe_b64encode(v):
#     """A urlsafe ba64encode which is compatible with Python 2 and 3.
#     Args:
#       v: A string to encode.
#     Returns:
#       The encoded string.
#     """
#     if sys.version_info[0] >= 3:  # pragma: NO COVER
#         return base64.urlsafe_b64encode(v.encode('UTF-8')).decode('ascii')
#     else:
#         return base64.urlsafe_b64encode(v)

def create_message(sender, to, subject, message_HTML, message_plain):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  # message = MIMEText(message_text)
  message=MIMEMultipart('alternative')
  message['To'] = to
  message['From'] = sender
  message['Subject'] = subject
  message.attach(MIMEText(message_plain, 'plain'))
  message.attach(MIMEText(message_HTML, 'html'))
  raw=base64.urlsafe_b64encode(message.as_bytes())
  raw=raw.decode()
  return {'raw': raw}
  # return {'raw': base64.urlsafe_b64encode(message.as_string())}
  # return {'raw': encoders.encode_base64(message)}
  # return {'raw': compat_urlsafe_b64encode(message)}

def send_message(sender, to, subject, message_HTML, message_plain):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    credentials=get_credentials()
    http=credentials.authorize(httplib2.Http())
    service=discovery.build('gmail', 'v1', http=http)
    message_to_send=create_message(sender, to, subject, message_HTML, message_plain)
    send_message_internal(service, "me", message_to_send)

def send_message_internal(service,user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    send_message(email_addr, phone+'@txt.att.net', 'test subj','', 'test')



if __name__ == '__main__':
    main()
