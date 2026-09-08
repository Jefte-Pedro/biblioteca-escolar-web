import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings 


# ──────────────────────────────────────────
# E-MAIL (Gmail via SMTP)
#
# Este arquivo cuida só do "COMO enviar": conexão SMTP, montagem do
# HTML/texto e o template visual. O "O QUE dizer" em cada notificação
# (prazos, atrasos, reservas etc.) fica centralizado em notifications.py,
# que é quem decide o assunto/mensagem de cada caso e chama enviar_email()
# diretamente. Isso evita ter o mesmo texto duplicado em dois lugares.
#
# Única exceção: o código de verificação (login/recuperação de senha),
# que não passa pelo sistema de notificações — por isso a função
# enviar_codigo_verificacao() continua aqui.
# ──────────────────────────────────────────

def enviar_codigo_verificacao(endereco, codigo):
    assunto = "Seu Código de Verificação para Acessar sua Conta"
    mensagem = (
        f"Olá!\n\n"
        f"Recebemos uma solicitação para acessar sua conta na Biblioteca da EREM Dr. Jaime Monteiro.\n\n"
        f"Utilize o código abaixo para concluir o acesso:\n\n"
        f"🔑  {codigo}\n\n"
        f"Este código é válido por 10 minutos e pode ser utilizado apenas uma vez.\n"
        f"Se você não solicitou este código, desconsidere este e-mail. Nenhuma ação adicional será necessária.\n\n"
        f"Atenciosamente,\n"
        f"Biblioteca da EREM Dr. Jaime Monteiro"
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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
            smtp.login(host_user, host_pass)
            # Usa o mesmo endereço do "From" também no envelope (evita
            # inconsistência entre remetente autenticado e remetente exibido).
            smtp.sendmail(remetente, endereco, msg.as_string())

        print(f"✅ E-mail enviado para {endereco}")
        return True

    except Exception as erro:
        print(f"❌ Erro ao enviar e-mail: {erro}")
        return False


def _template_html(assunto, mensagem):
    # ── Nota importante ──────────────────────────────────────────
    # NÃO usar a tag <hr> aqui. O Gmail interpreta <hr> como um
    # separador de "conteúdo citado" (igual ao que aparece antes de
    # texto encaminhado/respondido) e esconde tudo que vem depois
    # atrás de um botão "...", mesmo em e-mails novos sem histórico.
    # Por isso as linhas divisórias abaixo são feitas com <div> +
    # background-color, que têm o mesmo efeito visual sem disparar
    # esse comportamento de "clipping" do Gmail.
    divisor_estilo = (
        "height:1px;line-height:1px;font-size:1px;"
        "background-color:#e8eef6;border:none;"
    )
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

          <div style="{divisor_estilo} margin: 0 0 24px;">&nbsp;</div>

          <h3 style="color: #1e3a5f; margin: 0 0 16px;">{assunto}</h3>

          <p style="color: #333; font-size: 15px; line-height: 1.6; white-space: pre-line;">
            {mensagem}
          </p>

          <div style="{divisor_estilo} margin: 24px 0 16px;">&nbsp;</div>

          <p style="color: #999; font-size: 12px; text-align: center;">
            Este é um e-mail automático, por favor não responda.
          </p>
        </div>
      </body>
    </html>
    """