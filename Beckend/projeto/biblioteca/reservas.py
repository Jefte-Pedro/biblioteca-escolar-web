"""
Lógica de negócio do sistema de Reservas.
As views só chamam essas funções e devolvem o JsonResponse — toda a regra
de fila, prazos e notificações fica centralizada aqui.
"""

from django.utils import timezone
from datetime import timedelta

from .notifications import (
    notificar_reserva_pendente,
    notificar_reserva_aceita,
    notificar_reserva_recusada,
    notificar_fila_posicao,
    notificar_devolucao_com_reserva,
    notificar_reserva_disponivel,
    notificar_reserva_expirada,
)

MAX_FILA = 3
DIAS_RETIRADA = 2

STATUS_ATIVOS = ['pendente', 'aceita', 'aguardando_retirada', 'fila']


class ReservaError(Exception):
    """Erro de regra de negócio — vira mensagem amigável pro usuário, não um 500."""
    pass


def criar_reserva(usuario, livro):
    from .models import Reserva

    if livro.esta_disponivel():
        raise ReservaError('Este livro tem exemplares disponíveis, não é necessário reservar.')

    ja_tem = Reserva.objects.filter(
        usuario=usuario, livro=livro, status__in=STATUS_ATIVOS,
    ).exists()
    if ja_tem:
        raise ReservaError('Você já tem uma reserva ativa para este livro.')

    reservas_ativas = Reserva.objects.filter(livro=livro, status__in=STATUS_ATIVOS)

    if not reservas_ativas.exists():
        reserva = Reserva.objects.create(usuario=usuario, livro=livro, status='pendente')
        notificar_reserva_pendente(reserva)
        return reserva, False

    fila_atual = reservas_ativas.filter(status='fila').count()
    if fila_atual >= MAX_FILA:
        raise ReservaError(
            f'Este livro já tem {MAX_FILA} alunos na fila de espera. '
            'Escolha outro livro ou tente novamente mais tarde.'
        )

    reserva = Reserva.objects.create(
        usuario=usuario, livro=livro, status='fila', posicao_fila=fila_atual + 1,
    )
    notificar_fila_posicao(reserva)
    return reserva, True


def aceitar_reserva(reserva):
    if reserva.status != 'pendente':
        raise ReservaError('Esta reserva não está mais pendente.')
    reserva.status = 'aceita'
    reserva.save(update_fields=['status'])
    notificar_reserva_aceita(reserva)
    return reserva


def recusar_reserva(reserva):
    if reserva.status != 'pendente':
        raise ReservaError('Esta reserva não está mais pendente.')
    reserva.status = 'recusada'
    reserva.save(update_fields=['status'])
    notificar_reserva_recusada(reserva)
    promover_proximo_da_fila(reserva.livro)
    return reserva


def promover_proximo_da_fila(livro):
    from .models import Reserva

    proxima = Reserva.objects.filter(
        livro=livro, status='fila'
    ).order_by('posicao_fila', 'data_reserva').first()

    if not proxima:
        return None

    proxima.status = 'pendente'
    proxima.posicao_fila = None
    proxima.save(update_fields=['status', 'posicao_fila'])

    restantes = Reserva.objects.filter(livro=livro, status='fila').order_by('posicao_fila', 'data_reserva')
    for i, r in enumerate(restantes, start=1):
        if r.posicao_fila != i:
            r.posicao_fila = i
            r.save(update_fields=['posicao_fila'])

    notificar_reserva_pendente(proxima)
    return proxima


def verificar_devolucao_com_reserva(emprestimo):
    """Chamada dentro de devolver_emprestimo(). Avisa a bibliotecária se o
    livro devolvido tem uma reserva 'aceita' esperando disponibilidade."""
    from .models import Reserva

    livro = emprestimo.exemplar.livro
    reserva = Reserva.objects.filter(livro=livro, status='aceita').order_by('data_reserva').first()
    if reserva:
        notificar_devolucao_com_reserva(emprestimo, reserva)
    return reserva


def confirmar_disponibilidade(reserva):
    if reserva.status != 'aceita':
        raise ReservaError('Esta reserva não está aguardando confirmação de disponibilidade.')
    reserva.status = 'aguardando_retirada'
    reserva.data_expiracao = timezone.now() + timedelta(days=DIAS_RETIRADA)
    reserva.data_notificacao = timezone.now()
    reserva.save(update_fields=['status', 'data_expiracao', 'data_notificacao'])
    notificar_reserva_disponivel(reserva)
    return reserva


def confirmar_retirada(reserva):
    from .models import Exemplar, Emprestimo

    if reserva.status != 'aguardando_retirada':
        raise ReservaError('Esta reserva não está aguardando retirada.')

    exemplar = Exemplar.objects.filter(livro=reserva.livro, status='reservado').first()
    if not exemplar:
        exemplar = Exemplar.objects.filter(livro=reserva.livro, status='disponivel').first()
    if not exemplar:
        raise ReservaError('Não há exemplar disponível deste livro no momento.')

    emprestimo = Emprestimo.objects.create(exemplar=exemplar, usuario=reserva.usuario)
    exemplar.status = 'emprestado'
    exemplar.save(update_fields=['status'])

    reserva.status = 'concluida'
    reserva.save(update_fields=['status'])
    return emprestimo


def cancelar_reserva_usuario(reserva, usuario):
    if reserva.usuario_id != usuario.pk:
        raise ReservaError('Sem permissão para cancelar esta reserva.')
    if reserva.status not in STATUS_ATIVOS:
        raise ReservaError('Esta reserva não pode mais ser cancelada.')

    era_cabeca_de_fila = reserva.status != 'fila'
    reserva.status = 'cancelada'
    reserva.save(update_fields=['status'])

    if era_cabeca_de_fila:
        promover_proximo_da_fila(reserva.livro)
    return reserva


def expirar_reservas_vencidas():
    """Chamada 1x/dia via management command `verificar_reservas`."""
    from .models import Reserva, Exemplar

    vencidas = Reserva.objects.filter(
        status='aguardando_retirada', data_expiracao__lt=timezone.now(),
    )
    for reserva in vencidas:
        exemplar = Exemplar.objects.filter(livro=reserva.livro, status='reservado').first()
        if exemplar:
            exemplar.status = 'disponivel'
            exemplar.save(update_fields=['status'])

        reserva.status = 'expirada'
        reserva.save(update_fields=['status'])
        notificar_reserva_expirada(reserva)
        promover_proximo_da_fila(reserva.livro)