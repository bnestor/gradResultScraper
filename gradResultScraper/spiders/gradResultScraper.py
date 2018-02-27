"""
Grad Result Scraper
gradResultScraper.py
Copyright 2018 Bret Nestor

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
  OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import print_function
import scrapy
import pandas as pd

# from __future__ import print_function
import httplib2
import os
import sys

from apiclient import errors, discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


# for creating the email message
import smtplib
from email import encoders
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None

phone="##########" # change this to your phone number #identification
email_addr='#####@gmail.com' # you can also opt to have it email you

schools=['MIT', 'Massachussetts Institute of Technology', 'stanford', 'eth', 'epfl', 'toronto', 'university  of washington']
programs=['PhD', 'doctorate']

schools=[school.lower() for school in schools]
programs=[program.lower() for program in programs]


SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'gmail email sender'



class gradResultScraper(scrapy.Spider):
    name = "gradResultScraper" # this is the name of the scraper
    start_urls = [
    'http://thegradcafe.com/survey/index.php?q=computer+science&t=a&o=&pp=100'
    ]

    def start_requests(self):
        urls = [
        'http://thegradcafe.com/survey/index.php?q=computer+science&t=a&o=&pp=100'
        ]
        # urls = [
        # 'http://thegradcafe.com/survey/index.php?q=computer+science&t=a&o=&pp=100/'
        #     'http://quotes.toscrape.com/page/1/',
        #     'http://quotes.toscrape.com/page/2/',
        # ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        global phone
        global email_addr
        try:
            df=pd.read_pickle('recent_responses.pickle')
            df_len=len(df)
        except:
            df=pd.DataFrame(columns=['School', 'Program', 'Response_date','Response'])
            df_len=0


        for submission in response.xpath('//tr'):
            # print(submission)
            row=submission.xpath('td/text()').extract()
            place=row[0].lower()
            degree=row[1].lower()
            response_date=row[2]
            for school in schools:
                if school in place:
                    for program in programs:
                        if program in degree:
                            # scrape the span tag
                            result=submission.xpath('td/span/text()').extract_first()

                            new_df=pd.DataFrame(data=[[place, degree,response_date, result]], columns=['School','Program', 'Response_date', 'Response'])
                            new=df[(df['School']==place)&(df['Program']==degree)&(df['Response_date']==response_date)&(df['Response']==result)].empty
                            if new:
                                if result:
                                    send_message(email_addr, phone+'@txt.att.net', 'New Grad Cafe Results', "{},{},{},{}".format(place,  degree, response_date, result), 'message_plain')
                                    # sendAlert(place, degree, response_date, response)
                                    # send_message(service, user_id, message)
                            df=df.append(new_df)
        df=df.drop_duplicates()
        df.to_pickle('recent_responses.pickle')
        try:
            page = response.url.split("/")[-2]
        except:
            print(response)
        # filename = 'quotes-%s.html' % page
        filename='results.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

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
        try:
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:
                credentials = tools.run(flow, store)
        except: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials





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
    service=discovery.build('gmail', 'v1', http=http, cache_discovery=False)
    message_to_send=create_message(sender, to, subject, message_HTML, message_plain)
    send_message_internal(service, "me", message_to_send)

def send_message_internal(service,user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
