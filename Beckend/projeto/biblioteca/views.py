from django.shortcuts import render
from rest_framework import viewsets
from .models import Livro
from .serializers import LivroSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Emprestimo
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

def login(request):
    return render(request, 'biblioteca/Login.html')

def cadastro(request):
    return render(request, 'biblioteca/Login.html')

def recuperar_senha(request):
    return render(request, 'biblioteca/Login.html')

def renovar_emprestimo(request, pk): # Busca o empréstimo pelo ID
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    # Atualiza a data somando 15 dias ao prazo que já existia
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
    emprestimo.data.devolucao += timezone.timedelta(days=15)
    # Salva a alteração no mesmo registro (mantém o mesmo ID)
    emprestimo.renovacoes_concluidas += 1
    # Para adicionar uma renovação no emprestimo, caso bata 3, o sistema não permitirá mais renovações para aquele empréstimo.
    emprestimo.save()
    # Retorna uma resposta JSON indicando sucesso
    return JsonResponse({
        "sucesso": f"Renovado com sucesso. A nova data é: {emprestimo.data_devolucao_prevista}",
        "status": "Sucesso"
    })