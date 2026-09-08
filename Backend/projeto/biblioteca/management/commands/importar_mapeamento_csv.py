import csv
from django.core.management.base import BaseCommand
from biblioteca.models import CategoriaGrupo, Livro


class Command(BaseCommand):
    help = (
        'Importa o CSV já revisado para a tabela CategoriaGrupo (fonte '
        'permanente do mapeamento) e sincroniza os livros existentes. '
        'Rode isso UMA VEZ, depois disso o sistema mantém tudo sozinho.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--arquivo', default='mapeamento_categorias.csv')

    def handle(self, *args, **options):
        caminho = options['arquivo']
        criados = atualizados = 0

        with open(caminho, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for linha in reader:
                categoria = linha['categoria_original'].strip()
                grupo = linha['grupo_sugerido'].strip()
                if not categoria or not grupo:
                    continue

                obj, criado = CategoriaGrupo.objects.update_or_create(
                    categoria=categoria,
                    defaults={
                        'grupo': grupo,
                        'criado_automaticamente': False,
                        'revisado': True,
                    },
                )
                if criado:
                    criados += 1
                else:
                    atualizados += 1

        # Sincroniza os livros já existentes com a tabela de mapeamento
        total_sincronizados = 0
        for mapeamento in CategoriaGrupo.objects.all():
            n = Livro.objects.filter(categoria=mapeamento.categoria).exclude(
                categoria_grupo=mapeamento.grupo
            ).update(categoria_grupo=mapeamento.grupo)
            total_sincronizados += n

        self.stdout.write(self.style.SUCCESS(
            f'{criados} mapeamentos criados, {atualizados} atualizados. '
            f'{total_sincronizados} livros sincronizados.'
        ))