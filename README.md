# Entre Páginas

Clube de leitura on-line feito em **Django**: visitantes navegam pelo acervo e leem as resenhas, e leitores com conta escrevem resenhas com nota de 1 a 5 e cadastram livros novos.

Trabalho Final de **Programação III** — Análise e Desenvolvimento de Sistemas, IFRO Campus Ariquemes (2026.2).

## Onde cada item do enunciado está

| Item do enunciado | Onde está no projeto |
| --- | --- |
| **1.** Três ou mais tabelas com chave estrangeira, sendo uma o `User` do Django | `livros/models.py`: `Genero` → `Livro` → `Resenha`, e `Resenha.usuario` e `Livro.cadastrado_por` apontam para o `User` |
| **1.** Models, Templates com herança, Views e rotas | `livros/models.py`, `templates/` (`base.html` → `layouts/formulario.html` → páginas), `livros/views.py`, `livros/urls.py` e `config/urls.py` |
| **1.** Models registrados no admin | `livros/admin.py` (os três models, com busca, filtros e as resenhas dentro da página do livro) |
| **2.** O usuário pode se inscrever | View `cadastro` em `livros/views.py`, formulário `CadastroForm` em `livros/forms.py`, página `/contas/cadastro/` |
| **3.** Quem não está logado não pode fazer certas ações | `@login_required` em cadastrar livro, escrever, editar e excluir resenha e "Minhas resenhas". Além disso, ninguém edita a resenha de outra pessoa (`get_object_or_404(..., usuario=request.user)`) |
| **4.** Deploy no PythonAnywhere | Passo a passo em [Deploy no PythonAnywhere](#deploy-no-pythonanywhere) |
| **5.** Apresentação gravada | Roteiro sugerido em [Roteiro para a apresentação](#roteiro-para-a-apresentação) |

## Modelo de dados

```
User (do Django) ──1:N──► Resenha ◄──N:1── Livro ──N:1──► Genero
      │                                      ▲
      └──────────────1:N (cadastrado_por)────┘
```

- **Genero**: nome, slug (usado na URL), descrição e a cor das capas.
- **Livro**: título, autor, ano, sinopse, o gênero e quem cadastrou.
- **Resenha**: nota de 1 a 5, título e texto, o livro e o usuário que escreveu. Cada usuário escreve **uma** resenha por livro (`UniqueConstraint`).

O que cada `on_delete` faz:

- apagar um **livro** apaga as resenhas dele (`CASCADE`);
- um **gênero** que ainda tem livros não pode ser apagado (`PROTECT`);
- se um **usuário** for apagado, os livros que ele cadastrou continuam no acervo (`SET_NULL`).

## Páginas

| Rota | Página | Precisa de login? |
| --- | --- | --- |
| `/` | Início: resenhas recentes, ranking, livros novos e gêneros | Não |
| `/livros/` | Lista com filtro por gênero, busca e ordenação | Não |
| `/livros/<id>/` | Livro: média, distribuição das notas, sinopse e resenhas | Não |
| `/livros/novo/` | Cadastrar livro | **Sim** |
| `/livros/<id>/resenhar/` | Escrever resenha | **Sim** |
| `/resenhas/<id>/editar/` e `/excluir/` | Editar ou excluir a **própria** resenha | **Sim** |
| `/minhas-resenhas/` | Resenhas do usuário logado | **Sim** |
| `/contas/cadastro/`, `/contas/entrar/` | Criar conta e entrar | Não |
| `/admin/` | Administração do Django | Superusuário |

## Como rodar no computador

Precisa do Python 3.10 ou mais novo (o projeto foi feito com o 3.12).

```bash
# 1. Baixar o projeto
git clone https://github.com/MatheusPS-Dev/Atividade-Final-Prog-3.git
cd Atividade-Final-Prog-3

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux ou macOS

# 3. Instalar o Django
pip install -r requirements.txt

# 4. Criar o banco de dados e, se quiser, os dados de exemplo
python manage.py migrate
python manage.py popular_dados

# 5. Criar um usuário para entrar no /admin
python manage.py createsuperuser

# 6. Rodar
python manage.py runserver
```

Depois é só abrir <http://127.0.0.1:8000>.

**Dados de exemplo:** o comando `popular_dados` cria 5 gêneros, 15 livros, 4 leitores fictícios (Ana, Bruno, Carla e Diego) e 27 resenhas. Os leitores fictícios **não têm senha** e ninguém consegue entrar com eles. Para testar o login, crie a sua conta pelo site. O comando pode ser executado de novo sem duplicar nada.

### Testes automáticos

```bash
python manage.py test
```

São 13 testes. Eles conferem que as páginas públicas abrem sem login, que o filtro e a busca funcionam, que um visitante é mandado para o login nas ações restritas, que ninguém edita ou exclui a resenha de outra pessoa e que o cadastro cria a conta e já faz o login.

## Estrutura de pastas

```
config/                 configurações do projeto (settings.py, urls.py, wsgi.py)
livros/                 o app do site
  models.py             Genero, Livro e Resenha
  views.py              as páginas (funções)
  forms.py              formulários de cadastro, livro e resenha
  urls.py               rotas do app
  admin.py              registro no admin
  tests.py              testes automáticos
  templatetags/         filtros usados nos templates (estrelas, cor do avatar)
  management/commands/  comando popular_dados
templates/
  base.html             esqueleto de todas as páginas (menu lateral, avisos, rodapé)
  layouts/formulario.html  herda do base; usado por todas as telas de formulário
  livros/               páginas do app
  registration/         entrar e criar conta
  partials/             pedaços reaproveitados (capa, estrelas, ícones, campo)
static/css/estilo.css   todo o visual do site
static/js/site.js       menu no celular e ordenação automática da lista
```

## Deploy no PythonAnywhere

1. Crie uma conta gratuita (*Beginner*) em <https://www.pythonanywhere.com>.
2. No painel, abra **Consoles → Bash** e baixe o projeto:

   ```bash
   git clone https://github.com/MatheusPS-Dev/Atividade-Final-Prog-3.git
   cd Atividade-Final-Prog-3
   ```

3. Crie o ambiente virtual e instale as dependências. Use a versão de Python mais nova que aparecer no PythonAnywhere (3.10 ou superior):

   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 entre-paginas
   pip install -r requirements.txt
   ```

4. Prepare o banco e os arquivos estáticos:

   ```bash
   python manage.py migrate
   python manage.py popular_dados
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

5. Gere uma chave secreta e guarde o resultado para o passo 7:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

6. Vá em **Web → Add a new web app → Manual configuration**, escolha a **mesma versão de Python** do passo 3 e preencha:
   - **Source code:** `/home/SEU_USUARIO/Atividade-Final-Prog-3`
   - **Virtualenv:** `/home/SEU_USUARIO/.virtualenvs/entre-paginas`
   - **Static files:** URL `/static/` → diretório `/home/SEU_USUARIO/Atividade-Final-Prog-3/staticfiles`

7. Ainda na aba **Web**, abra o **WSGI configuration file**, apague o conteúdo e cole:

   ```python
   import os
   import sys

   path = '/home/SEU_USUARIO/Atividade-Final-Prog-3'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
   os.environ['DJANGO_SECRET_KEY'] = 'COLE_AQUI_A_CHAVE_DO_PASSO_5'
   os.environ['DJANGO_DEBUG'] = 'False'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

8. Clique em **Reload** e abra `https://SEU_USUARIO.pythonanywhere.com`.

Para publicar mudanças depois: no console Bash, `cd Atividade-Final-Prog-3`, `workon entre-paginas`, `git pull`, `python manage.py migrate`, `python manage.py collectstatic` e **Reload** na aba Web.

No plano gratuito, o PythonAnywhere desliga o site se ninguém renovar. Entre no painel de vez em quando e clique no botão de estender o prazo na aba **Web**, principalmente perto da data da apresentação.

## Roteiro para a apresentação

Uma sugestão de ordem para o vídeo (item 5):

1. **O site funcionando.** Navegar sem login (início, lista com filtro e busca, página de um livro), tentar escrever uma resenha e cair na tela de login, criar uma conta, escrever, editar e excluir uma resenha e cadastrar um livro.
2. **O admin.** Mostrar os três models registrados, com busca, filtros e as resenhas dentro da página do livro.
3. **O código.**
   - Os models e as chaves estrangeiras, incluindo a ligação com o `User` e a escolha de cada `on_delete`.
   - As views: `@login_required` e o filtro `usuario=request.user`, que impede editar a resenha de outra pessoa.
   - A herança de templates em três níveis: `base.html` → `layouts/formulario.html` → página.
   - A média e a contagem de notas calculadas pelo banco com `Avg` e `Count`.
4. **O que foi mais desafiador.** Possíveis pontos:
   - impedir que alguém edite a resenha de outra pessoa (o `@login_required` sozinho não basta);
   - garantir uma resenha por usuário e por livro (`UniqueConstraint` e o redirecionamento para a edição);
   - calcular média e ranking sem deixar um livro com uma única nota 5 liderar;
   - preparar as configurações para o deploy (`SECRET_KEY` e `DEBUG` por variável de ambiente, `collectstatic`).
