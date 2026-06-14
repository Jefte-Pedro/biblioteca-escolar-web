import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings


# ──────────────────────────────────────────
# E-MAIL (Gmail via SMTP)
# ──────────────────────────────────────────

def enviar_codigo_verificacao(endereco, codigo):
    assunto = "Seu código de acesso — Biblioteca"
    mensagem = (
        f"Olá!\n\n"
        f"Seu código de verificação para acessar a Biblioteca da EREM Dr. Jaime Monteiro é:\n\n"
        f"🔑  {codigo}\n\n"
        f"Este código é válido por 10 minutos.\n"
        f"Se você não solicitou este código, ignore este e-mail."
    )
    return enviar_email(endereco, assunto, mensagem)


def enviar_aviso_atraso(endereco, nome, titulo_livro, dias_atraso):
    assunto = "⚠️ Livro com devolução em atraso — Biblioteca"
    mensagem = (
        f"Olá, {nome}!\n\n"
        f"O livro \"{titulo_livro}\" está com {dias_atraso} dia(s) de atraso.\n\n"
        f"Por favor, procure a bibliotecária para devolvê-lo ou renová-lo.\n\n"
        f"Evite bloqueios na sua conta!"
    )
    return enviar_email(endereco, assunto, mensagem)


def enviar_aviso_prazo(endereco, nome, titulo_livro, dias_restantes):
    assunto = "📅 Seu livro vence em breve — Biblioteca"
    mensagem = (
        f"Olá, {nome}!\n\n"
        f"O livro \"{titulo_livro}\" deve ser devolvido em {dias_restantes} dia(s).\n\n"
        f"Se precisar de mais tempo, procure a bibliotecária para renovar."
    )
    return enviar_email(endereco, assunto, mensagem)


def enviar_email(endereco, assunto, mensagem):
    host_user = settings.EMAIL_HOST_USER
    host_pass = settings.EMAIL_HOST_PASSWORD
    remetente = settings.DEFAULT_FROM_EMAIL

    if not host_user or not host_pass:
        print("⚠️  E-mail não configurado. Simulando envio.")
        print(f"Para: {endereco} | Assunto: {assunto}")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"]    = remetente
        msg["To"]      = endereco

        msg.attach(MIMEText(mensagem, "plain", "utf-8"))
        msg.attach(MIMEText(_template_html(assunto, mensagem), "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(host_user, host_pass)
            smtp.sendmail(host_user, endereco, msg.as_string())

        print(f"✅ E-mail enviado para {endereco}")
        return True

    except Exception as erro:
        print(f"❌ Erro ao enviar e-mail: {erro}")
        return False


def _template_html(assunto, mensagem):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background: #f4f7fb; padding: 32px;">
        <div style="max-width: 480px; margin: auto; background: #fff;
                    border-radius: 12px; padding: 32px; box-shadow: 0 2px 8px #0001;">

          <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 32px;">📚</span>
            <h2 style="color: #1e5aa8; margin: 8px 0 0;">Biblioteca</h2>
            <p style="color: #666; font-size: 13px; margin: 4px 0 0;">
              EREM Dr. Jaime Monteiro
            </p>
          </div>

          <hr style="border: none; border-top: 1px solid #e8eef6; margin: 0 0 24px;">

          <h3 style="color: #1e3a5f; margin: 0 0 16px;">{assunto}</h3>

          <p style="color: #333; font-size: 15px; line-height: 1.6; white-space: pre-line;">
            {mensagem}
          </p>

          <hr style="border: none; border-top: 1px solid #e8eef6; margin: 24px 0 16px;">

          <p style="color: #999; font-size: 12px; text-align: center;">
            Este é um e-mail automático, por favor não responda.
          </p>
        </div>
      </body>
    </html>
    """