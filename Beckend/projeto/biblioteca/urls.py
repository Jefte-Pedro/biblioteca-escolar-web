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
    path('acervo/lista/criar/', views.criar_lista, name='criar_lista'),
    path('acervo/lista/deletar/<int:pk>/', views.deletar_lista, name='deletar_lista'),

    path('acervo/', views.acervo, name='acervo'),


    path('prazos/', views.prazos, name='prazos'),
    path('emprestimos/criar/', views.criar_emprestimo, name='criar_emprestimo'),
    path('emprestimos/renovar/<int:pk>/', views.renovar_emprestimo, name='renovar_emprestimo'),
    path('emprestimos/devolver/<int:pk>/', views.devolver_emprestimo, name='devolver_emprestimo'),


    path('cadastrar-livro/', views.cadastrar_livro, name='cadastrar-livro'),
    path('emprestimos/', views.emprestimos, name='emprestimos'),

    path('livro/<int:livro_id>/', views.detalhes_livro, name='detalhes_livro'),

    path('login/', views.pagina_login, name='login'),
    path('login/cadastro/', views.cadastro, name='cadastro'),
    path('login/recuperar_senha/', views.recuperar_senha, name='recuperar_senha'),

    path('api/', include(router.urls)),

    path('configuracoes/', views.configuracoes, name='configuracoes'),


    path('cancelar-reserva/<int:pk>/', views.cancelar_reserva, name='cancelar_reserva'),
]