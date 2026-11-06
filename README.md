# Entre Páginas — Clube de Leitura

Aplicação web desenvolvida em **Django** para compartilhamento e avaliação de livros. O sistema permite que visitantes explorem o acervo literário e leiam resenhas, enquanto usuários autenticados podem cadastrar novos títulos e publicar suas próprias avaliações com notas de 1 a 5.

Projeto desenvolvido como Trabalho Final da disciplina de **Programação III**  
**Curso:** Tecnologia em Análise e Desenvolvimento de Sistemas  
**Instituição:** Instituto Federal de Educação, Ciência e Tecnologia de Rondônia (IFRO) — Campus Ariquemes  

**Desenvolvedor:**
- Matheus P. S. ([@MatheusPS-Dev](https://github.com/MatheusPS-Dev))

---

## Requisitos Implementados

| Requisito | Detalhes da Implementação |
| --- | --- |
| **Modelos e Relacionamentos** | Três entidades principais (`Genero`, `Livro` e `Resenha`) com chaves estrangeiras e integração direta com o modelo `User` do Django. |
| **Arquitetura MTV** | Separação em `models.py`, `views.py`, formulários customizados em `forms.py` e herança de templates modularizada. |
| **Django Admin** | Modelos registrados em `livros/admin.py` com filtros, busca por campos de texto e inline de resenhas na página do livro. |
| **Autenticação de Usuários** | Fluxo de cadastro (`CadastroForm`), login, logout e redirecionamento de usuários. |
| **Permissões e Segurança** | Views protegidas por `@login_required`. Validação no banco e na view garantindo que cada usuário só altere ou exclua a sua própria resenha. |
| **Deploy em Produção** | Preparado com suporte a variáveis de ambiente (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) para publicação no PythonAnywhere. |

---

## Modelo de Dados

```
User (Django) ──1:N──► Resenha ◄──N:1── Livro ──N:1──► Genero
      │                                    ▲
      └──────────────1:N (cadastrado_por)──┘
```

- **Genero:** Nome, slug para URL amigável, descrição e definição de cor temática.
- **Livro:** Título, autor, ano de publicação, sinopse, gênero e vínculo com o usuário que o cadastrou.
- **Resenha:** Nota (1 a 5), título, comentário, livro e usuário autor. Regra de unicidade garantindo uma resenha por usuário por livro (`UniqueConstraint`).

Políticas de integridade referencial (`on_delete`):
- Excluir um **livro** remove em cascata as resenhas associadas (`CASCADE`).
- Excluir um **gênero** é bloqueado caso existam livros vinculados (`PROTECT`).
- Se um **usuário** for removido, seus livros cadastrados permanecem no acervo (`SET_NULL`).

---

## Rotas da Aplicação

| Rota | Descrição | Autenticação |
| --- | --- | :---: |
| `/` | Página inicial com destaques, livros mais bem avaliados e gêneros | Pública |
| `/livros/` | Catálogo com busca textual, paginação e filtros | Pública |
| `/livros/<id>/` | Detalhes do livro, distribuição de notas e lista de resenhas | Pública |
| `/livros/novo/` | Formulário de cadastro de novo livro no acervo | Requer Login |
| `/livros/<id>/resenhar/` | Publicação de resenha e nota para um livro | Requer Login |
| `/resenhas/<id>/editar/` | Edição da resenha do próprio usuário | Requer Login |
| `/resenhas/<id>/excluir/` | Remoção da resenha do próprio usuário | Requer Login |
| `/minhas-resenhas/` | Painel com as resenhas do usuário logado | Requer Login |
| `/contas/cadastro/` | Cadastro de nova conta | Pública |
| `/contas/entrar/` | Login de usuário | Pública |
| `/admin/` | Painel administrativo do Django | Administrador |

---

## Como Executar Localmente

### Pré-requisitos
* Python 3.10 ou superior
* Git

```bash
# 1. Clonar o repositório
git clone https://github.com/MatheusPS-Dev/Atividade-Final-Prog-3.git
cd Atividade-Final-Prog-3

# 2. Criar e ativar o ambiente virtual
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Executar as migrações do banco de dados
python manage.py migrate

# 5. (Opcional) Popular o banco com dados de teste
python manage.py popular_dados

# 6. Criar um superusuário para o painel de administração
python manage.py createsuperuser

# 7. Iniciar o servidor de desenvolvimento
python manage.py runserver
```

Acesse em seu navegador: `http://127.0.0.1:8000`

---

## Testes Automatizados

O projeto conta com suíte de testes cobrindo rotas públicas, restrições de autenticação e integridade de permissões:

```bash
python manage.py test
```

---

## Estrutura do Projeto

```
config/                 Configurações gerais do projeto (settings, urls, wsgi)
livros/                 App principal do sistema
  models.py             Entidades Genero, Livro e Resenha
  views.py              Lógica das visualizações e controle de acesso
  forms.py              Formulários de validação (Cadastro, Livro, Resenha)
  urls.py               Mapeamento de rotas do app
  admin.py              Customização do painel administrativo
  tests.py              Testes unitários e de integração
  templatetags/         Filtros customizados de template
  management/commands/  Comando para carga inicial de dados
templates/
  base.html             Template base com estrutura principal
  layouts/              Templates de layout reaproveitáveis
  livros/               Templates específicos das views de livros
  registration/         Templates de login e cadastro
  partials/             Fragmentos de interface reutilizáveis
static/                 Arquivos estáticos (CSS, JS e imagens)
```

---

## Instruções para Deploy (PythonAnywhere)

1. Crie uma conta no [PythonAnywhere](https://www.pythonanywhere.com).
2. Abra um console Bash e clone o repositório:
   ```bash
   git clone https://github.com/MatheusPS-Dev/Atividade-Final-Prog-3.git
   cd Atividade-Final-Prog-3
   ```
3. Crie o virtualenv e instale os pacotes:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 entre-paginas
   pip install -r requirements.txt
   ```
4. Execute as migrações, carga de dados e coleta de estáticos:
   ```bash
   python manage.py migrate
   python manage.py popular_dados
   python manage.py createsuperuser
   python manage.py collectstatic
   ```
5. Gere uma chave secreta para a aplicação:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
6. Na aba **Web**, crie uma nova aplicação com configuração manual (Python 3.12) e preencha:
   - **Source code:** `/home/SEU_USUARIO/Atividade-Final-Prog-3`
   - **Virtualenv:** `/home/SEU_USUARIO/.virtualenvs/entre-paginas`
   - **Static files:** URL `/static/` → diretório `/home/SEU_USUARIO/Atividade-Final-Prog-3/staticfiles`
7. No arquivo **WSGI configuration**, configure:
   ```python
   import os
   import sys

   path = '/home/SEU_USUARIO/Atividade-Final-Prog-3'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
   os.environ['DJANGO_SECRET_KEY'] = 'SUA_CHAVE_GERADA'
   os.environ['DJANGO_DEBUG'] = 'False'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
8. Clique em **Reload** e acesse a URL gerada.
