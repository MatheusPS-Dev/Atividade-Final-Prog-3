from django import template

register = template.Library()


@register.filter
def estrelas(nota):
    cheias = round(nota or 0)
    return [i < cheias for i in range(5)]


@register.filter
def matiz(usuario):
    return (usuario.pk * 137) % 360


@register.filter
def nome_exibicao(usuario):
    return usuario.first_name or usuario.username
