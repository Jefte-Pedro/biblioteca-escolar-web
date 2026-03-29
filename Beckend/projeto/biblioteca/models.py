from django.db import models
from django.utils import timezone
from datetime import timedelta

# Cria os modelos e classes de cada entidade.
class Livro(models.Model):

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    editora = models.CharField(max_length=150)
    genero =  models.CharField(max_length=100)
    edicao = models.CharField(max_length=50)
    sinopse = models.TextField()
    capa = models.ImageField(upload_to='capas/')
    quantidade = models.IntegerField()
    endereco_prateleira = models.CharField(max_length=100)
    observacoes = models.TextField()

    def __str__(self):
        return self.titulo
    
    class Usuario(models.Model):
        nome = models.CharField(max_length=100)
        email = models.EmailField(unique=True)
        senha = models.CharField(max_length=100)
        telefone = models.CharField(max_length=20, unique=True)
        tipo_usuario = models.CharField(aluno='Aluno', funcionario='Funcionário', exaluno='Ex-aluno', max_length=20)
        observacoes = models.TextField()

        def __str__(self):
            return self.nome
        
    class Emprestimo(models.Model):
        # As chave estrangeiras para Livro e Usuario, 
        # com on_delete=models.CASCADE para garantir que 
        # os empréstimos sejam excluídos se o livro ou usuário 
        # for removido.
        livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
        usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
        # Datas dos empréstimos, com data_emprestimo padrão 
        # para a data atual e data_devolucao para 15 dias depois
        # e para quando foi realmente devolvido.
        data_emprestimo = models.DateField(default=timezone.now)
        data_devolucao_prevista = models.DateField(default=timezone.now() + timedelta(days=15))
        data_devolucao_real = models.DateField(null=True, blank=True)
        observacoes = models.TextField(blank=True)

        def __str__(self):
            return f"{self.usuario.nome} - {self.livro.titulo}"
        
    class Reserva(models.Model):
        livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
        usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
        data_reserva = models.DateTimeField(auto_now_add=True) # Define a data de reserva como o momento em que a reserva é criada
        data_expiracao = models.DateTimeField(default=timezone.now() + timedelta(days=15))
        data_notificacao = models.DateTimeField(null=True, blank=True)
        observacoes = models.TextField(blank=True)
        lembrete_enviado = models.BooleanField(default=False)

        def __str__(self):
            return f"Reserva:{self.livro.titulo} para {self.usuario.nome}"