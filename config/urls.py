"""Rotas do projeto.

- /admin/            parte administrativa do Django
- /contas/...        entrar, sair e criar conta
- todo o resto       app "livros" (livros/urls.py)
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from livros import views as livros_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/entrar/', auth_views.LoginView.as_view(), name='login'),
    path('contas/sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('contas/cadastro/', livros_views.cadastro, name='cadastro'),
    path('', include('livros.urls')),
]
