from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import (
    Usuario,
    Livro,
    Exemplar,
    Emprestimo,
)


class LivroModelTest(TestCase):
    def test_normaliza_categoria_ao_salvar(self):
        livro = Livro.objects.create(
            titulo='Dom Casmurro',
            categoria='  LITERATURA   brasileira  ',
        )

        self.assertEqual(livro.categoria, 'Literatura Brasileira')

    def test_livro_disponivel_quando_exemplar_disponivel(self):
        livro = Livro.objects.create(titulo='Dom Casmurro')

        Exemplar.objects.create(
            livro=livro,
            codigo_variante='01',
            codigo_completo='DC-01',
            status='disponivel',
        )

        self.assertTrue(livro.esta_disponivel())
        self.assertEqual(livro.unidades_disponiveis, 1)

    def test_livro_indisponivel_quando_nao_ha_exemplar_disponivel(self):
        livro = Livro.objects.create(titulo='Dom Casmurro')

        Exemplar.objects.create(
            livro=livro,
            codigo_variante='01',
            codigo_completo='DC-01',
            status='emprestado',
        )

        self.assertFalse(livro.esta_disponivel())
        self.assertEqual(livro.unidades_disponiveis, 0)


class EmprestimoModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='aluno1',
            password='senha123',
        )

        self.livro = Livro.objects.create(
            titulo='Dom Casmurro',
        )

        self.exemplar = Exemplar.objects.create(
            livro=self.livro,
            codigo_variante='01',
            codigo_completo='DC-01',
        )

    def test_define_prazo_automaticamente(self):
        data_emprestimo = timezone.now().date()

        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            usuario=self.usuario,
            data_emprestimo=data_emprestimo,
        )

        self.assertEqual(
            emprestimo.data_devolucao_prevista,
            data_emprestimo + timedelta(days=15),
        )

    def test_emprestimo_nao_esta_atrasado_antes_do_vencimento(self):
        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            usuario=self.usuario,
            data_devolucao_prevista=timezone.now().date() + timedelta(days=2),
        )

        self.assertFalse(emprestimo.esta_atrasado())

    def test_emprestimo_esta_atrasado_depois_do_vencimento(self):
        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            usuario=self.usuario,
            data_devolucao_prevista=timezone.now().date() - timedelta(days=1),
        )

        self.assertTrue(emprestimo.esta_atrasado())

    def test_emprestimo_devolvido_nao_esta_atrasado(self):
        emprestimo = Emprestimo.objects.create(
            exemplar=self.exemplar,
            usuario=self.usuario,
            data_devolucao_prevista=timezone.now().date() - timedelta(days=1),
            data_devolucao_real=timezone.now().date(),
        )

        self.assertFalse(emprestimo.esta_atrasado())