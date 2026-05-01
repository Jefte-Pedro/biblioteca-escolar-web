from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from rest_framework import viewsets, filters
from datetime import date
import json

from .models import Livro, Emprestimo, Reserva, Lista, Usuario, Exemplar
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
    usuario = request.user if request.user.is_authenticated else None

    exemplares_emprestados_ids = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).values_list('exemplar_id', flat=True)

    livros_sem_disponivel = Exemplar.objects.filter(
        id_exemplar__in=exemplares_emprestados_ids
    ).values_list('livro_id', flat=True)

    sugestoes = Livro.objects.exclude(
        id_livro__in=livros_sem_disponivel
    ).order_by('?')[:10]

    listas = Lista.objects.filter(usuario=usuario) if usuario else []
    emprestimos_recentes = Emprestimo.objects.filter(
        usuario=usuario,
        data_devolucao_real__isnull=True
    )[:3] if usuario else []

    return render(request, 'biblioteca/inicio.html', {
        'sugestoes': sugestoes,
        'listas': listas,
        'emprestimos_recentes': emprestimos_recentes,
        'total_lidos': 0,
        'total_emprestados': emprestimos_recentes.count() if usuario else 0,
        'dia_semana': date.today().strftime('%A'),
        'data_hoje': date.today().strftime('%d/%m/%Y'),
        'prazo_urgente': None,
    })


def lista(request):
    listas = Lista.objects.filter(usuario=request.user) if request.user.is_authenticated else []
    return render(request, 'biblioteca/acervo.html', {'aba': 'lista', 'listas': listas})


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
        return JsonResponse({'erro': 'login_required', 'mensagem': 'Você precisa estar logado para criar listas.'}, status=401)
    data = json.loads(request.body)
    nome = data.get('nome', '').strip()
    if not nome:
        return JsonResponse({'erro': 'Nome não pode ser vazio.'}, status=400)
    nova_lista = Lista.objects.create(usuario=request.user, nome=nome)
    return JsonResponse({'id': nova_lista.id, 'nome': nova_lista.nome, 'qtd_livros': 0})


def lidos(request):
    return render(request, 'biblioteca/acervo.html', {'aba': 'lidos'})


def reservados(request):
    return render(request, 'biblioteca/acervo.html', {'aba': 'reservados'})


def prazos(request):
    emprestimos_usuario = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao_real__isnull=True
    ) if request.user.is_authenticated else []
    return render(request, 'biblioteca/prazo.html', {'emprestimos': emprestimos_usuario})


def configuracoes(request):
    return render(request, 'biblioteca/configuracoes.html')


def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id_livro=livro_id)
    disponivel = livro.esta_disponivel()
    return render(request, 'biblioteca/detalhes_livro.html', {'livro': livro, 'disponivel': disponivel})


# ──────────────────────────────────────────
# ADMIN / BIBLIOTECÁRIA
# ──────────────────────────────────────────

def cadastrar_livro(request):
    if request.method == 'GET':
        return render(request, 'biblioteca/cad-livro.html')

    # POST — salva no banco
    data = json.loads(request.body)

    titulo = data.get('titulo', '').strip()
    autor = data.get('autor', '').strip()
    editora = data.get('editora', '').strip()
    categoria = data.get('categoria', '').strip()
    colecao = data.get('colecao', '').strip()
    prateleira = data.get('prateleira', '').strip()
    codigo_base = data.get('codigo_base', '').strip()
    quantidade = int(data.get('quantidade', 1))
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

    # Cria os exemplares automaticamente
    for i in range(1, quantidade + 1):
        codigo_completo = f"{codigo_base}/V{i}" if codigo_base else f"{livro.id_livro}/V{i}"
        Exemplar.objects.create(
            livro=livro,
            codigo_variante=f"V{i}",
            codigo_completo=codigo_completo,
            status='disponivel',
        )

    return JsonResponse({
        'sucesso': True,
        'id': livro.id_livro,
        'titulo': livro.titulo,
        'exemplares_criados': quantidade,
    })


def emprestimos(request):
    emprestimos_ativos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).select_related('exemplar__livro', 'usuario')
    return render(request, 'biblioteca/emp-livro.html', {'emprestimos': emprestimos_ativos})


@require_POST
def criar_emprestimo(request):
    data = json.loads(request.body)
    codigo_completo = data.get('codigo_completo', '').strip()
    matricula = data.get('matricula', '').strip()
    data_emp = data.get('data_emprestimo', '').strip()
    data_dev = data.get('data_devolucao_prevista', '').strip()

    if not all([codigo_completo, matricula, data_emp]):
        return JsonResponse({'erro': 'Preencha todos os campos obrigatórios.'}, status=400)

    exemplar = Exemplar.objects.filter(codigo_completo=codigo_completo).first()
    if not exemplar:
        return JsonResponse({'erro': 'Exemplar não encontrado.'}, status=404)

    if exemplar.status != 'disponivel':
        return JsonResponse({'erro': 'Exemplar não está disponível.'}, status=400)

    try:
        usuario = Usuario.objects.get(matricula=matricula)
    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'Aluno não encontrado.'}, status=404)

    from datetime import date as d
    data_emprestimo = d.fromisoformat(data_emp)
    data_devolucao = d.fromisoformat(data_dev) if data_dev else data_emprestimo + timezone.timedelta(days=15)

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
        'id': emp.pk,
        'titulo': exemplar.livro.titulo,
        'codigo_completo': exemplar.codigo_completo,
        'usuario': usuario.get_full_name(),
        'data_emprestimo': str(emp.data_emprestimo),
        'data_devolucao_prevista': str(emp.data_devolucao_prevista),
        'atrasado': emp.esta_atrasado(),
        'observacoes': emp.observacoes,
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
        'sucesso': f'Renovado com sucesso. Nova data: {emprestimo.data_devolucao_prevista}',
        'nova_data': str(emprestimo.data_devolucao_prevista),
        'status': 'Sucesso'
    })


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


# ──────────────────────────────────────────
# API
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