from django import template

register = template.Library()


@register.filter
def estrelas(nota):
    """Transforma uma nota (ex.: 4.3) em 5 posições cheias/vazias: [True, True, True, True, False]."""
    cheias = round(nota or 0)
    return [i < cheias for i in range(5)]


@register.filter
def matiz(usuario):
    """Matiz (0-359) fixo para cada usuário, usado na cor do avatar.
    Somar 137 graus a cada id deixa usuários vizinhos com cores bem diferentes."""
    return (usuario.pk * 137) % 360


@register.filter
def nome_exibicao(usuario):
    return usuario.first_name or usuario.username
