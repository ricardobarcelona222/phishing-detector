from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = int(os.getenv("MAIL_PORT")),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS = os.getenv("MAIL_TLS") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL") == "True",
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_registration_email(email: EmailStr):

    html = f"""
    <div style="font-family: Arial, sans-serif; background:#f4f6fb; padding:40px;">
        <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.08);">
            
            <h2 style="color:#1b3c74;"> Registro exitoso</h2>

            <p style="font-size:15px; color:#444;">
                Tu cuenta en <strong>Phishing Detector Dashboard</strong> fue creada correctamente.
            </p>

            <p style="font-size:15px; color:#444;">
                 Para poder acceder al sistema, tu cuenta debe ser aprobada por un administrador.
            </p>

            <div style="background:#f1f5ff; padding:15px; border-radius:8px; margin:20px 0;">
                <p style="margin:0; font-size:14px;">
                     Cuenta registrada: <strong>{email}</strong>
                </p>
            </div>

            <p style="font-size:14px; color:#666;">
                Recibirás otro correo cuando tu cuenta sea aprobada.
            </p>

            <hr style="margin:25px 0;">

            <p style="font-size:12px; color:#999;">
                © 2026 Phishing Detector Dashboard — Seguridad Inteligente
            </p>

        </div>
    </div>
    """

    message = MessageSchema(
        subject="Registro recibido - Pendiente de aprobación",
        recipients=[email],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_approval_email(email: EmailStr):

    html = f"""
    <div style="font-family: Arial, sans-serif; background:#f4f6fb; padding:40px;">
        <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.08);">
            
            <h2 style="color:#1b3c74;"> Cuenta aprobada</h2>

            <p style="font-size:15px; color:#444;">
                ¡Buenas noticias!
            </p>

            <p style="font-size:15px; color:#444;">
                Tu cuenta en <strong>Phishing Detector Dashboard</strong> ha sido aprobada por un administrador.
            </p>

            <div style="background:#e8f5e9; padding:15px; border-radius:8px; margin:20px 0;">
                <p style="margin:0; font-size:14px;">
                     Cuenta aprobada: <strong>{email}</strong>
                </p>
            </div>

            <p style="font-size:14px; color:#444;">
                Ya puedes iniciar sesión y comenzar a utilizar la plataforma.
            </p>

            <a href="http://localhost:8000"
               style="display:inline-block; margin-top:15px; padding:10px 18px; background:#2f6edb; color:white; text-decoration:none; border-radius:6px;">
               Iniciar sesión
            </a>

            <hr style="margin:25px 0;">

            <p style="font-size:12px; color:#999;">
                © 2026 Phishing Detector Dashboard — Seguridad Inteligente
            </p>

        </div>
    </div>
    """

    message = MessageSchema(
        subject="Tu cuenta ha sido aprobada 🎉",
        recipients=[email],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
