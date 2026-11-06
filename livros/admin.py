from django.contrib import admin

from .models import Genero, Livro, Resenha

admin.site.site_header = 'Entre Páginas — Administração'
admin.site.site_title = 'Entre Páginas'
admin.site.index_title = 'Gerenciar o acervo'


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'tom', 'quantidade_de_livros']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ['nome']}

    @admin.display(description='livros')
    def quantidade_de_livros(self, obj):
        return obj.livros.count()


class ResenhaInline(admin.TabularInline):
    model = Resenha
    extra = 0
    fields = ['usuario', 'nota', 'titulo']
    readonly_fields = ['usuario', 'nota', 'titulo']
    can_delete = True
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'genero', 'ano_publicacao', 'cadastrado_por', 'criado_em']
    list_filter = ['genero']
    search_fields = ['titulo', 'autor']
    autocomplete_fields = ['genero']
    inlines = [ResenhaInline]


@admin.register(Resenha)
class ResenhaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'livro', 'usuario', 'nota', 'criado_em']
    list_filter = ['nota', 'livro__genero']
    search_fields = ['titulo', 'texto', 'livro__titulo', 'usuario__username']
    autocomplete_fields = ['livro']
