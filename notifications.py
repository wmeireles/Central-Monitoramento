import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
from datetime import datetime

try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

class NotificationManager:
    def __init__(self):
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'email_user': os.getenv('EMAIL_USER'),
            'email_password': os.getenv('EMAIL_PASSWORD')
        }
        
        self.telegram_config = {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID')
        }
        
        self.twilio_config = {
            'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
            'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
            'whatsapp_from': os.getenv('TWILIO_WHATSAPP_FROM'),
            'whatsapp_to': os.getenv('TWILIO_WHATSAPP_TO')
        }
    
    def send_alert(self, site_result: Dict, alert_type: str = "down") -> List[str]:
        """Envia alertas por todos os canais configurados"""
        sent_via = []
        message = self._format_message(site_result, alert_type)
        
        # Tentar enviar por e-mail
        if self._send_email(message, site_result['name'], alert_type):
            sent_via.append('email')
        
        # Tentar enviar por Telegram
        if self._send_telegram(message):
            sent_via.append('telegram')
        
        # Tentar enviar por WhatsApp
        if self._send_whatsapp(message):
            sent_via.append('whatsapp')
        
        return sent_via
    
    def _format_message(self, site_result: Dict, alert_type: str) -> str:
        """Formata a mensagem de alerta"""
        timestamp = site_result['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
        
        if alert_type == "down":
            emoji = "🔴"
            status = "INDISPONÍVEL"
        elif alert_type == "recovered":
            emoji = "🟢"
            status = "RECUPERADO"
        elif alert_type == "ssl_warning":
            emoji = "⚠️"
            status = "AVISO SSL"
        else:
            emoji = "ℹ️"
            status = "INFORMAÇÃO"
        
        message = f"""
{emoji} ALERTA DE MONITORAMENTO

Site: {site_result['name']}
URL: {site_result['url']}
Status: {status}
Timestamp: {timestamp}

Detalhes:
- Status Code: {site_result.get('status_code', 'N/A')}
- Tempo de Resposta: {site_result.get('response_time', 'N/A')}ms
- SSL (dias restantes): {site_result.get('ssl_days_remaining', 'N/A')}
- Erro: {site_result.get('error_message', 'Nenhum')}
        """.strip()
        
        return message
    
    def _send_email(self, message: str, site_name: str, alert_type: str) -> bool:
        """Envia alerta por e-mail"""
        try:
            if not all([self.email_config['smtp_server'], self.email_config['email_user'], 
                       self.email_config['email_password']]):
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email_user']
            msg['To'] = self.email_config['email_user']  # Enviar para si mesmo
            msg['Subject'] = f"[MONITORAMENTO] {site_name} - {alert_type.upper()}"
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email_user'], self.email_config['email_password'])
                server.send_message(msg)
            
            logging.info(f"E-mail enviado para {site_name}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar e-mail: {e}")
            return False
    
    def _send_telegram(self, message: str) -> bool:
        """Envia alerta por Telegram"""
        try:
            if not TELEGRAM_AVAILABLE:
                return False
                
            if not all([self.telegram_config['bot_token'], self.telegram_config['chat_id']]):
                return False
            
            bot = Bot(token=self.telegram_config['bot_token'])
            bot.send_message(
                chat_id=self.telegram_config['chat_id'],
                text=message,
                parse_mode='HTML'
            )
            
            logging.info("Mensagem enviada via Telegram")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar Telegram: {e}")
            return False
    
    def _send_whatsapp(self, message: str) -> bool:
        """Envia alerta por WhatsApp via Twilio"""
        try:
            if not TWILIO_AVAILABLE:
                return False
                
            if not all([self.twilio_config['account_sid'], self.twilio_config['auth_token'],
                       self.twilio_config['whatsapp_from'], self.twilio_config['whatsapp_to']]):
                return False
            
            client = Client(self.twilio_config['account_sid'], self.twilio_config['auth_token'])
            
            client.messages.create(
                body=message,
                from_=self.twilio_config['whatsapp_from'],
                to=self.twilio_config['whatsapp_to']
            )
            
            logging.info("Mensagem enviada via WhatsApp")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar WhatsApp: {e}")
            return False