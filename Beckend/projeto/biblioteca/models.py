from django.db import models
from django.utils import timezone
from datetime import timedelta

# Cria os modelos e classes de cada entidade.
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

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, unique=True)
        
    tipo_usuario = models.CharField(choices=[
        ('aluno', 'Aluno'),
        ('exaluno', 'Ex-aluno')
    ], max_length=20)
    observacoes = models.TextField()

    def __str__(self):
        return self.nome
        
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
        # Se não tiver data de devolução, soma 15 dias automaticamente
        if not self.data_devolucao_prevista:
            self.data_devolucao_prevista = self.data_emprestimo + timedelta(days=15)
        super().save(*args, **kwargs)
        
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
    
class Lista(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome