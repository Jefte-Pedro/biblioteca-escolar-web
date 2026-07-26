import re
import csv
from django.core.management.base import BaseCommand
from django.db.models import Count
from biblioteca.models import Livro

# Abreviações conhecidas -> forma expandida (ajuste conforme for revisando o CSV)
ABREVIACOES = [
    (r'\bifn\.?\s*jov\.?\b', 'Infantojuvenil'),
    (r'\binf\.?\s*juv\.?\b', 'Infantojuvenil'),
    (r'\blit\.?\b', 'Literatura'),
    (r'\bifn\.?\b', 'Infantil'),
    (r'\bjov\.?\b', 'Juvenil'),
    (r'\bjuv\.?\b', 'Juvenil'),
    (r'\bed\.?\b', 'Educação'),
]

# Grupos que precisam de mais de uma palavra para não virarem "Ciências" genérico demais
GRUPOS_COMPOSTOS = [
    'Ciências da Natureza', 'Ciências Sociais', 'Ficção Científica',
    'Língua Estrangeira', 'Formação de Professores', 'Educação Infantil',
    'Educação Especial', 'Lingua Estrangeira',
]

def normalizar(texto):
    t = texto.strip().lower()
    for padrao, substituto in ABREVIACOES:
        t = re.sub(padrao, substituto.lower(), t)
    return ' '.join(w.capitalize() for w in t.split())

def sugerir_grupo(categoria_normalizada):
    for composto in GRUPOS_COMPOSTOS:
        if categoria_normalizada.lower().startswith(composto.lower()):
            return composto
    palavras = categoria_normalizada.split()
    return palavras[0] if palavras else categoria_normalizada


class Command(BaseCommand):
    help = 'Lista as categorias distintas e sugere um agrupamento, para revisão manual em CSV.'

    def handle(self, *args, **options):
        categorias = (
            Livro.objects.exclude(categoria__isnull=True).exclude(categoria='')
            .values('categoria').annotate(total=Count('id_livro')).order_by('categoria')
        )

        linhas = []
        for item in categorias:
            original = item['categoria']
            total = item['total']
            grupo = sugerir_grupo(normalizar(original))
            linhas.append((original, total, grupo))

        linhas.sort(key=lambda x: (x[2], -x[1]))

        caminho = 'mapeamento_categorias.csv'
        with open(caminho, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['categoria_original', 'quantidade_livros', 'grupo_sugerido'])
            writer.writerows(linhas)

        self.stdout.write(self.style.SUCCESS(
            f'{len(linhas)} categorias analisadas. Abra "{caminho}" no Excel/LibreOffice, '
            f'revise a coluna grupo_sugerido (corrija onde estiver errado) e salve.'
        ))