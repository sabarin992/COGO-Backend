import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_otp_email(to_email: str, otp: str):
    sender_email = "sabarin992@gmail.com"
    sender_password = settings.APP_PASSWORD

    subject = "Your OTP Code"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("Email sending failed:", e)