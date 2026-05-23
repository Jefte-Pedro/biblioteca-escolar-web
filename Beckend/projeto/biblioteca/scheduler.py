from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None
notificacoes_enviadas = set()


def verificar_prazos():
    from .models import Emprestimo
    from .whatsapp import enviar_whatsapp, enviar_email

    print("Verificando prazos...")
    hoje = date.today()

    emprestimos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).select_related('usuario', 'exemplar__livro')

    for e in emprestimos:
        if not e.data_devolucao_prevista:
            continue

        dias = (e.data_devolucao_prevista - hoje).days
        usuario = e.usuario
        nome = usuario.first_name
        titulo = e.exemplar.livro.titulo if e.exemplar and e.exemplar.livro else "livro"

        tipo = None
        mensagem = None

        if dias == 2:
            tipo = "prazo"
            mensagem = (
                f"Olá {nome}!\n\n"
                f"Seu empréstimo do livro *{titulo}* vence em 2 dias.\n"
                f"Por favor, realize a devolução dentro do prazo."
            )
        elif dias < 0:
            tipo = "atraso"
            mensagem = (
                f"Olá {nome}!\n\n"
                f"Seu empréstimo do livro *{titulo}* está atrasado.\n"
                f"Por favor, regularize a devolução."
            )

        if not tipo:
            continue

        chave = (e.pk, tipo, str(e.data_devolucao_prevista))
        if chave in notificacoes_enviadas:
            continue

        enviado = False

        if usuario.telefone:
            enviar_whatsapp(usuario.telefone, mensagem)

        if usuario.email:
            enviar_email(usuario.email, "Aviso de empréstimo — Biblioteca", mensagem)

        notificacoes_enviadas.add(chave)

        if enviado:
            notificacoes_enviadas.add(chave)


def iniciar_scheduler():
    global scheduler

    if scheduler and scheduler.running:
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        verificar_prazos,
        'interval',
        minutes=30,
        id='verificar_prazos',
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler iniciado.")