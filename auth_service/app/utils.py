import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_password_reset_email(to_email, reset_token):
    # Configuración del servidor SMTP
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Crear el mensaje de correo
    subject = "Recuperación de contraseña"
    reset_link = f"https://example.com/reset-password?token={reset_token}"
    body = f"""
    Hola,

    Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:
    {reset_link}

    Si no solicitaste este cambio, ignora este correo.

    Saludos,
    El equipo de soporte.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)

    # Enviar el correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")