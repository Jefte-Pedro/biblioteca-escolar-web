"""
biblioteca/management/commands/verificar_prazos.py

Comando para rodar 1x por dia (cron / Agendador de Tarefas do Windows):

    python manage.py verificar_prazos

Ele varre todos os empréstimos ativos e cria notificações de prazo
(2 dias antes, amanhã, hoje, atrasado) — sem duplicar no mesmo dia.
"""

from django.core.management.base import BaseCommand
from biblioteca.notifications import verificar_prazos


class Command(BaseCommand):
    help = 'Verifica prazos de devolução de empréstimos e envia notificações (sininho + e-mail).'

    def handle(self, *args, **options):
        verificar_prazos()
        self.stdout.write(self.style.SUCCESS('Verificação de prazos concluída com sucesso.'))