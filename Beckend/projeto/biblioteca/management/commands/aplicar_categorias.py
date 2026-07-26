import csv
from django.core.management.base import BaseCommand
from biblioteca.models import Livro


class Command(BaseCommand):
    help = 'Aplica o mapeamento revisado (mapeamento_categorias.csv) ao campo categoria_grupo.'

    def add_arguments(self, parser):
        parser.add_argument('--arquivo', default='mapeamento_categorias.csv')

    def handle(self, *args, **options):
        caminho = options['arquivo']
        atualizados = 0
        nao_encontrados = []

        with open(caminho, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for linha in reader:
                original = linha['categoria_original']
                grupo = linha['grupo_sugerido'].strip()
                if not grupo:
                    continue
                n = Livro.objects.filter(categoria=original).update(categoria_grupo=grupo)
                if n == 0:
                    nao_encontrados.append(original)
                atualizados += n

        self.stdout.write(self.style.SUCCESS(f'{atualizados} livros atualizados com categoria_grupo.'))

        if nao_encontrados:
            self.stdout.write(self.style.WARNING(
                f'{len(nao_encontrados)} categorias do CSV não bateram com nenhum livro (nome pode ter mudado): '
                + ', '.join(nao_encontrados)
            ))