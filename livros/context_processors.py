from .models import Genero


def menu(request):
    return {'generos_menu': Genero.objects.all()}
