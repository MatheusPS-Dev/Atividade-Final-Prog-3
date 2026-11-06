"""Testes automáticos. Rode com:  python manage.py test"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Genero, Livro, Resenha


class BaseTeste(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genero = Genero.objects.create(nome='Fantasia', slug='fantasia', tom='rosa')
        cls.outro_genero = Genero.objects.create(nome='Tecnologia', slug='tecnologia', tom='teal')
        cls.ana = User.objects.create_user('ana', password='senha-de-teste-123', first_name='Ana')
        cls.bruno = User.objects.create_user('bruno', password='senha-de-teste-123', first_name='Bruno')
        cls.livro = Livro.objects.create(titulo='O Hobbit', autor='J. R. R. Tolkien', genero=cls.genero, ano_publicacao=1937)
        cls.livro_tec = Livro.objects.create(titulo='Código Limpo', autor='Robert C. Martin', genero=cls.outro_genero)
        cls.resenha_ana = Resenha.objects.create(livro=cls.livro, usuario=cls.ana, nota=4, titulo='Boa aventura', texto='Gostei.')


class PaginasPublicasTeste(BaseTeste):
    """Quem não está logado consegue navegar e ler."""

    def test_inicio_lista_e_detalhe_abrem_sem_login(self):
        for url in [reverse('livros:inicio'), reverse('livros:lista'), reverse('livros:detalhe', args=[self.livro.pk])]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_lista_filtra_por_genero(self):
        resposta = self.client.get(reverse('livros:lista'), {'genero': 'tecnologia'})
        self.assertContains(resposta, 'Código Limpo')
        self.assertNotContains(resposta, 'O Hobbit')

    def test_lista_busca_por_titulo_ou_autor(self):
        resposta = self.client.get(reverse('livros:lista'), {'q': 'tolkien'})
        self.assertContains(resposta, 'O Hobbit')
        self.assertNotContains(resposta, 'Código Limpo')

    def test_detalhe_mostra_media_das_notas(self):
        Resenha.objects.create(livro=self.livro, usuario=self.bruno, nota=5, titulo='Ótimo', texto='Muito bom.')
        resposta = self.client.get(reverse('livros:detalhe', args=[self.livro.pk]))
        self.assertContains(resposta, '4,5')  # (4 + 5) / 2, com vírgula por causa do pt-br


class AcoesRestritasTeste(BaseTeste):
    """Item 3 do enunciado: quem não está logado não pode fazer certas ações."""

    def test_visitante_e_mandado_para_o_login(self):
        urls = [
            reverse('livros:novo_livro'),
            reverse('livros:nova_resenha', args=[self.livro.pk]),
            reverse('livros:editar_resenha', args=[self.resenha_ana.pk]),
            reverse('livros:excluir_resenha', args=[self.resenha_ana.pk]),
            reverse('livros:minhas_resenhas'),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f"{reverse('login')}?next={url}")

    def test_visitante_nao_consegue_publicar_resenha(self):
        self.client.post(reverse('livros:nova_resenha', args=[self.livro_tec.pk]),
                         {'nota': 5, 'titulo': 'Spam', 'texto': 'Spam'})
        self.assertFalse(Resenha.objects.filter(livro=self.livro_tec).exists())

    def test_usuario_logado_publica_resenha(self):
        self.client.force_login(self.bruno)
        resposta = self.client.post(reverse('livros:nova_resenha', args=[self.livro.pk]),
                                    {'nota': 5, 'titulo': 'Clássico', 'texto': 'Recomendo.'})
        resenha = Resenha.objects.get(livro=self.livro, usuario=self.bruno)
        self.assertRedirects(resposta, resenha.get_absolute_url(), fetch_redirect_response=False)

    def test_usuario_logado_cadastra_livro_em_seu_nome(self):
        self.client.force_login(self.bruno)
        self.client.post(reverse('livros:novo_livro'), {
            'titulo': 'Duna', 'autor': 'Frank Herbert', 'genero': self.genero.pk, 'ano_publicacao': 1965, 'sinopse': '',
        })
        self.assertEqual(Livro.objects.get(titulo='Duna').cadastrado_por, self.bruno)

    def test_uma_resenha_por_livro(self):
        self.client.force_login(self.ana)
        resposta = self.client.get(reverse('livros:nova_resenha', args=[self.livro.pk]))
        self.assertRedirects(resposta, reverse('livros:editar_resenha', args=[self.resenha_ana.pk]))

    def test_ninguem_edita_ou_exclui_resenha_de_outra_pessoa(self):
        self.client.force_login(self.bruno)
        editar = self.client.post(reverse('livros:editar_resenha', args=[self.resenha_ana.pk]),
                                  {'nota': 1, 'titulo': 'Hackeado', 'texto': 'x'})
        excluir = self.client.post(reverse('livros:excluir_resenha', args=[self.resenha_ana.pk]))
        self.assertEqual(editar.status_code, 404)
        self.assertEqual(excluir.status_code, 404)
        self.resenha_ana.refresh_from_db()
        self.assertEqual(self.resenha_ana.titulo, 'Boa aventura')

    def test_dono_exclui_a_propria_resenha(self):
        self.client.force_login(self.ana)
        self.client.post(reverse('livros:excluir_resenha', args=[self.resenha_ana.pk]))
        self.assertFalse(Resenha.objects.filter(pk=self.resenha_ana.pk).exists())


class CadastroTeste(TestCase):
    """Item 2 do enunciado: o usuário consegue se inscrever no site."""

    def test_cadastro_cria_usuario_e_ja_entra_logado(self):
        resposta = self.client.post(reverse('cadastro'), {
            'first_name': 'Carla', 'username': 'carla', 'email': 'carla@example.com',
            'password1': 'umaSenhaBemForte!42', 'password2': 'umaSenhaBemForte!42',
        })
        self.assertRedirects(resposta, reverse('livros:inicio'))
        self.assertTrue(User.objects.filter(username='carla').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='carla').pk)

    def test_cadastro_recusa_senhas_diferentes(self):
        self.client.post(reverse('cadastro'), {
            'first_name': 'Carla', 'username': 'carla', 'email': 'carla@example.com',
            'password1': 'umaSenhaBemForte!42', 'password2': 'outraSenha!42',
        })
        self.assertFalse(User.objects.filter(username='carla').exists())
