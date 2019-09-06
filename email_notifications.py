# BASIC EMAIL NOTIFICATIONS USING AWS SES

import smtplib
import os
from dotenv import load_dotenv

# Get creds from enviroment variables if set otherwise try env file (dev only)
smtp_creds = {}
smtp_creds['user'] = os.getenv('SMTP_USER')
smtp_creds['pass'] = os.getenv('SMTP_PASS')
if not smtp_creds['user'] or not smtp_creds['pass']:
    print('Using dev smtp creds')
    load_dotenv()
    smtp_creds['user'] = os.getenv('SMTP_USER')
    smtp_creds['pass'] = os.getenv('SMTP_PASS')

async def send_login_notification(user_email):
    # Setup smtp object
    smtp = smtplib.SMTP( 'email-smtp.eu-west-1.amazonaws.com' )
    smtp.starttls()
    smtp.login(smtp_creds['user'],smtp_creds['pass'])
    # Form message
    send = "the-mountain-logbook@daveb.me.uk"
    receive = "the-mountain-logbook@daveb.me.uk"
    headers = "from:the-mountain-logbook@daveb.me.uk\nsubject:The Mountain Logbook - User Login\n\n"
    body = "User %s just logged in." % user_email
    message = headers + body
    # Send email and close
    smtp.sendmail(send, receive, message)
    smtp.quit()