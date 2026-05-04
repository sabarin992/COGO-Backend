import smtplib
from email.mime.text import MIMEText
from app.core.config import settings
from datetime import datetime,timedelta

def send_otp_email(to_email: str, otp: str):
    sender_email = "sabarin992@gmail.com"
    sender_password = settings.APP_PASSWORD
    company_name = "COGO"
    expiry_minutes = 1
    expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
    formatted_time = expiry_time.strftime("%I:%M %p")

    subject = "Your OTP Code"
    body = f"""

    <html>
    <body style="margin:0; padding:0; background-color:#f6f9fc; font-family: 'Segoe UI', Arial, sans-serif;">
        
        <div style="max-width:600px; margin:40px auto; background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 8px 24px rgba(0,0,0,0.08);">

            <!-- 🔵 Header -->
            <div style="background: linear-gradient(90deg, #4f46e5, #3b82f6); padding:20px; text-align:center;">
                <h1 style="color:white; margin:0; letter-spacing:1px;">{company_name}</h1>
            </div>

            <!-- 📩 Body -->
            <div style="padding:30px; text-align:center;">

                <h2 style="margin-bottom:10px; color:#111827;">Verify Your Email</h2>

                <p style="color:#6b7280; font-size:15px;">
                    Enter the verification code below to continue with <b>{company_name}</b>.
                </p>

                <!-- 🔐 OTP BOX -->
                <div style="
                    display:inline-block;
                    margin:25px 0;
                    padding:15px 25px;
                    font-size:32px;
                    letter-spacing:8px;
                    font-weight:bold;
                    color:#111827;
                    background:#f3f4f6;
                    border-radius:8px;
                ">
                    {otp}
                </div>

                <!-- ⏳ Expiry -->
                <p style="color:#ef4444; font-weight:600; margin-top:10px;">
                    ⏳ Expires in {expiry_minutes} minutes (by {formatted_time})
                </p>

                <!-- ⚠️ Note -->
                <p style="font-size:14px; color:#6b7280; margin-top:20px;">
                    For your security, do not share this code with anyone.
                </p>

            </div>

            <!-- 🔻 Footer -->
            <div style="background:#f9fafb; padding:20px; text-align:center;">
                <p style="font-size:12px; color:#9ca3af; margin:0;">
                    © {company_name}. All rights reserved.
                </p>
                <p style="font-size:12px; color:#9ca3af; margin-top:5px;">
                    If you didn’t request this, you can safely ignore this email.
                </p>
            </div>

        </div>

    </body>
    </html>
    """

    msg = MIMEText(body,"html")
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