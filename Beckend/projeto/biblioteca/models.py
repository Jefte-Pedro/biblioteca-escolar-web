from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


# ──────────────────────────────────────────
# USUÁRIO
# ──────────────────────────────────────────

class Usuario(AbstractUser):
    matricula = models.IntegerField(unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=11, blank=True, null=True)
    turma = models.CharField(max_length=5, blank=True, null=True)
    serie = models.CharField(max_length=50, blank=True, null=True)
    primeiro_acesso = models.BooleanField(default=True)
    tipo_usuario = models.CharField(choices=[
        ('aluno', 'Aluno'),
        ('exaluno', 'Ex-aluno'),
        ('bibliotecario', 'Bibliotecário'),
    ], max_length=20, default='aluno')
    observacoes = models.TextField(blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_set',
        blank=True,
    )
    
    class Meta:
        db_table = 'biblioteca_usuario'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_bibliotecario(self):
        return self.tipo_usuario == 'bibliotecario'


# ──────────────────────────────────────────
# LIVRO
# ──────────────────────────────────────────

class Livro(models.Model):
    id_livro = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=300)
    autor = models.CharField(max_length=200, blank=True, null=True)
    editora = models.CharField(max_length=150, blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    colecao = models.CharField(max_length=150, blank=True, null=True)
    quantidade = models.IntegerField(default=1)
    codigo_base = models.CharField(max_length=50, blank=True, null=True)
    prateleira = models.CharField(max_length=10, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    capa_url = models.TextField(blank=True, null=True)
    sinopse = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'livro'
        managed = True

    def __str__(self):
        return self.titulo

    def esta_disponivel(self):
        return Exemplar.objects.filter(
            livro=self, status='disponivel'
        ).exists()

    @property
    def unidades_disponiveis(self):
        return Exemplar.objects.filter(
            livro=self, status='disponivel'
        ).count()


# ──────────────────────────────────────────
# EXEMPLAR
# ──────────────────────────────────────────

class Exemplar(models.Model):
    id_exemplar = models.AutoField(primary_key=True)
    livro = models.ForeignKey(
        Livro, on_delete=models.CASCADE, db_column='id_livro'
    )
    codigo_variante = models.CharField(max_length=10)
    codigo_completo = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('disponivel', 'Disponível'),
        ('emprestado', 'Emprestado'),
        ('reservado', 'Reservado'),
        ('indisponivel', 'Indisponível'),
    ], default='disponivel')

    class Meta:
        db_table = 'exemplar'
        managed = True

    def __str__(self):
        return f"{self.codigo_completo} - {self.livro.titulo}"


# ──────────────────────────────────────────
# EMPRESTIMO
# ──────────────────────────────────────────

class Emprestimo(models.Model):
    exemplar = models.ForeignKey(
        Exemplar, on_delete=models.CASCADE, db_column='id_exemplar'
    )
    usuario = models.ForeignKey(
        'Usuario', on_delete=models.CASCADE
    )
    data_emprestimo = models.DateField(default=timezone.now)
    data_devolucao_prevista = models.DateField(blank=True, null=True)
    data_devolucao_real = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        db_table = 'biblioteca_emprestimo'

    def __str__(self):
        return f"{self.usuario} - {self.exemplar}"

    def esta_atrasado(self):
        if self.data_devolucao_real:
            return False
        return timezone.now().date() > self.data_devolucao_prevista

    def save(self, *args, **kwargs):
        if not self.data_devolucao_prevista:
            self.data_devolucao_prevista = (
                self.data_emprestimo + timedelta(days=15)
            )
        super().save(*args, **kwargs)


# ──────────────────────────────────────────
# RESERVA
# ──────────────────────────────────────────

class Reserva(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    data_reserva = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(blank=True, null=True)
    data_notificacao = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ], default='pendente')
    lembrete_enviado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)

    class Meta:
        db_table = 'biblioteca_reserva'

    def __str__(self):
        return f"Reserva: {self.livro.titulo} para {self.usuario}"


# ──────────────────────────────────────────
# LISTA
# ──────────────────────────────────────────

class Lista(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    criada_em = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(blank=True, null=True)
    livros = models.ManyToManyField(Livro, blank=True)

    class Meta:
        db_table = 'biblioteca_lista'

    def __str__(self):
        return self.nome


# ──────────────────────────────────────────
# LIVRO LIDO
# ──────────────────────────────────────────

class LivroLido(models.Model):
    usuario      = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='livros_lidos')
    livro        = models.ForeignKey(Livro,   on_delete=models.CASCADE, related_name='leitores')
    data_marcado = models.DateField(auto_now_add=True)

    class Meta:
        db_table        = 'biblioteca_livrolido'
        unique_together = ('usuario', 'livro')
        ordering        = ['-data_marcado']
        verbose_name    = 'Livro Lido'
        verbose_name_plural = 'Livros Lidos'

    def __str__(self):
        return f'{self.usuario} – {self.livro.titulo}'