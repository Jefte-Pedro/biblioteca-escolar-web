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


def _nome_exibicao(usuario):
    """Nome usado na saudação das mensagens ('Olá, {nome}!')."""
    return usuario.first_name or usuario.get_full_name() or usuario.username


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
        nome = _nome_exibicao(emp.usuario)
        data_str = emp.data_devolucao_prevista.strftime('%d/%m/%Y')

        if delta == 2:
            _notificar_prazo_unico(
                emp, 'prazo_2dias',
                f'"{titulo_livro}" vence em 2 dias',
                (
                    f'Olá, {nome}!\n\n'
                    f'Este é um lembrete de que o prazo de devolução do livro:\n\n'
                    f'{titulo_livro}\n\n'
                    f'termina em 2 dias ({data_str}).\n\n'
                    f'Caso ainda precise do livro por mais tempo, procure a biblioteca para verificar a possibilidade de renovação do empréstimo antes do vencimento.\n\n'
                    f'Se a devolução ou renovação já foi realizada recentemente, desconsidere esta mensagem, pois a atualização do sistema pode levar algum tempo.\n\n'
                    f'Atenciosamente,\n'
                    f'Biblioteca da EREM Dr. Jaime Monteiro'
                ),
            )

        elif delta == 1:
            _notificar_prazo_unico(
                emp, 'prazo_amanha',
                f'"{titulo_livro}" vence amanhã',
                (
                    f'Olá, {nome}!\n\n'
                    f'Este é um lembrete de que o prazo de devolução do livro:\n\n'
                    f'{titulo_livro}\n\n'
                    f'termina amanhã ({data_str}).\n\n'
                    f'Caso ainda precise do livro por mais tempo, procure a biblioteca para verificar a possibilidade de renovação do empréstimo antes do vencimento.\n\n'
                    f'Se a devolução já foi realizada recentemente, desconsidere esta mensagem, pois a atualização do sistema pode levar algum tempo.\n\n'
                    f'Atenciosamente,\n'
                    f'Biblioteca da EREM Dr. Jaime Monteiro'
                ),
            )

        elif delta == 0:
            _notificar_prazo_unico(
                emp, 'prazo_hoje',
                f'"{titulo_livro}" vence hoje',
                (
                    f'Olá, {nome}!\n\n'
                    f'Este é um lembrete de que o prazo de devolução do livro:\n\n'
                    f'{titulo_livro}\n\n'
                    f'termina hoje ({data_str}).\n\n'
                    f'Pedimos, por gentileza, que realize a devolução do exemplar ou procure a biblioteca para verificar a possibilidade de renovação do empréstimo.\n\n'
                    f'Se a devolução já foi realizada recentemente, desconsidere esta mensagem, pois a atualização do sistema pode levar algum tempo.\n\n'
                    f'Atenciosamente,\n'
                    f'Biblioteca da EREM Dr. Jaime Monteiro'
                ),
            )

        elif delta < 0:
            dias_atraso = abs(delta)
            _notificar_prazo_unico(
                emp, 'atraso',
                f'"{titulo_livro}" está com devolução em atraso',
                (
                    f'Olá, {nome}!\n\n'
                    f'Identificamos que o livro:\n\n'
                    f'{titulo_livro}\n\n'
                    f'está com {dias_atraso} dia{"s" if dias_atraso != 1 else ""} de atraso na devolução.\n\n'
                    f'Pedimos, por gentileza, que procure a biblioteca para realizar a devolução ou, caso seja possível, solicitar a renovação do empréstimo.\n\n'
                    f'Caso o livro já tenha sido devolvido recentemente, desconsidere este e-mail. Em algumas situações, pode haver um intervalo entre a devolução do material e a atualização do sistema pela equipe da biblioteca.\n\n'
                    f'Em caso de dúvidas, entre em contato com a bibliotecária.\n\n'
                    f'Atenciosamente,\n'
                    f'Biblioteca da EREM Dr. Jaime Monteiro'
                ),
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
    
# ──────────────────────────────────────────
# RESERVAS
# ──────────────────────────────────────────

def notificar_reserva_pendente(reserva):
    aluno = reserva.usuario.get_full_name() or reserva.usuario.username
    data_str = reserva.data_reserva.strftime('%d/%m/%Y')
    notificar_bibliotecarios(
        tipo='reserva_pendente',
        titulo=f'Nova solicitação de reserva: "{reserva.livro.titulo}"',
        mensagem=(
            f'O aluno {aluno} solicitou a reserva do livro "{reserva.livro.titulo}" '
            f'em {data_str}. Verifique a disponibilidade do exemplar e confirme ou recuse a solicitação.'
        ),
        requer_acao=True,
        reserva=reserva,
    )


def notificar_reserva_aceita(reserva):
    criar_notificacao(
        destinatario=reserva.usuario,
        tipo='reserva_aceita',
        titulo=f'Reserva confirmada: "{reserva.livro.titulo}"',
        mensagem=(
            f'Sua solicitação de reserva para "{reserva.livro.titulo}" foi aprovada com sucesso. '
            f'Assim que o exemplar estiver disponível para retirada, você receberá uma nova notificação.'
        ),
        reserva=reserva,
    )


def notificar_reserva_recusada(reserva):
    criar_notificacao(
        destinatario=reserva.usuario,
        tipo='reserva_recusada',
        titulo=f'Reserva não aprovada: "{reserva.livro.titulo}"',
        mensagem=(
            f'No momento, não foi possível aprovar sua reserva para "{reserva.livro.titulo}". '
            f'Caso ainda tenha interesse, acompanhe a disponibilidade do livro no acervo e tente realizar uma nova solicitação futuramente.'
        ),
        reserva=reserva,
    )


def notificar_fila_posicao(reserva):
    criar_notificacao(
        destinatario=reserva.usuario,
        tipo='fila_posicao',
        titulo=f'Você entrou na fila de espera: "{reserva.livro.titulo}"',
        mensagem=(
            f'O livro "{reserva.livro.titulo}" já possui reservas realizadas anteriormente. '
            f'Você ocupa a posição {reserva.posicao_fila} na fila de espera. '
            f'Assim que houver disponibilidade, você será notificado automaticamente.'
        ),
        reserva=reserva,
    )


def notificar_devolucao_com_reserva(emprestimo, reserva):
    notificar_bibliotecarios(
        tipo='devolucao_com_reserva',
        titulo=f'Livro devolvido com reserva pendente: "{reserva.livro.titulo}"',
        mensagem=(
            f'O livro "{reserva.livro.titulo}" foi devolvido e existe uma reserva ativa para '
            f'{reserva.usuario.get_full_name() or reserva.usuario.username}. '
            f'Confirme a disponibilidade do exemplar para que o aluno seja notificado.'
        ),
        requer_acao=True,
        reserva=reserva,
        emprestimo=emprestimo,
    )


def notificar_reserva_disponivel(reserva):
    criar_notificacao(
        destinatario=reserva.usuario,
        tipo='reserva_disponivel',
        titulo=f'Livro disponível para retirada: "{reserva.livro.titulo}"',
        mensagem=(
            f'O livro "{reserva.livro.titulo}" já está disponível para retirada na biblioteca. '
            f'O exemplar ficará reservado até {reserva.data_expiracao.strftime("%d/%m/%Y")}. '
            f'Após essa data, a reserva será cancelada automaticamente e o livro voltará a ficar disponível.'
        ),
        reserva=reserva,
    )


def notificar_reserva_expirada(reserva):
    criar_notificacao(
        destinatario=reserva.usuario,
        tipo='reserva_expirada',
        titulo=f'Reserva expirada: "{reserva.livro.titulo}"',
        mensagem=(
            f'O prazo para retirada do livro "{reserva.livro.titulo}" foi encerrado e a reserva expirou. '
            f'O exemplar voltou a ficar disponível para empréstimo. '
            f'Caso ainda tenha interesse, você poderá realizar uma nova reserva.'
        ),
        reserva=reserva,
    )