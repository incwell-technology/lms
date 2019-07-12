from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import smtplib
import socket
import urllib  
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from datetime import datetime, timedelta
from lms_user.tokens import password_reset_token
import jwt
from django.template.loader import get_template
from django.template import Context
import yaml

def send_email(request,user, text):
    try:
        credentials = yaml.load(open('credentials.yaml'))
        sender = credentials['lms_admin_email']
        password = credentials['lms_admin_password']
        msg = MIMEMultipart() 
        recipient = user.email 
        exp = str(datetime.now() + timedelta(hours=24))
        current_site = get_current_site(request) 
        try:
            token = str(jwt.encode({'email': recipient,'expires':exp},credentials['secret'], algorithm='HS256')).split("'")[1]
        except Exception:
            token = jwt.encode({'email': recipient,'expries':exp},credentials['secret'], algorithm='HS256')
        if text == 'Password Reset':
            msg['Subject'] = 'LMS | Password Reset'
            body = render_to_string('lms_user/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'protocol':request.scheme,
                'token': token
            })  
        elif text == 'Password Change':
            msg['Subject'] = 'LMS | Password Change'
            body = render_to_string('lms_user/password_changed.html', {
                'datetime': str(datetime.now()),
                'user': user.get_full_name()
            })
        elif text == 'Password Reset Mobile':
            msg['Subject'] = 'LMS | Password Reset'
            body = render_to_string('lms_user/password_reset_mobile_email.html', {
                'user': user,
                'domain': current_site.domain,
                'protocol':request.scheme,
                'token': token
            })  
        msg.attach(MIMEText(body,'plain'))
        urllib.request.urlopen('https://www.google.com/', timeout=1)
        server = smtplib.SMTP_SSL(credentials['smtp_server'], credentials['smtp_port'])
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        return True
    except (smtplib.SMTPException,socket.gaierror,Exception) as err:
        print(err)
        return False
        