from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Livro
from .serializers import LivroSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Emprestimo
from .models import Reserva
from django.utils import timezone
import json
from django.views.decorators.http import require_POST
from .models import Lista
from .models import Usuario



def inicio(request):
    return render(request, 'biblioteca/inicio.html')

def lista(request):
    usuario = Usuario.objects.first()
    listas = Lista.objects.filter(usuario=usuario) if usuario else []
    return render(request, 'biblioteca/acervo.html', {
        'aba': 'lista',
        'listas': listas
    })

@require_POST
def criar_lista(request):
    data = json.loads(request.body)
    nome = data.get('nome', '').strip()

    if not nome:
        return JsonResponse({'erro': 'Nome não pode ser vazio.'}, status=400)

    usuario = Usuario.objects.first()
    nova_lista = Lista.objects.create(usuario=usuario, nome=nome)

    return JsonResponse({
        'id': nova_lista.id,
        'nome': nova_lista.nome,
        'qtd_livros': 0
    })

def lidos(request):
    return render(request, 'biblioteca/acervo.html', { 'aba': 'lidos' })

def reservados(request):
    return render(request, 'biblioteca/acervo.html', { 'aba': 'reservados' })

def prazos(request):
    usuario = Usuario.objects.first()
    emprestimos_usuario = Emprestimo.objects.filter(
        usuario=usuario,
        data_devolucao_real__isnull=True
    ) if usuario else []
    return render(request, 'biblioteca/prazo.html', {
        'emprestimos': emprestimos_usuario
    })

def cadastrar_livro(request):
    return render(request, 'biblioteca/cad-livro.html')

def emprestimos(request):
    emprestimos_ativos = Emprestimo.objects.filter(data_devolucao_real__isnull=True)
    return render(request, 'biblioteca/emp-livro.html', {
        'emprestimos': emprestimos_ativos
    })

@require_POST
def criar_emprestimo(request):
    data = json.loads(request.body)

    titulo = data.get('titulo', '').strip()
    codigo = data.get('codigo_catalografico', '').strip()
    nome_aluno = data.get('nome_aluno', '').strip()
    turma = data.get('turma', '').strip()
    data_emp = data.get('data_emprestimo', '').strip()
    data_dev = data.get('data_devolucao_prevista', '').strip()

    if not all([titulo, codigo, nome_aluno, turma, data_emp]):
        return JsonResponse({'erro': 'Preencha todos os campos obrigatórios.'}, status=400)

    livro = Livro.objects.filter(titulo__icontains=titulo).first()
    if not livro:
        return JsonResponse({'erro': 'Livro não encontrado.'}, status=404)

    usuario = Usuario.objects.first()

    from datetime import date
    data_emprestimo = date.fromisoformat(data_emp)
    data_devolucao = date.fromisoformat(data_dev) if data_dev else None

    emp = Emprestimo.objects.create(
        livro=livro,
        usuario=usuario,
        codigo_catalografico=codigo,
        nome_aluno=nome_aluno,
        turma=turma,
        data_emprestimo=data_emprestimo,
        data_devolucao_prevista=data_devolucao,
        observacoes=data.get('observacoes', '')
    )

    return JsonResponse({
        'id': emp.pk,
        'titulo': livro.titulo,
        'codigo_catalografico': emp.codigo_catalografico,
        'nome_aluno': emp.nome_aluno,
        'turma': emp.turma,
        'data_emprestimo': str(emp.data_emprestimo),
        'data_devolucao_prevista': str(emp.data_devolucao_prevista),
        'atrasado': emp.esta_atrasado(),
        'foi_renovado': emp.foi_renovado,
        'observacoes': emp.observacoes,
    })

@require_POST
def devolver_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    emprestimo.data_devolucao_real = timezone.now().date()
    emprestimo.save()
    return JsonResponse({'sucesso': 'Livro devolvido com sucesso.'})

def pagina_login(request):
    return render(request, 'registration/login.html')

def cadastro(request):
    if request.method == 'POST':
        metodo = request.POST.get('metodo_contato')
        # salva o metodo junto ao usuario
    return render(request, 'registration/cadastro.html')

def recuperar_senha(request):
    metodo = None
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        usuario = Usuario.objects.filter(matricula=matricula).first()
        if usuario:
            metodo = usuario.metodo_contato
    return render(request, 'registration/recuperar_senha.html', {'metodo': metodo})

@require_POST
def renovar_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    hoje = timezone.now().date()
    if emprestimo.data_devolucao_prevista < hoje:
        return JsonResponse({
            "Erro": "Não é possível renovar um empréstimo atrasado",
            "status": "Erro"
        }, status=400)
    if emprestimo.renovacoes_concluidas >= 3:
        return JsonResponse({
            "Erro": "Limite de renovações atingido para este empréstimo",
            "status": "Erro"
        }, status=400)
    emprestimo.data_devolucao_prevista += timezone.timedelta(days=15)
    emprestimo.renovacoes_concluidas += 1
    emprestimo.foi_renovado = True
    emprestimo.save()
    return JsonResponse({
        "sucesso": f"Renovado com sucesso. A nova data é: {emprestimo.data_devolucao_prevista}",
        "nova_data": str(emprestimo.data_devolucao_prevista),
        "status": "Sucesso"
    })

@require_POST
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)  # ← salva na variável
    if reserva.usuario != request.user:
        return JsonResponse({"Erro": "Você não tem permissão para cancelar esta reserva"}, status=403)
    if reserva.status != 'pendente':
        return JsonResponse({"Erro": "Esta reserva não pode mais ser cancelada"}, status=400)
    reserva.status = 'cancelada'
    reserva.save()
    return JsonResponse({"sucesso": "Reserva cancelada com sucesso"})

def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    disponivel = livro.esta_disponivel()
    return render(request, 'biblioteca/detalhes_livro.html', {'livro': livro, 'disponivel': disponivel})

def configuracoes(request):
    return render(request, 'biblioteca/configuracoes.html')

class LivroViewset(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'autor']  # busca por título ou autor

@require_POST
def deletar_lista(request, pk):
    lista = get_object_or_404(Lista, pk=pk)
    lista.delete()
    return JsonResponse({'sucesso': 'Lista deletada.'})