import requests
from celery import shared_task
from .models import Reserva
from django.utils import timezone
from datetime import timedelta

@shared_task
def verificar_prazos_reservas():
    amanha = timezone.now().date() + timedelta(days=1)
    reservas = Reserva.objects.filter(data_expiracao__date=amanha)

    url_api = "http://localhost:8000/message/sendText/SuaInstancia"
    headers = {
        "apikey":
            "SuaApiKeyDaEvolution", 
            "Content-Type": 
            "application/json"
               }
    
    for reserva in reservas:
        payload = {
            "number": f"55{reserva.usuario.telefone}",  # Adiciona o código do país (55 para Brasil)
            "message": f"Olá {reserva.usuario.nome}, sua reserva do livro '{reserva.livro.titulo}' está vencendo amanhã. Por favor, devolva o livro ou renove a reserva."
        }
        requests.post(url_api, json=payload, headers=headers)