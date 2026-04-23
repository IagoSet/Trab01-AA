import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Notifier:
    """
    Responsável por enviar notificações de mudança de preço por e-mail.
    """
    
    def __init__(self, recipient_email=None):
        # Credenciais do "Bot" (Você pode preencher aqui ou usar variáveis de ambiente)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.bot_email = os.getenv("BOT_EMAIL", "jejzksnlabd@gmail.com")
        self.bot_password = os.getenv("BOT_PASSWORD", "udzlzmrtglttnncj")
        self.recipient_email = recipient_email

    async def send_notification(self, old_value, new_value):
        """
        Envia um e-mail informando a alteração de preço.
        """
        if not self.recipient_email:
            print("Erro: Nenhum e-mail de destino configurado.")
            return False

        try:
            # Configuração da mensagem
            msg = MIMEMultipart()
            msg['From'] = self.bot_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"ALERTA: O preço mudou! (R$ {old_value} -> R$ {new_value})"
            
            body = f"""
            Olá!
            
            Houve uma mudança no preço que você está monitorando:
            
            - Valor Anterior: R$ {old_value}
            - Novo Valor: R$ {new_value}
            
            O monitor continuará rodando para as próximas alterações.
            """
            msg.attach(MIMEText(body, 'plain'))

            # Conexão com o servidor e envio
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Protocolo de segurança
            server.login(self.bot_email, self.bot_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return False
