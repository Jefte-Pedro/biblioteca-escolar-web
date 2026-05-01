from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import Emprestimo
from whatsapp import enviar_whatsapp


agendador = None
notificacoes_enviadas = set()


def verificar_prazos():
    print("Verificando prazos...")

    db = SessionLocal()

    try:
        hoje = date.today()

        emprestimos = (
            db.query(Emprestimo)
            .options(joinedload(Emprestimo.aluno), joinedload(Emprestimo.exemplar))
            .all()
        )

        for e in emprestimos:

            if e.data_devolucao_real is not None:
                continue

            if e.data_devolucao_prevista is None:
                continue

            dias = (e.data_devolucao_prevista - hoje).days

            numero = e.aluno.telefone if e.aluno else None

            if not numero:
                print(f"Emprestimo {e.id_emprestimo} sem telefone cadastrado.")
                continue

            tipo = None
            mensagem = None

            if dias == 2:
                tipo = "prazo"
                mensagem = f"""
Ola {e.aluno.nome}!

Seu emprestimo de ID {e.id_emprestimo} vence em 2 dias.

Por favor, realize a devolucao dentro do prazo.
"""

            elif dias < 0:
                tipo = "atraso"
                mensagem = f"""
Ola {e.aluno.nome}!

Seu emprestimo de ID {e.id_emprestimo} esta atrasado.

Por favor, regularize a devolucao.
"""

            if not tipo:
                continue

            chave = (e.id_emprestimo, tipo, e.data_devolucao_prevista)

            if chave in notificacoes_enviadas:
                continue

            if enviar_whatsapp(numero, mensagem):
                notificacoes_enviadas.add(chave)

    except Exception as erro:
        print("Erro ao verificar prazos:")
        print(erro)

    finally:
        db.close()


def iniciar_agendador():
    global agendador

    if agendador and agendador.running:
        print("Agendador ja iniciado.")
        return agendador

    agendador = BackgroundScheduler()

    agendador.add_job(
        verificar_prazos,
        "interval",
        seconds=30,
        id="verificar_prazos",
        max_instances=1,
        coalesce=True,
        replace_existing=True
    )

    agendador.start()
    return agendador
