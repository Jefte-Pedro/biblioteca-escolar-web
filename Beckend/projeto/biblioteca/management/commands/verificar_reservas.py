"""
Comando para rodar 1x por dia (cron / Agendador de Tarefas do Windows):

    python manage.py verificar_reservas

Expira reservas 'aguardando_retirada' cujo prazo de 2 dias passou,
libera o exemplar pra estante geral e promove o próximo da fila (se houver).
"""

from django.core.management.base import BaseCommand
from biblioteca.reservas import expirar_reservas_vencidas


class Command(BaseCommand):
    help = 'Expira reservas vencidas (prazo de retirada de 2 dias) e promove a fila.'

    def handle(self, *args, **options):
        expirar_reservas_vencidas()
        self.stdout.write(self.style.SUCCESS('Verificação de reservas concluída com sucesso.'))