import os
import re

# ──────────────────────────────────────────
# WHATSAPP (Evolution API — implementar depois)
# ──────────────────────────────────────────

def formatar_numero_whatsapp(numero):
    digitos = re.sub(r"\D", "", str(numero))
    if len(digitos) in (10, 11):
        digitos = f"55{digitos}"
    if not digitos.startswith("55") or len(digitos) not in (12, 13):
        raise ValueError("Número de WhatsApp inválido")
    return digitos


def enviar_whatsapp(numero, mensagem):
    # 🔧 Pendente: configurar Evolution API com a bibliotecária
    print("=================================")
    print(f"[WhatsApp SIMULADO] Para: {numero}")
    print(f"Mensagem: {mensagem}")
    print("=================================")
    return True