# BASIC EMAIL NOTIFICATIONS USING AWS SES

import smtplib
import os
import json # required for dev only

# Get creds from enviroment variables if set otherwise untracked file (dev)
smtp_creds = {}
try:
    smtp_creds['user'] = os.getenv['SMTP_USER']
    smtp_creds['pass'] = os.getenv['SMTP_PASS']
except:
    print('Using local SMTP creds')
    with open('email_creds.txt') as creds:
        data = json.load(creds)
        smtp_creds['user'] = data['SMTP_USER']
        smtp_creds['pass'] = data['SMTP_PASS']

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