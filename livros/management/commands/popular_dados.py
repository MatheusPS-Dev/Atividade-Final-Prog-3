"""Comando: python manage.py popular_dados

Preenche o banco com DADOS DE EXEMPLO (gêneros, livros, leitores e resenhas) para o site
não começar vazio na apresentação. Pode ser executado mais de uma vez sem duplicar nada.

Os leitores de exemplo são criados SEM senha utilizável: ninguém consegue entrar com eles.
Para testar o login, crie sua própria conta pelo site ou com "createsuperuser".
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from livros.models import Genero, Livro, Resenha

GENEROS = [
    ('Literatura brasileira', 'literatura-brasileira', 'verde',
     'Romances e contos brasileiros, dos clássicos aos contemporâneos.'),
    ('Ficção científica', 'ficcao-cientifica', 'azul',
     'Futuros possíveis, viagens espaciais e sociedades imaginadas.'),
    ('Fantasia', 'fantasia', 'rosa',
     'Mundos inventados, magia, dragões e longas jornadas de herói.'),
    ('Tecnologia', 'tecnologia', 'teal',
     'Programação, algoritmos e boas práticas para quem estuda ADS.'),
    ('Não ficção', 'nao-ficcao', 'grafite',
     'História, ciência e ideias sobre o mundo real, de quem pesquisa.'),
]

# (título, autor, slug do gênero, ano, sinopse)
LIVROS = [
    ('Dom Casmurro', 'Machado de Assis', 'literatura-brasileira', 1899,
     'Bento Santiago, já velho, conta a própria vida e tenta provar que Capitu o traiu. '
     'Como só temos a versão dele, o leitor precisa decidir em quem acreditar.'),
    ('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 'literatura-brasileira', 1881,
     'Um defunto resolve escrever suas memórias e, livre de qualquer vergonha, '
     'comenta com ironia a sociedade do Rio de Janeiro do século XIX.'),
    ('Vidas Secas', 'Graciliano Ramos', 'literatura-brasileira', 1938,
     'Fabiano, Sinhá Vitória, os dois meninos e a cachorra Baleia fogem da seca '
     'pelo sertão nordestino, em capítulos curtos e secos como a paisagem.'),
    ('A Hora da Estrela', 'Clarice Lispector', 'literatura-brasileira', 1977,
     'Um narrador tenta contar a história de Macabéa, uma moça alagoana que vive '
     'quase invisível no Rio de Janeiro.'),
    ('Torto Arado', 'Itamar Vieira Junior', 'literatura-brasileira', 2019,
     'Duas irmãs crescem numa fazenda do sertão baiano, marcadas por um acidente '
     'de infância e pela luta dos trabalhadores pela terra.'),
    ('Duna', 'Frank Herbert', 'ficcao-cientifica', 1965,
     'Paul Atreides chega ao planeta desértico Arrakis, única fonte da especiaria '
     'mais valiosa do universo, e se vê no centro de uma disputa entre impérios.'),
    ('Fundação', 'Isaac Asimov', 'ficcao-cientifica', 1951,
     'Um matemático prevê a queda do Império Galáctico e cria um plano para '
     'encurtar a era de barbárie que virá depois dela.'),
    ('1984', 'George Orwell', 'ficcao-cientifica', 1949,
     'Winston Smith trabalha reescrevendo o passado para um governo que vigia tudo '
     'e começa, em segredo, a duvidar do Grande Irmão.'),
    ('Neuromancer', 'William Gibson', 'ficcao-cientifica', 1984,
     'Um hacker decadente recebe uma última chance de voltar ao ciberespaço '
     'em troca de um trabalho perigoso.'),
    ('O Hobbit', 'J. R. R. Tolkien', 'fantasia', 1937,
     'Bilbo Bolseiro sai do conforto de sua toca para ajudar um grupo de anões '
     'a recuperar o tesouro guardado pelo dragão Smaug.'),
    ('O Nome do Vento', 'Patrick Rothfuss', 'fantasia', 2007,
     'Kvothe, hoje dono de uma estalagem, conta como foi de menino de uma trupe '
     'de artistas a estudante da Universidade e lenda viva.'),
    ('Código Limpo', 'Robert C. Martin', 'tecnologia', 2008,
     'Princípios e exemplos para escrever código fácil de ler e de manter: '
     'nomes claros, funções pequenas e testes.'),
    ('O Programador Pragmático', 'Andrew Hunt e David Thomas', 'tecnologia', 1999,
     'Conselhos práticos sobre a carreira e o dia a dia de quem desenvolve software, '
     'do controle de versão à automação.'),
    ('Entendendo Algoritmos', 'Aditya Y. Bhargava', 'tecnologia', 2016,
     'Busca binária, recursão, grafos e programação dinâmica explicados com '
     'desenhos e exemplos simples.'),
    ('Sapiens', 'Yuval Noah Harari', 'nao-ficcao', 2011,
     'Uma história da humanidade desde os primeiros Homo sapiens até hoje, '
     'passando pela agricultura, o dinheiro e a ciência.'),
]

# (username, nome)
LEITORES = [
    ('ana.souza', 'Ana'),
    ('bruno.lima', 'Bruno'),
    ('carla.mendes', 'Carla'),
    ('diego.rocha', 'Diego'),
]

# (username, título do livro, nota, título da resenha, texto, há quantos dias)
RESENHAS = [
    ('ana.souza', 'Duna', 5, 'Vale cada página do começo lento',
     'As primeiras cem páginas exigem paciência, com muitos nomes e casas nobres. Depois que a '
     'família chega a Arrakis o livro não para mais. A ecologia do planeta é o que mais me marcou.', 1),
    ('bruno.lima', 'Código Limpo', 4, 'Mudou o jeito que eu nomeio variáveis',
     'Li durante a disciplina de Programação III e comecei a aplicar na hora: funções menores e '
     'nomes que explicam o que fazem. Alguns exemplos em Java parecem datados, mas a ideia continua valendo.', 2),
    ('carla.mendes', 'Vidas Secas', 5, 'Curto, duro e inesquecível',
     'Graciliano não desperdiça uma palavra. O capítulo da Baleia é um dos mais tristes que já li. '
     'Dá para ler em uma tarde e pensar nele por semanas.', 3),
    ('diego.rocha', 'Duna', 4, 'Política no deserto',
     'Gostei mais das intrigas entre as casas do que das batalhas. O final ficou meio corrido, '
     'mas já comecei a continuação.', 4),
    ('ana.souza', 'Dom Casmurro', 5, 'Capitu traiu? Eu ainda não sei',
     'Reli depois do ensino médio e foi outra experiência. Bentinho é um narrador em quem não dá '
     'para confiar, e perceber isso é o melhor do livro.', 6),
    ('bruno.lima', 'Entendendo Algoritmos', 5, 'O livro que eu queria ter lido antes',
     'Os desenhos tornam busca em largura e programação dinâmica fáceis de visualizar. '
     'Recomendo para quem está pegando Estrutura de Dados.', 8),
    ('carla.mendes', 'O Hobbit', 4, 'Aventura leve e divertida',
     'Mais simples que O Senhor dos Anéis, quase um livro infantil, e isso é um elogio. '
     'A conversa de enigmas com o Gollum é ótima.', 9),
    ('diego.rocha', '1984', 5, 'Assustadoramente atual',
     'Escrito em 1949 e parece falar de hoje: vigilância, notícias reescritas, palavras sendo '
     'apagadas. A terceira parte é muito pesada.', 11),
    ('ana.souza', 'A Hora da Estrela', 4, 'Pequeno e estranho',
     'O narrador fala mais de si do que da Macabéa no começo, e isso me incomodou. '
     'Mas quando a história engrena, ela fica na cabeça.', 13),
    ('bruno.lima', 'Fundação', 3, 'Ideia genial, personagens rasos',
     'A psico-história é um conceito incrível. Só que os personagens trocam a cada capítulo '
     'e eu não consegui me apegar a nenhum.', 14),
    ('carla.mendes', 'Torto Arado', 5, 'O melhor que li este ano',
     'Bibiana e Belonísia são personagens fortes, e a parte narrada pela terceira voz me pegou '
     'de surpresa. Uma leitura importante sobre terra e trabalho.', 16),
    ('diego.rocha', 'O Programador Pragmático', 4, 'Bons conselhos para o estágio',
     'Alguns capítulos são óbvios hoje, mas as ideias de não repetir código e automatizar '
     'tarefas me ajudaram no estágio.', 18),
    ('ana.souza', 'Sapiens', 3, 'Interessante, mas generaliza demais',
     'A parte sobre a revolução agrícola rende boas discussões. Em vários momentos o autor '
     'afirma coisas grandes com pouca base.', 20),
    ('bruno.lima', 'Memórias Póstumas de Brás Cubas', 4, 'Machado sendo irônico',
     'Os capítulos curtíssimos e as conversas com o leitor deixam a leitura rápida. '
     'O capítulo das negativas no final é genial.', 23),
    ('carla.mendes', 'Duna', 5, 'Ficção científica de verdade',
     'Religião, economia e ecologia no mesmo livro. Entendi por que tanta gente considera '
     'Duna o maior clássico do gênero.', 25),
    ('diego.rocha', 'Neuromancer', 3, 'Difícil de acompanhar',
     'O estilo é cheio de gírias e cenas rápidas. Admiro a importância histórica, '
     'mas tive que voltar várias páginas.', 27),
    ('ana.souza', 'Código Limpo', 5, 'Leitura obrigatória em ADS',
     'Depois desse livro passei a revisar meu código antes de entregar os trabalhos. '
     'Os capítulos sobre funções e comentários são os mais úteis.', 29),
    ('bruno.lima', 'O Nome do Vento', 5, 'Não consegui largar',
     'A escrita é bonita e a parte da Universidade é a minha favorita. '
     'Só não leia se não aguentar esperar pelo terceiro livro.', 31),
    ('bruno.lima', 'Dom Casmurro', 5, 'Os olhos de ressaca',
     'Comecei por obrigação e terminei discutindo o final com a turma inteira. '
     'Machado escreve frases curtas que dizem muito mais do que parecem.', 5),
    ('diego.rocha', 'Entendendo Algoritmos', 5, 'Finalmente entendi recursão',
     'O capítulo de recursão com a caixa dentro de caixas resolveu uma dúvida que eu tinha desde '
     'Algoritmos I. Leitura rápida e cheia de exemplos.', 7),
    ('bruno.lima', 'Duna', 5, 'Mundo construído com cuidado',
     'Cada detalhe de Arrakis tem uma razão de existir, da água guardada nos trajes aos vermes '
     'gigantes. Releria fácil.', 10),
    ('diego.rocha', 'Vidas Secas', 4, 'A seca vista por dentro',
     'Os capítulos podem ser lidos quase separados, o que deixa a leitura leve apesar do tema. '
     'Fabiano tentando falar e não conseguindo diz muito.', 12),
    ('carla.mendes', '1984', 4, 'Perturbador do jeito certo',
     'A novilíngua e a ideia de apagar palavras para apagar ideias me fizeram pensar muito. '
     'O romance de Winston é a parte mais fraca.', 15),
    ('ana.souza', 'O Hobbit', 5, 'Perfeito para ler nas férias',
     'Tolkien conta a história como se estivesse lendo em voz alta para alguém. '
     'Smaug é um dos melhores vilões que já encontrei.', 17),
    ('diego.rocha', 'Torto Arado', 4, 'Começo forte, meio lento',
     'O mistério da faca no começo prende demais. No meio a narrativa desacelera, '
     'mas o final compensa.', 19),
    ('ana.souza', 'Fundação', 4, 'Melhor do que eu esperava',
     'É mais um livro de ideias do que de ação, com muita conversa e pouca batalha. '
     'Gostei de ver o plano funcionando ao longo dos séculos.', 22),
    ('carla.mendes', 'Sapiens', 2, 'Não me convenceu',
     'Lê fácil, mas várias afirmações ficam sem fonte. Prefiro livros de história '
     'que mostram de onde tiraram cada conclusão.', 26),
]


class Command(BaseCommand):
    help = 'Cria gêneros, livros, leitores e resenhas de exemplo.'

    @transaction.atomic
    def handle(self, *args, **options):
        generos = {}
        for nome, slug, tom, descricao in GENEROS:
            generos[slug], _ = Genero.objects.update_or_create(
                slug=slug, defaults={'nome': nome, 'tom': tom, 'descricao': descricao},
            )

        leitores = {}
        for username, nome in LEITORES:
            usuario, criado = User.objects.get_or_create(username=username, defaults={'first_name': nome})
            if criado:
                usuario.set_unusable_password()  # conta de exemplo: não dá para entrar com ela
                usuario.save()
            leitores[username] = usuario

        agora = timezone.now()
        livros = {}
        for indice, (titulo, autor, slug, ano, sinopse) in enumerate(LIVROS):
            livro, criado = Livro.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'autor': autor, 'genero': generos[slug], 'ano_publicacao': ano,
                    'sinopse': sinopse, 'cadastrado_por': leitores[LEITORES[indice % len(LEITORES)][0]],
                },
            )
            if criado:  # espalha as datas de cadastro pelas últimas semanas
                Livro.objects.filter(pk=livro.pk).update(criado_em=agora - timedelta(days=40 - indice * 2))
            livros[titulo] = livro

        novas = 0
        for username, titulo_livro, nota, titulo, texto, dias in RESENHAS:
            resenha, criada = Resenha.objects.get_or_create(
                livro=livros[titulo_livro], usuario=leitores[username],
                defaults={'nota': nota, 'titulo': titulo, 'texto': texto},
            )
            if criada:
                Resenha.objects.filter(pk=resenha.pk).update(criado_em=agora - timedelta(days=dias, hours=dias * 3))
                novas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Pronto: {len(generos)} gêneros, {len(livros)} livros, {len(leitores)} leitores '
            f'e {novas} resenhas novas.'
        ))
