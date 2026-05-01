import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')
django.setup()

from biblioteca.models import Usuario

dev = Usuario.objects.create_user(
    username='dev',
    password='dev123456',
    first_name='Jefte',
    last_name='Pedro',
    matricula=1,
    tipo_usuario='bibliotecario',
    primeiro_acesso=False,
)

aluno = Usuario.objects.create_user(
    username='aluno_teste',
    password='aluno123456',
    first_name='Aluno',
    last_name='Teste',
    matricula=2,
    tipo_usuario='aluno',
    primeiro_acesso=False,
)

print("✅ DEV:", dev)
print("✅ Aluno:", aluno)