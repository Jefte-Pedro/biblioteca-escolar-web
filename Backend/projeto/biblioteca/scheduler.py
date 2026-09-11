from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None


def executar_tarefas():
    """
    Executa as tarefas automáticas do sistema.

    As regras de negócio permanecem centralizadas nos respectivos módulos:
    - notifications.py → verificação de prazos e notificações
    - reservas.py → expiração de reservas vencidas
    """

    from .notifications import verificar_prazos
    from .reservas import expirar_reservas_vencidas

    print("Executando tarefas automáticas...")

    try:
        verificar_prazos()
        print("Verificação de prazos concluída.")
    except Exception as exc:
        print(f"Erro ao verificar prazos: {exc}")

    try:
        expirar_reservas_vencidas()
        print("Verificação de reservas concluída.")
    except Exception as exc:
        print(f"Erro ao verificar reservas: {exc}")


def iniciar_scheduler():
    global scheduler

    if scheduler and scheduler.running:
        return

    scheduler = BackgroundScheduler(timezone='America/Recife')

    scheduler.add_job(
        executar_tarefas,
        'cron',
        hour='8,20',
        id='executar_tarefas',
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    scheduler.start()
    print("Scheduler iniciado.")