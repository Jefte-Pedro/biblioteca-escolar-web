from django.contrib import admin
from .models import CategoriaGrupo, Livro


@admin.register(CategoriaGrupo)
class CategoriaGrupoAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'grupo', 'qtd_livros', 'criado_automaticamente', 'revisado')
    list_filter = ('criado_automaticamente', 'revisado')
    search_fields = ('categoria', 'grupo')
    list_editable = ('grupo', 'revisado')
    ordering = ('-criado_automaticamente', 'grupo', 'categoria')

    def qtd_livros(self, obj):
        return Livro.objects.filter(categoria=obj.categoria).count()
    qtd_livros.short_description = 'Livros com essa categoria'