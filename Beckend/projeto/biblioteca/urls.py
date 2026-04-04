from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivroViewset
from . import views

router = DefaultRouter()
router.register(r'livros', LivroViewset)

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.inicio, name='inicio'), 
    

    path('acervo/lista/', views.lista, name='minha_lista'),
    path('acervo/reservados/', views.reservados, name='reservados'),
    path('acervo/lidos/', views.lidos, name='lidos'),

    path('prazos/', views.prazos, name='prazos'),

    path('cadastrar-livro/', views.cadastrar_livro, name='cadastrar-livro'),
    path('emprestimos/', views.emprestimos, name='emprestimos'),

    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar_senha'),

    path('api/', include(router.urls)),

    path('renovar/<int:pk>/', views.renovar_emprestimo, name='renovar_emprestimo'),
    path('cancelar-reserva/<int:pk>/', views.cancelar_reserva, name='cancelar_reserva'),
]