from django.shortcuts import render
from rest_framework import viewsets
from .models import Livro
from .serializers import LivroSerializer
# Create your views here.
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
