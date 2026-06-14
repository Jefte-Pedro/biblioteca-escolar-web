from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None
notificacoes_enviadas = set()


def verificar_prazos():
    from .models import Emprestimo
    from .whatsapp import enviar_whatsapp
    from .gmail import enviar_aviso_atraso, enviar_aviso_prazo

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

        if dias == 2:
            tipo = "prazo"
        elif dias < 0:
            tipo = "atraso"
        else:
            continue

        chave = (e.pk, tipo, str(e.data_devolucao_prevista))
        if chave in notificacoes_enviadas:
            continue

        # WhatsApp
        if usuario.telefone:
            if tipo == "prazo":
                msg_zap = (
                    f"Olá {nome}!\n\n"
                    f"Seu empréstimo do livro *{titulo}* vence em 2 dias.\n"
                    f"Por favor, realize a devolução dentro do prazo."
                )
            else:
                msg_zap = (
                    f"Olá {nome}!\n\n"
                    f"Seu empréstimo do livro *{titulo}* está atrasado.\n"
                    f"Por favor, regularize a devolução."
                )
            enviar_whatsapp(usuario.telefone, msg_zap)

        # E-mail
        if usuario.email:
            if tipo == "prazo":
                enviar_aviso_prazo(usuario.email, nome, titulo, dias_restantes=2)
            else:
                enviar_aviso_atraso(usuario.email, nome, titulo, dias_atraso=abs(dias))

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