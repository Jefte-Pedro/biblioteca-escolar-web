"""
Módulo central do sistema de notificações.
Toda notificação do sistema (reservas, prazos, etc.) passa por aqui —
isso garante que TODA notificação some no sininho E no e-mail do usuário,
sem duplicar essa lógica em cada view.

O envio de e-mail usa o gmail.py que você já tem (SMTP + template HTML).
"""

from django.utils import timezone
from .gmail import enviar_email


# ──────────────────────────────────────────
# CRIAÇÃO DE NOTIFICAÇÃO (uso geral)
# ──────────────────────────────────────────

def criar_notificacao(destinatario, tipo, titulo, mensagem,
                       requer_acao=False, reserva=None, emprestimo=None,
                       enviar_email_flag=True):
    """
    Cria uma notificação no banco (aparece no sininho) e, se o usuário tiver
    e-mail cadastrado, também envia por e-mail usando o gmail.py existente.

    Uso típico:
        criar_notificacao(
            destinatario=aluno,
            tipo='prazo_hoje',
            titulo='Seu livro vence hoje',
            mensagem='O livro "Dom Casmurro" vence hoje...',
        )
    """
    from .models import Notificacao  # import local pra evitar import circular

    notif = Notificacao.objects.create(
        destinatario=destinatario,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        requer_acao=requer_acao,
        reserva=reserva,
        emprestimo=emprestimo,
    )

    if enviar_email_flag and destinatario.email:
        try:
            sucesso = enviar_email(destinatario.email, titulo, mensagem)
            notif.enviado_email = bool(sucesso)
            notif.save(update_fields=['enviado_email'])
        except Exception:
            # Nunca deixa o fluxo principal (ex: devolver um livro) quebrar
            # só porque o e-mail falhou.
            pass

    return notif


def notificar_bibliotecarios(tipo, titulo, mensagem, requer_acao=False,
                              reserva=None, emprestimo=None, enviar_email_flag=False):
    """
    Manda a mesma notificação para TODAS as contas com tipo_usuario='bibliotecario'.
    Útil para avisos como "reserva pendente" ou "devolução com reserva".
    Por padrão NÃO manda e-mail pra bibliotecária (só sininho) — ajuste se quiser.
    """
    from .models import Usuario

    bibliotecarios = Usuario.objects.filter(tipo_usuario='bibliotecario')
    return [
        criar_notificacao(
            destinatario=b, tipo=tipo, titulo=titulo, mensagem=mensagem,
            requer_acao=requer_acao, reserva=reserva, emprestimo=emprestimo,
            enviar_email_flag=enviar_email_flag,
        )
        for b in bibliotecarios
    ]


# ──────────────────────────────────────────
# VERIFICAÇÃO DE PRAZOS (rodar 1x/dia via cron)
# ──────────────────────────────────────────

def verificar_prazos():
    """
    Varre todos os empréstimos ativos e cria notificações de prazo:
    - 2 dias antes de vencer
    - 1 dia antes (amanhã)
    - no dia em que vence
    - todo dia em atraso (repete diariamente até devolver)

    Chamada pelo management command `verificar_prazos`.
    """
    from .models import Emprestimo

    hoje = timezone.now().date()

    ativos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).select_related('usuario', 'exemplar__livro')

    for emp in ativos:
        if not emp.usuario or not emp.data_devolucao_prevista:
            continue

        delta = (emp.data_devolucao_prevista - hoje).days
        titulo_livro = emp.exemplar.livro.titulo if emp.exemplar and emp.exemplar.livro else 'seu livro'

        if delta == 2:
            _notificar_prazo_unico(
                emp, 'prazo_2dias',
                f'"{titulo_livro}" vence em 2 dias',
                f'O livro "{titulo_livro}" está prestes a acabar o prazo em 2 dias '
                f'({emp.data_devolucao_prevista.strftime("%d/%m/%Y")}). '
                f'Não esqueça de devolver ou pedir renovação na biblioteca.',
            )
        elif delta == 1:
            _notificar_prazo_unico(
                emp, 'prazo_amanha',
                f'"{titulo_livro}" vence amanhã',
                f'O prazo do livro "{titulo_livro}" acaba amanhã '
                f'({emp.data_devolucao_prevista.strftime("%d/%m/%Y")}). '
                f'Procure a bibliotecária para renovar ou devolver seu livro.',
            )
        elif delta == 0:
            _notificar_prazo_unico(
                emp, 'prazo_hoje',
                f'"{titulo_livro}" vence hoje',
                f'O prazo do livro "{titulo_livro}" acaba hoje. '
                f'Favor procurar a bibliotecária para renovar ou devolver seu livro.',
            )
        elif delta < 0:
            dias_atraso = abs(delta)
            _notificar_prazo_unico(
                emp, 'atraso',
                f'"{titulo_livro}" está atrasado',
                f'O livro "{titulo_livro}" está atrasado há {dias_atraso} '
                f'dia{"s" if dias_atraso != 1 else ""}. Devolva o quanto antes '
                f'para regularizar sua situação na biblioteca.',
            )


def _notificar_prazo_unico(emp, tipo, titulo, mensagem):
    """Evita notificar o mesmo aluno/empréstimo/tipo mais de uma vez no mesmo dia."""
    from .models import Notificacao

    hoje = timezone.now().date()
    ja_existe = Notificacao.objects.filter(
        destinatario=emp.usuario,
        tipo=tipo,
        emprestimo=emp,
        criada_em__date=hoje,
    ).exists()
    if ja_existe:
        return

    criar_notificacao(
        destinatario=emp.usuario,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        emprestimo=emp,
    )