import os
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def formatar_numero_whatsapp(numero):
    digitos = re.sub(r"\D", "", str(numero))
    if len(digitos) in (10, 11):
        digitos = f"55{digitos}"
    if not digitos.startswith("55") or len(digitos) not in (12, 13):
        raise ValueError("Numero de WhatsApp invalido")
    return f"whatsapp:+{digitos}"


def enviar_whatsapp(numero, mensagem):
    try:
        destino = formatar_numero_whatsapp(numero)
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        remetente = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

        if account_sid and auth_token:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            client.messages.create(
                from_=f"whatsapp:{remetente}" if not remetente.startswith("whatsapp:") else remetente,
                to=destino,
                body=mensagem.strip()
            )
            print(f"Mensagem enviada para: {destino}")
            return True

        # Modo simulação
        print("Twilio nao configurado. Simulando envio.")
        print("=================================")
        print(f"Para: {destino}")
        print(f"Mensagem: {mensagem}")
        print("=================================")
        return True

    except Exception as erro:
        print(f"Erro ao enviar WhatsApp: {erro}")
        return False


def enviar_email(endereco, assunto, mensagem):
    # Placeholder — implementar com SMTP futuramente
    print("=================================")
    print(f"Email para: {endereco}")
    print(f"Assunto: {assunto}")
    print(f"Mensagem: {mensagem}")
    print("=================================")
    return True