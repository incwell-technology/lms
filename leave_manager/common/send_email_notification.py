import yaml
import smtplib
from email.mime.text import MIMEText


def send_email_notification(update_details):
    credentials = yaml.load(open('credentials.yaml'))

    sender = credentials['lms_admin_email']
    password = credentials['lms_admin_password']
    recipient = update_details['recipient_email']

    # Create message
    msg = MIMEText(update_details['email_body'])
    msg['Subject'] = update_details['email_subject']
    msg['From'] = sender
    msg['To'] = recipient

    try:
        # Create server object with SSL option
        server = smtplib.SMTP_SSL(credentials['smtp_server'], credentials['smtp_port'])
        # Perform operations via server
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        return True

    except Exception as e:
        print(e)
        return False
