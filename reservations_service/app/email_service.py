import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.email_user)

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True):
        """Envía un email"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def send_reservation_confirmation(self, user_email: str, reservation_data: dict):
        """Envía email de confirmación de reserva"""
        subject = "Confirmación de Reserva - AgendaGol"
        
        body = f"""
        <html>
            <body>
                <h2>¡Reserva Confirmada!</h2>
                <p>Hola,</p>
                <p>Tu reserva ha sido confirmada exitosamente con los siguientes detalles:</p>
                
                <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; background-color: #f9f9f9;">
                    <h3>Detalles de la Reserva</h3>
                    <p><strong>Cancha:</strong> {reservation_data.get('field_name')}</p>
                    <p><strong>Ubicación:</strong> {reservation_data.get('field_location')}</p>
                    <p><strong>Fecha y Hora:</strong> {reservation_data.get('start_time')}</p>
                    <p><strong>Duración:</strong> {reservation_data.get('duration_hours')} hora(s)</p>
                    <p><strong>Precio Total:</strong> ${reservation_data.get('total_price')}</p>
                    <p><strong>ID de Reserva:</strong> #{reservation_data.get('id')}</p>
                </div>
                
                <p>Por favor, llega 10 minutos antes de tu horario reservado.</p>
                <p>Para cancelar tu reserva, puedes hacerlo desde nuestra plataforma.</p>
                
                <p>¡Gracias por elegir AgendaGol!</p>
                
                <hr>
                <small>Este es un email automático, por favor no responder.</small>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)

    def send_reservation_cancellation(self, user_email: str, reservation_data: dict, reason: str = None):
        """Envía email de cancelación de reserva"""
        subject = "Cancelación de Reserva - AgendaGol"
        
        reason_text = f"<p><strong>Motivo:</strong> {reason}</p>" if reason else ""
        
        body = f"""
        <html>
            <body>
                <h2>Reserva Cancelada</h2>
                <p>Hola,</p>
                <p>Tu reserva ha sido cancelada. Aquí están los detalles:</p>
                
                <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; background-color: #fff2f2;">
                    <h3>Detalles de la Reserva Cancelada</h3>
                    <p><strong>Cancha:</strong> {reservation_data.get('field_name')}</p>
                    <p><strong>Ubicación:</strong> {reservation_data.get('field_location')}</p>
                    <p><strong>Fecha y Hora:</strong> {reservation_data.get('start_time')}</p>
                    <p><strong>Duración:</strong> {reservation_data.get('duration_hours')} hora(s)</p>
                    <p><strong>ID de Reserva:</strong> #{reservation_data.get('id')}</p>
                    {reason_text}
                </div>
                
                <p>Puedes hacer una nueva reserva cuando gustes desde nuestra plataforma.</p>
                
                <p>¡Gracias por elegir AgendaGol!</p>
                
                <hr>
                <small>Este es un email automático, por favor no responder.</small>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
