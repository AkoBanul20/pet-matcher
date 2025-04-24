import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utilities.constants import EMAIL_PASSWORD


def send_email(to_email, subject, body):
    try:
        # Email configuration
        smtp_server = "smtp.hostinger.com"
        smtp_port = 587
        sender_email = "noreplynotification@qcacac.site"
        sender_password = EMAIL_PASSWORD

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        print(f"Email sent successfully to {to_email}")
    except BaseException as e:
        print(f"Failed to send email: {e}")