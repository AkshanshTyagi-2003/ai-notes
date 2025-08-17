from dotenv import load_dotenv
load_dotenv()  # Must be at the top before accessing os.getenv

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import html
from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError, SMTPException

def send_email(subject: str, body: str, recipients: list):
    # Load SMTP configuration from environment variables
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP_USER and SMTP_PASS environment variables must be set.")

    # Escape HTML special characters
    escaped_body = html.escape(body)

    # Convert markdown-style headings and bullet points to basic HTML
    html_body = escaped_body
    html_body = html_body.replace("\n# ", "<h2>").replace("\n", "</h2><br>", 1)
    html_body = html_body.replace("\n- ", "<ul><li>").replace("\n", "</li></ul>", 1)
    html_body = html_body.replace("\n", "<br>")  # Replace remaining line breaks

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg['From'] = smtp_user
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject

    # Attach both plain text and HTML versions
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipients, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {', '.join(recipients)}")

    except SMTPRecipientsRefused as e:
        print(f"Error: Recipient refused - {e.recipients}")
        raise ValueError(f"One or more recipient emails are invalid: {e.recipients}") from e

    except SMTPAuthenticationError as e:
        print("Error: SMTP authentication failed. Check SMTP_USER and SMTP_PASS.")
        raise ValueError("SMTP authentication failed. Check your username and password.") from e

    except SMTPException as e:
        print(f"SMTP error occurred: {e}")
        raise RuntimeError(f"SMTP error occurred: {e}") from e

    except Exception as e:
        print(f"Unexpected error sending email: {e}")
        raise RuntimeError(f"Unexpected error sending email: {e}") from e
