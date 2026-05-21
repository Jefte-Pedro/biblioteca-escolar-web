from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from rest_framework import viewsets, filters
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from collections import defaultdict
import json

from django.views.decorators.csrf import csrf_exempt

from .models import Livro, Emprestimo, Reserva, Lista, Usuario, Exemplar, LivroLido
from .serializers import LivroSerializer


# ──────────────────────────────────────────
# AUTENTICAÇÃO
# ──────────────────────────────────────────

def pagina_login(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    return render(request, 'registration/login.html')


def verificar_matricula(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=405)
    data = json.loads(request.body)
    matricula = data.get('matricula', '').strip()
    try:
        usuario = Usuario.objects.get(matricula=matricula)
        return JsonResponse({
            'existe': True,
            'primeiro_acesso': usuario.primeiro_acesso,
            'nome': usuario.get_full_name() or usuario.username,
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'existe': False})


def fazer_login(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=405)
    data = json.loads(request.body)
    matricula = data.get('matricula', '').strip()
    senha = data.get('senha', '').strip()
    try:
        usuario = Usuario.objects.get(matricula=matricula)
    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'Matrícula não encontrada.'}, status=404)
    user = authenticate(request, username=usuario.username, password=senha)
    if user is not None:
        login(request, user)
        destino = '/biblioteca/emprestimos/' if user.is_bibliotecario else '/biblioteca/'
        return JsonResponse({'sucesso': True, 'redirect': destino})
    return JsonResponse({'erro': 'Senha incorreta.'}, status=401)


def primeiro_acesso(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método inválido'}, status=405)
    data = json.loads(request.body)
    matricula = data.get('matricula', '').strip()
    senha = data.get('senha', '').strip()
    email = data.get('email', '').strip()
    telefone = data.get('telefone', '').strip()
    try:
        usuario = Usuario.objects.get(matricula=matricula)
    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'Matrícula não encontrada.'}, status=404)
    if not usuario.primeiro_acesso:
        return JsonResponse({'erro': 'Essa conta já foi ativada.'}, status=400)
    if len(senha) < 8:
        return JsonResponse({'erro': 'Senha deve ter pelo menos 8 caracteres.'}, status=400)
    if not email and not telefone:
        return JsonResponse({'erro': 'Informe ao menos um canal de contato.'}, status=400)
    usuario.set_password(senha)
    if email:
        usuario.email = email
    if telefone:
        usuario.telefone = telefone
    usuario.primeiro_acesso = False
    usuario.save()
    user = authenticate(request, username=usuario.username, password=senha)
    login(request, user)
    return JsonResponse({'sucesso': True, 'redirect': '/biblioteca/'})


def fazer_logout(request):
    logout(request)
    return redirect('login')


def cadastro(request):
    matricula = request.GET.get('matricula', '').strip()
    if not matricula:
        return redirect('login')
    try:
        usuario = Usuario.objects.get(matricula=matricula)
    except Usuario.DoesNotExist:
        return redirect('login')
    if not usuario.primeiro_acesso:
        return redirect('login')
    iniciais = ''
    partes = usuario.get_full_name().split()
    if len(partes) >= 2:
        iniciais = partes[0][0].upper() + partes[-1][0].upper()
    elif partes:
        iniciais = partes[0][0].upper()
    return render(request, 'registration/cadastro.html', {
        'matricula': matricula,
        'nome': usuario.get_full_name(),
        'serie': usuario.serie or '',
        'iniciais': iniciais,
    })


def recuperar_senha(request):
    metodo = None
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        usuario = Usuario.objects.filter(matricula=matricula).first()
        if usuario:
            metodo = usuario.telefone or usuario.email
    return render(request, 'registration/recuperar_senha.html', {'metodo': metodo})


# ──────────────────────────────────────────
# PÁGINAS PRINCIPAIS
# ──────────────────────────────────────────

def inicio(request):
    from datetime import date as d_
    hoje = d_.today()
    usuario = request.user if request.user.is_authenticated else None

    CORES = ['#1e5aa8', '#7c3aed', '#059669', '#b45309', '#dc2626', '#0891b2', '#be185d']
    ICONES_LISTA = ['📚', '⭐', '🎯', '📖', '🔖', '💡', '🏆']
    ROTS = [-6, -2, 4]

    exemplares_emprestados_ids = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).values_list('exemplar_id', flat=True)

    livros_sem_disponivel = Exemplar.objects.filter(
        id_exemplar__in=exemplares_emprestados_ids
    ).values_list('livro_id', flat=True)

    sugestoes = Livro.objects.exclude(
        id_livro__in=livros_sem_disponivel
    ).order_by('?')[:10]

    listas = []
    emprestimos_recentes = []
    prazo_urgente = None

    if usuario:
        listas_qs = Lista.objects.filter(usuario=usuario).prefetch_related('livros')
        for l in listas_qs:
            livros = l.livros.all()[:3]
            l.livros_preview = [
                {
                    'titulo':     livro.titulo,
                    'capa_url':   livro.capa_url or '',
                    'cover_from': '#1e5aa8',
                    'cover_to':   '#0b1526',
                    'rot':        ROTS[i % len(ROTS)],
                }
                for i, livro in enumerate(livros)
            ]
            l.icone  = ICONES_LISTA[l.pk % len(ICONES_LISTA)]
            l.cor    = CORES[l.pk % len(CORES)]
            l.vis    = 'privada'
            l.criada = l.criada_em
            listas.append(l)

        qs = Emprestimo.objects.filter(
            usuario=usuario,
            data_devolucao_real__isnull=True,
        ).select_related('exemplar__livro').order_by('data_devolucao_prevista')[:3]

        for emp in qs:
            delta = (emp.data_devolucao_prevista - hoje).days
            emp.livro             = emp.exemplar.livro
            emp.dias_restantes    = max(delta, 0)
            emp.dias_usados       = max((hoje - emp.data_emprestimo).days, 0)
            emp.dias_total        = 15
            emp.percentual_usado  = min(int((emp.dias_usados / 15) * 100), 100)
            emp.urgente           = 0 <= delta <= 3 or delta < 0
            emp.renovacoes_usadas = 0
            emp.renovacoes_max    = 1
            emp.cor_avatar        = CORES[emp.pk % len(CORES)]
            emprestimos_recentes.append(emp)

        urgentes = [e for e in emprestimos_recentes if e.urgente]
        if urgentes:
            prazo_urgente = urgentes[0]
            prazo_urgente.data_devolucao = prazo_urgente.data_devolucao_prevista

    return render(request, 'biblioteca/inicio.html', {
        'sugestoes':            sugestoes,
        'listas':               listas,
        'emprestimos_recentes': emprestimos_recentes,
        'total_lidos':          0,
        'total_emprestados':    len(emprestimos_recentes),
        'dia_semana':           hoje.strftime('%A'),
        'data_hoje':            hoje.strftime('%d/%m/%Y'),
        'prazo_urgente':        prazo_urgente,
    })


def lista(request):
    listas_qs = Lista.objects.filter(usuario=request.user).prefetch_related('livros') \
        if request.user.is_authenticated else []

    listas = []
    for l in listas_qs:
        livros = l.livros.all()[:3]
        l.livros_preview = [
            {
                'titulo':     livro.titulo,
                'capa_url':   livro.capa_url or '',
                'cover_from': '#1e5aa8',
                'cover_to':   '#0b1526',
            }
            for livro in livros
        ]
        listas.append(l)

    return render(request, 'biblioteca/acervo.html', {'aba': 'lista', 'listas': listas})


@login_required
def detalhe_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    return render(request, 'biblioteca/detalhe_lista.html', {'lista': lista})


def acervo(request):
    q = request.GET.get('q', '')
    if q:
        livros = Livro.objects.filter(titulo__icontains=q) | Livro.objects.filter(autor__icontains=q)
    else:
        livros = Livro.objects.all()[:50]
    return render(request, 'biblioteca/acervo_busca.html', {'livros': livros, 'q': q})


@require_POST
def criar_lista(request):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    data = json.loads(request.body)
    nome = data.get('nome', '').strip()
    if not nome:
        return JsonResponse({'erro': 'Nome não pode ser vazio.'}, status=400)
    nova_lista = Lista.objects.create(usuario=request.user, nome=nome)
    return JsonResponse({'id': nova_lista.id, 'nome': nova_lista.nome, 'qtd_livros': 0})


@require_POST
def excluir_lista(request, lista_id):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    lista.delete()
    return JsonResponse({'status': 'ok'})


@require_POST
def renomear_lista(request, lista_id):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    data = json.loads(request.body)
    novo_nome = data.get('nome', '').strip()
    descricao = data.get('descricao', '').strip()
    if not novo_nome:
        return JsonResponse({'erro': 'Nome não pode ser vazio.'}, status=400)
    lista.nome = novo_nome
    lista.descricao = descricao if descricao else None
    lista.save()
    return JsonResponse({'id': lista.id, 'nome': lista.nome, 'descricao': lista.descricao})


@require_POST
def adicionar_livro_lista(request, lista_id):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    lista = get_object_or_404(Lista, id=lista_id, usuario=request.user)
    try:
        data = json.loads(request.body)
        livro_id = data.get('livro_id')
        livro = Livro.objects.filter(id_livro=livro_id).first()
        if not livro:
            livro = Livro.objects.filter(pk=livro_id).first()
        if not livro:
            return JsonResponse({'erro': f'Livro {livro_id} não encontrado.'}, status=404)
        lista.livros.add(livro)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@require_POST
def remover_livro_lista(request, lista_id):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)

    try:
        lista = Lista.objects.get(pk=lista_id)
    except Lista.DoesNotExist:
        return JsonResponse({'erro': 'Lista não encontrada.'}, status=404)

    if lista.usuario_id != request.user.pk:
        return JsonResponse({'erro': 'Sem permissão.'}, status=403)

    try:
        data = json.loads(request.body)
        livro_id = data.get('livro_id')
        livro = Livro.objects.filter(id_livro=livro_id).first()
        if not livro:
            livro = Livro.objects.filter(pk=livro_id).first()
        if not livro:
            return JsonResponse({'erro': f'Livro {livro_id} não encontrado.'}, status=404)
        lista.livros.remove(livro)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


def listas_do_usuario(request):
    if not request.user.is_authenticated:
        return JsonResponse({'listas': []})
    livro_id = request.GET.get('livro_id')
    listas = Lista.objects.filter(usuario=request.user).prefetch_related('livros')
    resultado = []
    for l in listas:
        tem_livro = False
        if livro_id:
            tem_livro = l.livros.filter(id_livro=livro_id).exists()
        resultado.append({
            'id':         l.id,
            'nome':       l.nome,
            'qtd_livros': l.livros.count(),
            'tem_livro':  tem_livro,
        })
    return JsonResponse({'listas': resultado})


# ──────────────────────────────────────────
# LIVROS LIDOS
# ──────────────────────────────────────────

@require_POST
@login_required
def marcar_livro_lido(request, livro_id):
    livro = get_object_or_404(Livro, id_livro=livro_id)
    # get_or_create garante que não duplica se o user clicar duas vezes
    _, criado = LivroLido.objects.get_or_create(usuario=request.user, livro=livro)
    return JsonResponse({'status': 'ok', 'criado': criado})


@require_POST
@login_required
def desmarcar_livro_lido(request, livro_id):
    livro = get_object_or_404(Livro, id_livro=livro_id)
    LivroLido.objects.filter(usuario=request.user, livro=livro).delete()
    return JsonResponse({'status': 'ok'})


def lidos(request):
    livros_lidos = []
    lidos_count = 0

    if request.user.is_authenticated:
        qs = LivroLido.objects.filter(
            usuario=request.user
        ).select_related('livro')

        lidos_count = qs.count()

        for registro in qs:
            registro.livro.autor_sobrenome = (
                registro.livro.autor.split()[-1] if registro.livro.autor else ''
            )
            # Cores de fallback para capa gradiente
            registro.livro.cover_from = '#1e5aa8'
            registro.livro.cover_to   = '#0b1526'
            livros_lidos.append(registro)

    return render(request, 'biblioteca/acervo.html', {
        'aba':          'lidos',
        'livros_lidos': livros_lidos,
        'lidos_count':  lidos_count,
    })


def reservados(request):
    return render(request, 'biblioteca/acervo.html', {'aba': 'reservados'})


def prazos(request):
    from datetime import date as d_
    hoje = d_.today()

    CORES = ['#1e5aa8', '#7c3aed', '#059669', '#b45309', '#dc2626', '#0891b2', '#be185d']

    emprestimos_qs = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao_real__isnull=True,
    ).select_related('exemplar__livro').order_by('data_devolucao_prevista') \
        if request.user.is_authenticated else Emprestimo.objects.none()

    total_ok = total_breve = total_atrasados = 0

    for emp in emprestimos_qs:
        delta = (emp.data_devolucao_prevista - hoje).days
        emp.vence_em_breve   = 0 <= delta <= 3
        emp.dias_restantes   = max(delta, 0)
        emp.dias_atraso      = abs(delta) if delta < 0 else 0
        emp.dias_usados      = max((hoje - emp.data_emprestimo).days, 0)
        emp.percentual_usado = min(int((emp.dias_usados / 15) * 100), 100)
        emp.cor_avatar       = CORES[emp.pk % len(CORES)]

        if emp.esta_atrasado():
            total_atrasados += 1
        elif emp.vence_em_breve:
            total_breve += 1
        else:
            total_ok += 1

    historico = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao_real__isnull=False,
    ).order_by('-data_devolucao_real') if request.user.is_authenticated else Emprestimo.objects.none()

    historico_count  = historico.count()
    ultimo_devolvido = historico.first().data_devolucao_real if historico_count > 0 else None

    return render(request, 'biblioteca/prazo.html', {
        'emprestimos':      emprestimos_qs,
        'total_ativos':     emprestimos_qs.count(),
        'total_ok':         total_ok,
        'total_breve':      total_breve,
        'total_atrasados':  total_atrasados,
        'historico_count':  historico_count,
        'ultimo_devolvido': ultimo_devolvido,
    })


def configuracoes(request):
    return render(request, 'biblioteca/configuracoes.html')


def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id_livro=livro_id)
    disponivel = livro.esta_disponivel()

    # Verifica se o usuário já marcou este livro como lido
    ja_lido = (
        request.user.is_authenticated and
        LivroLido.objects.filter(usuario=request.user, livro=livro).exists()
    )

    return render(request, 'biblioteca/detalhes_livro.html', {
        'livro':     livro,
        'disponivel': disponivel,
        'ja_lido':   ja_lido,
    })


def explorar(request):
    from django.db.models import Exists, OuterRef

    # Subquery: existe algum exemplar disponível para este livro?
    tem_disponivel = Exemplar.objects.filter(
        livro=OuterRef('pk'),
        status='disponivel'
    )

    livros = (
        Livro.objects
        .annotate(disponivel=Exists(tem_disponivel))
        .order_by('titulo')
    )

    # Categorias e prateleiras em 2 queries simples (sem iterar livros)
    categorias = (
        Livro.objects
        .exclude(categoria__isnull=True).exclude(categoria='')
        .values_list('categoria', flat=True)
        .distinct().order_by('categoria')
    )
    prateleiras = (
        Livro.objects
        .exclude(prateleira__isnull=True).exclude(prateleira='')
        .values_list('prateleira', flat=True)
        .distinct().order_by('prateleira')
    )

    return render(request, 'biblioteca/explorar.html', {
        'livros':       livros,
        'categorias':   categorias,
        'prateleiras':  prateleiras,
        'total_livros': livros.count(),
    })


# ──────────────────────────────────────────
# ADMIN / BIBLIOTECÁRIA
# ──────────────────────────────────────────

def cadastrar_livro(request):
    if request.method == 'GET':
        return render(request, 'biblioteca/cad-livro.html')

    data = json.loads(request.body)
    titulo      = data.get('titulo', '').strip()
    autor       = data.get('autor', '').strip()
    editora     = data.get('editora', '').strip()
    categoria   = data.get('categoria', '').strip()
    colecao     = data.get('colecao', '').strip()
    prateleira  = data.get('prateleira', '').strip()
    codigo_base = data.get('codigo_base', '').strip()
    quantidade  = int(data.get('quantidade', 1))
    observacoes = data.get('observacoes', '').strip()

    if not titulo or not prateleira or not quantidade:
        return JsonResponse({'erro': 'Preencha todos os campos obrigatórios.'}, status=400)

    livro = Livro.objects.create(
        titulo=titulo,
        autor=autor or None,
        editora=editora or None,
        categoria=categoria or None,
        colecao=colecao or None,
        prateleira=prateleira,
        codigo_base=codigo_base or None,
        quantidade=quantidade,
        observacoes=observacoes or None,
    )

    for i in range(1, quantidade + 1):
        codigo_completo = f"{codigo_base}/V{i}" if codigo_base else f"{livro.id_livro}/V{i}"
        Exemplar.objects.create(
            livro=livro,
            codigo_variante=f"V{i}",
            codigo_completo=codigo_completo,
            status='disponivel',
        )

    return JsonResponse({
        'sucesso':            True,
        'id':                 livro.id_livro,
        'titulo':             livro.titulo,
        'exemplares_criados': quantidade,
    })


def emprestimos(request):
    from datetime import date as d_
    hoje = d_.today()

    emprestimos_ativos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).select_related('exemplar__livro', 'usuario').order_by('data_devolucao_prevista')

    vencem_hoje     = emprestimos_ativos.filter(data_devolucao_prevista=hoje).count()
    atrasados       = sum(1 for e in emprestimos_ativos if e.esta_atrasado())
    devolvidos_hoje = Emprestimo.objects.filter(data_devolucao_real=hoje).count()

    CORES = ['#1e5aa8', '#7c3aed', '#059669', '#b45309', '#dc2626', '#0891b2']

    def enrich(emp, hoje, CORES):
        delta = (emp.data_devolucao_prevista - hoje).days
        emp.vence_hoje     = (delta == 0)
        emp.dias_restantes = max(delta, 0)
        emp.dias_atraso    = abs(delta) if delta < 0 else 0
        partes = emp.usuario.get_full_name().split() if emp.usuario else []
        if len(partes) >= 2:
            emp.iniciais_av = partes[0][0].upper() + partes[-1][0].upper()
        elif partes:
            emp.iniciais_av = partes[0][0].upper()
        else:
            emp.iniciais_av = '?'
        emp.cor_avatar           = CORES[emp.pk % len(CORES)]
        emp.nome_aluno           = emp.usuario.get_full_name() if emp.usuario else 'Desconhecido'
        emp.turma                = emp.usuario.serie if emp.usuario else ''
        emp.matricula_aluno      = emp.usuario.matricula if emp.usuario else ''
        emp.codigo_catalografico = emp.exemplar.codigo_completo if emp.exemplar else ''
        emp.livro_obj            = emp.exemplar.livro if emp.exemplar else None
        return emp

    emprestimos_enriched = [enrich(e, hoje, CORES) for e in emprestimos_ativos]

    # ── HISTÓRICO (devolvidos) ──────────────────────────────────
    historico_qs = Emprestimo.objects.filter(
        data_devolucao_real__isnull=False
    ).select_related('exemplar__livro', 'usuario').order_by('-data_devolucao_real')[:100]

    historico_enriched = []
    for emp in historico_qs:
        # Para devolvidos, delta é baseado na data prevista vs real
        delta = (emp.data_devolucao_prevista - emp.data_devolucao_real).days
        emp.vence_hoje     = False
        emp.dias_restantes = 0
        emp.dias_atraso    = 0
        emp.foi_devolvido_atrasado = emp.data_devolucao_real > emp.data_devolucao_prevista
        partes = emp.usuario.get_full_name().split() if emp.usuario else []
        if len(partes) >= 2:
            emp.iniciais_av = partes[0][0].upper() + partes[-1][0].upper()
        elif partes:
            emp.iniciais_av = partes[0][0].upper()
        else:
            emp.iniciais_av = '?'
        emp.cor_avatar           = CORES[emp.pk % len(CORES)]
        emp.nome_aluno           = emp.usuario.get_full_name() if emp.usuario else 'Desconhecido'
        emp.turma                = emp.usuario.serie if emp.usuario else ''
        emp.matricula_aluno      = emp.usuario.matricula if emp.usuario else ''
        emp.codigo_catalografico = emp.exemplar.codigo_completo if emp.exemplar else ''
        emp.livro_obj            = emp.exemplar.livro if emp.exemplar else None
        historico_enriched.append(emp)

    return render(request, 'biblioteca/emp-livro.html', {
        'emprestimos':     emprestimos_enriched,
        'historico':       historico_enriched,          # ← novo
        'vencem_hoje':     vencem_hoje,
        'atrasados':       atrasados,
        'devolvidos_hoje': devolvidos_hoje,
    })


@require_POST
def criar_emprestimo(request):
    data = json.loads(request.body)
    codigo_completo = data.get('codigo_completo', '').strip()
    nome_aluno      = data.get('nome_aluno', '').strip()
    turma           = data.get('turma', '').strip()
    usuario_id      = data.get('usuario_id')
    data_emp        = data.get('data_emprestimo', '').strip()
    data_dev        = data.get('data_devolucao_prevista', '').strip()

    if not all([codigo_completo, nome_aluno, data_emp]):
        return JsonResponse({'erro': 'Preencha todos os campos obrigatórios.'}, status=400)

    exemplar = Exemplar.objects.filter(codigo_completo=codigo_completo).first()
    if not exemplar:
        return JsonResponse({'erro': 'Exemplar não encontrado.'}, status=404)

    if exemplar.status != 'disponivel':
        return JsonResponse({'erro': 'Exemplar não está disponível.'}, status=400)

    usuario = None
    if usuario_id:
        usuario = Usuario.objects.filter(pk=usuario_id).first()

    if not usuario:
        from django.db.models import Q
        partes = nome_aluno.split()
        if partes:
            q = Q(first_name__icontains=partes[0])
            if len(partes) > 1:
                q &= Q(last_name__icontains=partes[-1])
            usuario = Usuario.objects.filter(q).first()

    if not usuario:
        return JsonResponse({'erro': f'Aluno "{nome_aluno}" não encontrado. Verifique o nome.'}, status=404)

    emprestimos_ativos = Emprestimo.objects.filter(
        usuario=usuario,
        data_devolucao_real__isnull=True
    ).count()
    if emprestimos_ativos >= 2:
        return JsonResponse({
            'erro': f'{usuario.get_full_name()} já possui 2 empréstimos ativos (limite máximo).'
        }, status=400)

    from datetime import date as d_
    data_emprestimo = d_.fromisoformat(data_emp)
    data_devolucao  = d_.fromisoformat(data_dev) if data_dev else data_emprestimo + timezone.timedelta(days=15)

    emp = Emprestimo.objects.create(
        exemplar=exemplar,
        usuario=usuario,
        data_emprestimo=data_emprestimo,
        data_devolucao_prevista=data_devolucao,
        observacoes=data.get('observacoes', '')
    )

    exemplar.status = 'emprestado'
    exemplar.save()

    return JsonResponse({
        'id':                      emp.pk,
        'titulo':                  exemplar.livro.titulo,
        'codigo_completo':         exemplar.codigo_completo,
        'usuario':                 usuario.get_full_name(),
        'turma':                   usuario.serie or turma,
        'data_emprestimo':         str(emp.data_emprestimo),
        'data_devolucao_prevista': str(emp.data_devolucao_prevista),
        'atrasado':                emp.esta_atrasado(),
        'observacoes':             emp.observacoes,
    })


@require_POST
def devolver_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    emprestimo.data_devolucao_real = timezone.now().date()
    emprestimo.save()
    emprestimo.exemplar.status = 'disponivel'
    emprestimo.exemplar.save()
    return JsonResponse({'sucesso': 'Livro devolvido com sucesso.'})


@require_POST
def renovar_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    hoje = timezone.now().date()
    if emprestimo.data_devolucao_prevista < hoje:
        return JsonResponse({'erro': 'Não é possível renovar um empréstimo atrasado.', 'status': 'Erro'}, status=400)
    emprestimo.data_devolucao_prevista += timezone.timedelta(days=15)
    emprestimo.save()
    return JsonResponse({
        'sucesso':   f'Renovado com sucesso. Nova data: {emprestimo.data_devolucao_prevista}',
        'nova_data': str(emprestimo.data_devolucao_prevista),
        'status':    'Sucesso'
    })

@require_POST
@staff_member_required
def excluir_livro(request, id_livro):
    livro = get_object_or_404(Livro, id_livro=id_livro)
    livro.delete()
    return JsonResponse({'sucesso': True})

@require_POST
def excluir_historico(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    
    # Só permite excluir registros já devolvidos
    if emprestimo.data_devolucao_real is None:
        return JsonResponse({
            'erro': 'Não é possível excluir um empréstimo ainda ativo.'
        }, status=400)
    
    emprestimo.delete()
    return JsonResponse({'sucesso': 'Registro excluído do histórico.'})

@require_POST
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if reserva.usuario != request.user:
        return JsonResponse({'erro': 'Sem permissão.'}, status=403)
    if reserva.status != 'pendente':
        return JsonResponse({'erro': 'Reserva não pode ser cancelada.'}, status=400)
    reserva.status = 'cancelada'
    reserva.save()
    return JsonResponse({'sucesso': 'Reserva cancelada com sucesso.'})


def alunos(request):
    CORES = ['#1e5aa8', '#7c3aed', '#059669', '#b45309', '#dc2626', '#0891b2', '#be185d']

    alunos_qs = Usuario.objects.filter(
        tipo_usuario='aluno'
    ).order_by('serie', 'first_name', 'last_name')

    for aluno in alunos_qs:
        partes = aluno.get_full_name().split()
        aluno.iniciais   = (partes[0][0] + partes[-1][0]).upper() if len(partes) >= 2 else partes[0][0].upper() if partes else '?'
        aluno.cor_avatar = CORES[aluno.pk % len(CORES)]

    alunos_por_turma = defaultdict(list)
    for aluno in alunos_qs:
        alunos_por_turma[aluno.serie or 'Sem turma'].append(aluno)

    turmas = sorted(alunos_por_turma.keys())

    return render(request, 'biblioteca/alunos.html', {
        'alunos_por_turma': dict(sorted(alunos_por_turma.items())),
        'turmas':           turmas,
        'total_alunos':     alunos_qs.count(),
        'total_turmas':     len(turmas),
    })


@require_POST
def importar_alunos(request):
    data = json.loads(request.body)
    alunos = data.get('alunos', [])
    criados = atualizados = 0

    for item in alunos:
        nome      = item.get('nome', '').strip()
        matricula = item.get('matricula', '').strip()
        turma     = item.get('turma', '').strip()

        if not nome or not matricula:
            continue

        partes     = nome.split()
        first_name = partes[0] if partes else ''
        last_name  = ' '.join(partes[1:]) if len(partes) > 1 else ''

        usuario, criado = Usuario.objects.update_or_create(
            matricula=matricula,
            defaults={
                'first_name':      first_name,
                'last_name':       last_name,
                'serie':           turma,
                'tipo_usuario':    'aluno',
                'username':        matricula,
                'primeiro_acesso': True,
            }
        )
        if criado:
            usuario.set_unusable_password()
            usuario.save()
            criados += 1
        else:
            atualizados += 1

    return JsonResponse({'criados': criados, 'atualizados': atualizados})



@require_POST
@staff_member_required
def editar_livro(request, livro_id):
    livro = get_object_or_404(Livro, id_livro=livro_id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'erro': 'JSON inválido.'}, status=400)

    campos_texto = ['titulo', 'autor', 'editora', 'isbn', 'codigo_base',
                    'categoria', 'colecao', 'prateleira', 'capa_url', 'sinopse']

    for campo in campos_texto:
        if campo in data:
            valor = data[campo].strip()
            setattr(livro, campo, valor if valor else None)

    if 'quantidade' in data:
        try:
            livro.quantidade = max(0, int(data['quantidade']))
        except (ValueError, TypeError):
            return JsonResponse({'erro': 'Quantidade inválida.'}, status=400)

    livro.save()
    return JsonResponse({'sucesso': True})


# ──────────────────────────────────────────
# BUSCA
# ──────────────────────────────────────────

def buscar_livro(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'livros': []})

    livros = Livro.objects.filter(titulo__icontains=q)[:8]
    resultado = []
    for livro in livros:
        exemplares_list = list(
            Exemplar.objects.filter(livro=livro, status='disponivel')
            .values('id_exemplar', 'codigo_completo', 'codigo_variante')
        )
        resultado.append({
            'id':                     livro.id_livro,
            'titulo':                 livro.titulo,
            'autor':                  livro.autor or '',
            'prateleira':             livro.prateleira or '',
            'capa_url':               livro.capa_url or '',
            'total_exemplares':       livro.quantidade,
            'exemplares_disponiveis': exemplares_list,
            'qtd_disponivel':         len(exemplares_list),
        })

    return JsonResponse({'livros': resultado})


def buscar_usuario(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'usuarios': []})

    from django.db.models import Q
    usuarios = Usuario.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q)
    ).exclude(tipo_usuario='bibliotecario')[:8]

    resultado = []
    for u in usuarios:
        emprestimos_ativos = Emprestimo.objects.filter(
            usuario=u, data_devolucao_real__isnull=True
        ).count()
        resultado.append({
            'id':                 u.pk,
            'nome':               u.get_full_name() or u.username,
            'matricula':          str(u.matricula) if u.matricula else '',
            'serie':              u.serie or '',
            'tipo':               u.tipo_usuario,
            'emprestimos_ativos': emprestimos_ativos,
            'pode_emprestar':     emprestimos_ativos < 2,
        })

    return JsonResponse({'usuarios': resultado})


# ──────────────────────────────────────────
# API REST
# ──────────────────────────────────────────

class LivroViewset(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'autor']


@require_POST
def deletar_lista(request, pk):
    lista = get_object_or_404(Lista, pk=pk)
    lista.delete()
    return JsonResponse({'sucesso': 'Lista deletada.'})