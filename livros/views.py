from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CadastroForm, LivroForm, ResenhaForm
from .models import Genero, Livro, Resenha


def livros_com_notas():
    """Livros já com a média das notas e o número de resenhas calculados pelo banco."""
    return Livro.objects.select_related('genero').annotate(
        media=Avg('resenhas__nota'),
        total_resenhas=Count('resenhas'),
    )


# ---------------------------------------------------------------------------
# Páginas públicas: qualquer visitante pode ver
# ---------------------------------------------------------------------------

MINIMO_RESENHAS_RANKING = 2  # uma única nota 5 não basta para liderar o ranking


def inicio(request):
    # ranking: melhor média entre os livros com pelo menos 2 resenhas
    ranking = (
        livros_com_notas()
        .filter(total_resenhas__gte=MINIMO_RESENHAS_RANKING)
        .order_by('-media', '-total_resenhas', 'titulo')[:6]
    )
    contexto = {
        'resenhas_recentes': Resenha.objects.select_related('livro__genero', 'usuario')[:4],
        'mais_bem_avaliados': ranking,
        'destaque': ranking[0] if ranking else None,  # a frase do topo usa o 1º do ranking
        'minimo_ranking': MINIMO_RESENHAS_RANKING,
        'novos_livros': Livro.objects.select_related('genero').order_by('-criado_em', '-pk')[:6],
        'generos': Genero.objects.annotate(total_livros=Count('livros')),
        'total_resenhas': Resenha.objects.count(),
        'total_livros': Livro.objects.count(),
    }
    return render(request, 'livros/inicio.html', contexto)


ORDENACOES = {
    'titulo': ('Título', ['titulo']),
    'nota': ('Melhor nota', [F('media').desc(nulls_last=True), 'titulo']),
    'resenhas': ('Mais resenhados', ['-total_resenhas', 'titulo']),
    'recentes': ('Cadastrados por último', ['-criado_em', '-pk']),
}


def lista_livros(request):
    livros = livros_com_notas()

    genero_ativo = None
    slug = request.GET.get('genero')
    if slug:
        genero_ativo = get_object_or_404(Genero, slug=slug)
        livros = livros.filter(genero=genero_ativo)

    busca = request.GET.get('q', '').strip()
    if busca:
        livros = livros.filter(Q(titulo__icontains=busca) | Q(autor__icontains=busca))

    ordem = request.GET.get('ordem', 'titulo')
    if ordem not in ORDENACOES:
        ordem = 'titulo'
    livros = livros.order_by(*ORDENACOES[ordem][1])

    pagina = Paginator(livros, 10).get_page(request.GET.get('pagina'))
    contexto = {
        'pagina': pagina,
        'genero_ativo': genero_ativo,
        'busca': busca,
        'ordem': ordem,
        'ordenacoes': [(chave, rotulo) for chave, (rotulo, _) in ORDENACOES.items()],
        'generos': Genero.objects.all(),
    }
    return render(request, 'livros/lista.html', contexto)


def detalhe_livro(request, pk):
    livro = get_object_or_404(livros_com_notas().select_related('cadastrado_por'), pk=pk)
    resenhas = livro.resenhas.select_related('usuario')

    # quantas resenhas deram cada nota (5 até 1), para o gráfico de barras
    # (order_by() vazio tira a ordenação padrão, que atrapalharia o agrupamento)
    contagem = dict(
        livro.resenhas.order_by().values('nota').annotate(total=Count('id')).values_list('nota', 'total')
    )
    maior = max(contagem.values(), default=0)
    distribuicao = [
        {
            'nota': nota,
            'total': contagem.get(nota, 0),
            'largura': round(contagem.get(nota, 0) / maior * 100) if maior else 0,
        }
        for nota in range(5, 0, -1)
    ]

    minha_resenha = None
    if request.user.is_authenticated:
        minha_resenha = resenhas.filter(usuario=request.user).first()

    contexto = {
        'livro': livro,
        'resenhas': resenhas,
        'distribuicao': distribuicao,
        'minha_resenha': minha_resenha,
    }
    return render(request, 'livros/detalhe.html', contexto)


def cadastro(request):
    """Inscrição de um novo usuário. Depois de criar a conta, ele já entra logado."""
    if request.user.is_authenticated:
        return redirect('livros:inicio')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'Conta criada. Boas-vindas, {usuario.first_name}!')
            return redirect('livros:inicio')
    else:
        form = CadastroForm()
    return render(request, 'registration/cadastro.html', {'form': form})


# ---------------------------------------------------------------------------
# Ações restritas: só para quem está logado (@login_required)
# Quem não está logado é mandado para a tela de login (settings.LOGIN_URL).
# ---------------------------------------------------------------------------

@login_required
def novo_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            livro = form.save(commit=False)
            livro.cadastrado_por = request.user
            livro.save()
            messages.success(request, f'“{livro.titulo}” entrou no acervo.')
            return redirect(livro)
    else:
        form = LivroForm(initial={'genero': request.GET.get('genero')})
    return render(request, 'livros/livro_form.html', {'form': form})


@login_required
def nova_resenha(request, pk):
    livro = get_object_or_404(Livro.objects.select_related('genero'), pk=pk)

    existente = Resenha.objects.filter(livro=livro, usuario=request.user).first()
    if existente:
        messages.info(request, 'Você já resenhou este livro. Aqui você pode editar a sua resenha.')
        return redirect('livros:editar_resenha', pk=existente.pk)

    if request.method == 'POST':
        form = ResenhaForm(request.POST)
        if form.is_valid():
            resenha = form.save(commit=False)
            resenha.livro = livro
            resenha.usuario = request.user
            resenha.save()
            messages.success(request, 'Resenha publicada.')
            return redirect(resenha)
    else:
        form = ResenhaForm()
    return render(request, 'livros/resenha_form.html', {'form': form, 'livro': livro})


@login_required
def editar_resenha(request, pk):
    # filtrar por usuario=request.user garante que ninguém edita a resenha de outra pessoa
    resenha = get_object_or_404(Resenha.objects.select_related('livro__genero'), pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = ResenhaForm(request.POST, instance=resenha)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resenha atualizada.')
            return redirect(resenha)
    else:
        form = ResenhaForm(instance=resenha)
    return render(request, 'livros/resenha_form.html', {'form': form, 'livro': resenha.livro, 'resenha': resenha})


@login_required
def excluir_resenha(request, pk):
    resenha = get_object_or_404(Resenha.objects.select_related('livro'), pk=pk, usuario=request.user)

    if request.method == 'POST':
        livro = resenha.livro
        resenha.delete()
        messages.success(request, f'Sua resenha sobre “{livro.titulo}” foi excluída.')
        return redirect('livros:minhas_resenhas')
    return render(request, 'livros/resenha_excluir.html', {'resenha': resenha})


@login_required
def minhas_resenhas(request):
    resenhas = request.user.resenhas.select_related('livro__genero')
    resumo = resenhas.aggregate(media=Avg('nota'), total=Count('id'))
    return render(request, 'livros/minhas_resenhas.html', {'resenhas': resenhas, 'resumo': resumo})
