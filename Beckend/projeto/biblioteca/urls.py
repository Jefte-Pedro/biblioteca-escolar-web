from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivroViewset
from . import views

router = DefaultRouter()
router.register(r'livros', LivroViewset)

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.inicio, name='inicio'), 

    path('lista/', views.lista, name='minha_lista'),
    path('reservados/', views.reservados, name='reservados'),
    path('lidos/', views.lidos, name='lidos'),

    path('prazos/', views.prazos, name='prazos'),

    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar_senha'),

    path('api/', include(router.urls)),
]