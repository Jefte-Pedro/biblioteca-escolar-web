from django.shortcuts import render
from rest_framework import viewsets
from .models import Livro
from .serializers import LivroSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Emprestimo
from .models import Reserva
from django.utils import timezone
# Cria as views.
class LivroViewset(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

def inicio(request):
    return render(request, 'biblioteca/inicio.html')

def lista(request):
    return render(request, 'biblioteca/acervo.html', { 'aba': 'lista' })

def lidos(request):
    return render(request, 'biblioteca/acervo.html', { 'aba': 'lidos' })

def reservados(request):
    return render(request, 'biblioteca/acervo.html', { 'aba': 'reservados' })

def prazos(request):
    return render(request, 'biblioteca/prazo.html')

def cadastrar_livro(request):
    return render(request, 'biblioteca/cad-livro.html')

def emprestimos(request):
    return render(request, 'biblioteca/emp-livro.html')

def login(request):
    return render(request, 'biblioteca/Login.html')

def cadastro(request):
    return render(request, 'biblioteca/Login.html')

def recuperar_senha(request):
    return render(request, 'biblioteca/Login.html')

def renovar_emprestimo(request, pk): # Busca o empréstimo pelo ID
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    hoje = timezone.now().date()
    if emprestimo.data_devolucao_prevista < hoje: # Verifica se o empréstimo está atrasado
        return JsonResponse({
            "Erro": "Não é possível renovar um empréstimo atrasado",
            "status": "Erro"
        }, status=400)
    if emprestimo.renovacoes_concluidas >= 3: # Verifica se o empréstimo já foi renovado 3 vezes
        return JsonResponse({
            "Erro": "Limite de renovações atingido para este empréstimo",
            "status": "Erro"
        }, status=400)
    # Se após isso, o empréstimo ainda for elegível para renovação, atualiza a data de devolução prevista
    emprestimo.data_devolucao_prevista += timezone.timedelta(days=15) # Atualiza a data somando 15 dias ao prazo que já existia
    # Salva a alteração no mesmo registro (mantém o mesmo ID)
    emprestimo.renovacoes_concluidas += 1
    # Para adicionar uma renovação no emprestimo, caso bata 3, o sistema não permitirá mais renovações para aquele empréstimo.
    emprestimo.save()
    # Retorna uma resposta JSON indicando sucesso
    return JsonResponse({
        "sucesso": f"Renovado com sucesso. A nova data é: {emprestimo.data_devolucao_prevista}",
        "status": "Sucesso"
    })

def cancelar_reserva(request, pk):
    get_object_or_404(Reserva, pk=pk) #Busca a reserva pelo ID, se não encontrar, retorna 404
    if Reserva.usuario != request.user: # Verifica se a reserva pertence ao usuário logado
        return JsonResponse({
            "Erro": "Você não tem permissão para cancelar esta reserva",
            "status": "Erro"
        }, status=403)
    if Reserva.status != 'pendente': # Verifica se a reserva ainda está pendente
        return JsonResponse({
            "Erro": "Esta reserva não pode ser mais ser cancelada",
        }, status=400)
    Reserva.status = 'cancelada' # Se a reserva for válida para cancelamento, exclui o registro
    Reserva.save()
    return JsonResponse({
        "sucesso": "Reserva cancelada com sucesso",
        "status": "Sucesso"
    })

def detalhes_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    disponivel = livro.esta_disponivel()
    return render(request, 'biblioteca/detalhes_livro.html', {'livro': livro, 'disponivel': disponivel})