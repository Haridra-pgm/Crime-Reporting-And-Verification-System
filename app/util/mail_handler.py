import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail credentials
EMAIL = "haridra2005@gmail.com"
APP_PASSWORD = "qejs rylz pynk hgrx"

def send_email(to_email, subject, message):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        
        msg.attach(MIMEText(message, "plain"))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        # Send email
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")
        return True

    except Exception as e:
        print("Error sending email:", e)
        return False
