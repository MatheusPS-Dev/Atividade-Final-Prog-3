from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class Genero(models.Model):
    TONS = [
        ('azul', 'Azul'),
        ('verde', 'Verde'),
        ('teal', 'Verde-azulado'),
        ('rosa', 'Rosa'),
        ('grafite', 'Grafite'),
        ('oliva', 'Oliva'),
    ]

    nome = models.CharField('nome', max_length=60, unique=True)
    slug = models.SlugField(
        'slug', max_length=60, unique=True,
        help_text='Versão do nome usada na URL (ex.: ficcao-cientifica).',
    )
    descricao = models.TextField('descrição', blank=True)
    tom = models.CharField(
        'cor', max_length=10, choices=TONS, default='azul',
        help_text='Cor das etiquetas e das capas dos livros deste gênero.',
    )

    class Meta:
        verbose_name = 'gênero'
        verbose_name_plural = 'gêneros'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('livros:lista') + f'?genero={self.slug}'


class Livro(models.Model):
    titulo = models.CharField('título', max_length=200)
    autor = models.CharField('autor(a)', max_length=150)
    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT,
        related_name='livros',
        verbose_name='gênero',
    )
    ano_publicacao = models.PositiveSmallIntegerField('ano de publicação', null=True, blank=True)
    sinopse = models.TextField('sinopse', blank=True)
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livros_cadastrados',
        verbose_name='cadastrado por',
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'livro'
        verbose_name_plural = 'livros'
        ordering = ['titulo']

    def __str__(self):
        return f'{self.titulo} ({self.autor})'

    def get_absolute_url(self):
        return reverse('livros:detalhe', args=[self.pk])

    def media_notas(self):
        return self.resenhas.aggregate(media=Avg('nota'))['media']


class Resenha(models.Model):
    NOTAS = [
        (1, 'Não gostei'),
        (2, 'Fraco'),
        (3, 'Bom'),
        (4, 'Muito bom'),
        (5, 'Excelente'),
    ]

    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name='resenhas',
        verbose_name='livro',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenhas',
        verbose_name='usuário',
    )
    nota = models.PositiveSmallIntegerField(
        'nota',
        choices=NOTAS,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    titulo = models.CharField('título da resenha', max_length=120)
    texto = models.TextField('resenha')
    criado_em = models.DateTimeField('criada em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizada em', auto_now=True)

    class Meta:
        verbose_name = 'resenha'
        verbose_name_plural = 'resenhas'
        ordering = ['-criado_em']
        constraints = [
            models.UniqueConstraint(fields=['livro', 'usuario'], name='uma_resenha_por_usuario_e_livro'),
        ]

    def __str__(self):
        return f'{self.titulo} — {self.usuario} sobre {self.livro.titulo}'

    def get_absolute_url(self):
        return self.livro.get_absolute_url() + f'#resenha-{self.pk}'
