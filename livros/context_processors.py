from .models import Genero


def menu(request):
    """Deixa a lista de gêneros disponível em todos os templates (menu lateral do base.html)."""
    return {'generos_menu': Genero.objects.all()}
