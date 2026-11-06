from django.urls import path

from . import views

app_name = 'livros'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('livros/', views.lista_livros, name='lista'),
    path('livros/novo/', views.novo_livro, name='novo_livro'),
    path('livros/<int:pk>/', views.detalhe_livro, name='detalhe'),
    path('livros/<int:pk>/resenhar/', views.nova_resenha, name='nova_resenha'),
    path('resenhas/<int:pk>/editar/', views.editar_resenha, name='editar_resenha'),
    path('resenhas/<int:pk>/excluir/', views.excluir_resenha, name='excluir_resenha'),
    path('minhas-resenhas/', views.minhas_resenhas, name='minhas_resenhas'),
]
