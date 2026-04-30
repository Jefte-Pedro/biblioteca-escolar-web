from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    # Campos do AbstractUser que já vêm prontos:
    # username, password, first_name, last_name, email, is_staff, is_active

    matricula = models.CharField(max_length=20, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    serie = models.CharField(max_length=50, blank=True, null=True)
    primeiro_acesso = models.BooleanField(default=True)  # True = ainda não criou senha

    tipo_usuario = models.CharField(choices=[
        ('aluno', 'Aluno'),
        ('exaluno', 'Ex-aluno'),
        ('bibliotecario', 'Bibliotecário'),
    ], max_length=20, default='aluno')

    observacoes = models.TextField(blank=True)

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_bibliotecario(self):
        return self.tipo_usuario == 'bibliotecario'


class Livro(models.Model):
    id_livro = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=300)
    autor = models.CharField(max_length=200)
    editora = models.CharField(max_length=150, blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    colecao = models.CharField(max_length=150, blank=True, null=True)
    quantidade = models.IntegerField(blank=True, null=True)
    codigo_base = models.CharField(max_length=50, blank=True, null=True)
    prateleira = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'livro'

    def __str__(self):
        return self.titulo

    def esta_disponivel(self):
        total_exemplares = self.quantidade or 0
        emprestimos_ativos = Emprestimo.objects.filter(livro=self, data_devolucao_real__isnull=True).count()
        reservas_ativas = Reserva.objects.filter(livro=self, status='pendente').count()
        return total_exemplares > (emprestimos_ativos + reservas_ativas)
    
    @property
    def unidades_disponiveis(self):
        total = self.quantidade or 0
        emprestimos_ativos = Emprestimo.objects.filter(livro=self, data_devolucao_real__isnull=True).count()
        reservas_ativas = Reserva.objects.filter(livro=self, status='pendente').count()
        return max(0, total - emprestimos_ativos - reservas_ativas)


class Emprestimo(models.Model):
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    codigo_catalografico = models.CharField(max_length=50)
    nome_aluno = models.CharField(max_length=100)
    turma = models.CharField(max_length=50)
    data_emprestimo = models.DateField(default=timezone.now)
    data_devolucao_prevista = models.DateField(blank=True, null=True)
    data_devolucao_real = models.DateField(null=True, blank=True)
    renovacoes_concluidas = models.IntegerField(default=0)
    foi_renovado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nome_aluno} - {self.livro.titulo}"

    def esta_atrasado(self):
        if self.data_devolucao_real:
            return False
        return timezone.now().date() > self.data_devolucao_prevista

    def save(self, *args, **kwargs):
        if not self.data_devolucao_prevista:
            self.data_devolucao_prevista = self.data_emprestimo + timedelta(days=15)
        super().save(*args, **kwargs)


class Reserva(models.Model):
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    data_reserva = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(default=timezone.now() + timedelta(days=15))
    data_notificacao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    lembrete_enviado = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ], default='pendente')

    def __str__(self):
        return f"Reserva: {self.livro.titulo} para {self.usuario}"


class Lista(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome