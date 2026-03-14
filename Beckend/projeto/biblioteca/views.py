from django.shortcuts import render
from rest_framework import viewsets
from .models import Livro
from .serializers import LivroSerializer
# Create your views here.
class LivroViewset(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer