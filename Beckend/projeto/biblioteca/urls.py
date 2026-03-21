from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivroViewset
from . import views

router = DefaultRouter()
router.register(r'livros', LivroViewset)

urlpatterns = [
    # path('', include(router.urls)),
    path('', views.inicio, name='inicio'), 
    path('acervo/', views.acervo, name='acervo'),
    path('prazos/', views.prazos, name='prazos'),
    path('api/', include(router.urls)),
]