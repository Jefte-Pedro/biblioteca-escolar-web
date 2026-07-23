from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivroViewset
from . import views

router = DefaultRouter()
router.register(r'livros', LivroViewset)

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('acervo/', views.acervo, name='acervo'),
    path('acervo/lista/', views.lista, name='minha_lista'),
    path('acervo/lista/criar/', views.criar_lista, name='criar_lista'),
    path('acervo/lista/excluir/<int:lista_id>/', views.excluir_lista, name='excluir_lista'),
    path('acervo/lista/renomear/<int:lista_id>/', views.renomear_lista, name='renomear_lista'), 
    path('acervo/reservados/', views.reservados, name='reservados'),
    path('acervo/lidos/', views.lidos, name='lidos'),

    
    path('lista/<int:lista_id>/', views.detalhe_lista, name='detalhe_lista'),
    path('lista/<int:lista_id>/adicionar-livro/', views.adicionar_livro_lista, name='adicionar_livro_lista'),
    path('lista/<int:lista_id>/remover-livro/', views.remover_livro_lista, name='remover_livro_lista'),

    path('listas/minhas/', views.listas_do_usuario, name='listas_do_usuario'),

    path('explorar/', views.explorar, name='explorar'),

    path('prazos/', views.prazos, name='prazos'),

    path('emprestimos/', views.emprestimos, name='emprestimos'),
    path('emprestimos/criar/', views.criar_emprestimo, name='criar_emprestimo'),
    path('emprestimos/renovar/<int:pk>/', views.renovar_emprestimo, name='renovar_emprestimo'),
    path('emprestimos/devolver/<int:pk>/', views.devolver_emprestimo, name='devolver_emprestimo'),

    path('cadastrar-livro/', views.cadastrar_livro, name='cadastrar-livro'),

    path('buscar-livro/', views.buscar_livro, name='buscar_livro'),
    path('buscar-usuario/', views.buscar_usuario, name='buscar_usuario'),

    path('livro/<int:livro_id>/', views.detalhes_livro, name='detalhes_livro'),
    path('livro/<int:livro_id>/editar/', views.editar_livro, name='editar_livro'),
    path('livro/<int:livro_id>/marcar-lido/', views.marcar_livro_lido, name='marcar_livro_lido'),
    path('livro/<int:livro_id>/desmarcar-lido/', views.desmarcar_livro_lido, name='desmarcar_livro_lido'),
    
    path('livro/excluir/<int:id_livro>/', views.excluir_livro, name='excluir_livro'),

    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/grafico/', views.relatorios_grafico, name='relatorios_grafico'),
    path('relatorios/exportar-pdf/', views.exportar_relatorio_pdf, name='exportar_relatorio_pdf'),

    path('login/', views.pagina_login, name='login'),
    path('login/cadastro/', views.cadastro, name='cadastro'),
    path('login/recuperar_senha/', views.recuperar_senha, name='recuperar_senha'),
    path('login/verificar-matricula/', views.verificar_matricula, name='verificar_matricula'),
    path('login/primeiro-acesso/', views.primeiro_acesso, name='primeiro_acesso'),
    path('login/entrar/', views.fazer_login, name='fazer_login'),
    path('logout/', views.fazer_logout, name='logout'),
    path('login/enviar-codigo/', views.enviar_codigo, name='enviar_codigo'),
    path('login/verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),   
    path('login/verificar/', views.verificar_codigo_page, name='verificar_codigo_page'),
    
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('configuracoes/salvar-perfil/', views.salvar_perfil, name='salvar_perfil'),
    path('configuracoes/alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('configuracoes/salvar-notif/', views.salvar_notif, name='salvar_notif'),

    path('notificacoes/', views.notificacoes_listar, name='notificacoes_listar'),
    path('notificacoes/nao-lidas/', views.notificacoes_nao_lidas, name='notificacoes_nao_lidas'),
    path('notificacoes/<int:pk>/marcar-lida/', views.notificacoes_marcar_lida, name='notificacoes_marcar_lida'),
    path('notificacoes/marcar-todas-lidas/', views.notificacoes_marcar_todas_lidas, name='notificacoes_marcar_todas_lidas'),
    path('notificacoes/<int:pk>/responder/', views.notificacoes_responder, name='notificacoes_responder'),  
    
    path('livro/<int:livro_id>/reservar/', views.reservar_livro, name='reservar_livro'),
    path('reservas/<int:pk>/confirmar-retirada/', views.reserva_confirmar_retirada, name='reserva_confirmar_retirada'),
    path('notificacoes/<int:pk>/excluir/', views.notificacoes_excluir, name='notificacoes_excluir'),
    path('notificacoes/excluir-todas/', views.notificacoes_excluir_todas, name='notificacoes_excluir_todas'),
    path('cancelar-reserva/<int:pk>/', views.cancelar_reserva, name='cancelar_reserva'),

    path('alunos/', views.alunos, name='alunos'),
    path('alunos/importar/', views.importar_alunos, name='importar_alunos'),
    path('alunos/excluir/<int:pk>/', views.excluir_aluno, name='excluir_aluno'),
    path('alunos/limpar/', views.limpar_alunos, name='limpar_alunos'),
    path('turmas/', views.listar_turmas,  name='listar_turmas'),
    path('turmas/salvar/',  views.salvar_turmas,  name='salvar_turmas'),  
    path('cargos/', views.listar_cargos,  name='listar_cargos'),
    path('cargos/salvar/',  views.salvar_cargo,   name='salvar_cargo'),
    path('cargos/excluir/<int:pk>/', views.excluir_cargo,  name='excluir_cargo'),
    path('alunos/atribuir-cargo/<int:pk>/', views.atribuir_cargo, name='atribuir_cargo'),

    path('emprestimos/excluir-historico/<int:pk>/', views.excluir_historico, name='excluir-historico'),
    path('emprestimos/notificar-atraso/<int:pk>/', views.notificar_atraso, name='notificar_atraso'),
    path('exportar/', views.exportar, name='exportar'),
    path('exportar/acervo/', views.exportar_acervo,      name='exportar_acervo'),
    path('exportar/emprestimos/', views.exportar_emprestimos,  name='exportar_emprestimos'),
    path('exportar/alunos/', views.exportar_alunos,      name='exportar_alunos'),
    
    path('login/recuperar-buscar-contato/', views.recuperar_buscar_contato, name='recuperar_buscar_contato'),
    path('login/redefinir-senha/', views.redefinir_senha_recuperacao, name='redefinir_senha_recuperacao'),
    path('login/nova-senha/', views.nova_senha_page, name='nova_senha_page'),
    
    path('api/', include(router.urls)),
]   