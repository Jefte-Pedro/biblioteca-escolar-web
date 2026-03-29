from django.core.management.base import BaseCommand
from biblioteca.models import Reserva
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Verifica as reservas vencendo em 1 dia e envia mensagem para o Whatsapp do usuário'

    def handle(self, *args, **kwargs):
        amanha =timezone.now().date() + timedelta(days=1)
        # Filtra as reservas que estão vencendo em 1 dia e ainda não foram notificadas
        reservas_quase_vencendo =Reserva.models.filter(data_expiracao__date=amanha, lembrete_enviado=False)

        for reserva in reservas_quase_vencendo:
            telefone = reserva.usuario.telefone
            mensagem = f"Olá {reserva.usuario.nome}, sua reserva do livro '{reserva.livro.titulo}' está vencendo amanhã. Por favor, devolva o livro ou renove a reserva."
            