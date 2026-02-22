import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()  # ⭐ ESTA LINEA FALTABA

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_reset_email(to_email: str, token: str):

    print("EMAIL_USER:", EMAIL_USER)   # DEBUG
    print("EMAIL_PASSWORD:", EMAIL_PASSWORD)  # DEBUG
    print("Enviando correo a:", to_email)

    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}"

    subject = "Recuperar contraseña - Phishing Detector"

    body = f"""
Hola,

Haz clic en el siguiente enlace para cambiar tu contraseña:

{reset_link}
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
