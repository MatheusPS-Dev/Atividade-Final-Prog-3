from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Livro, Resenha


class CadastroForm(UserCreationForm):
    """Formulário de inscrição no site: o UserCreationForm do Django com nome e e-mail."""

    first_name = forms.CharField(label='Seu nome', max_length=150)
    email = forms.EmailField(label='E-mail')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'username', 'email']
        labels = {'username': 'Nome de usuário'}


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'genero', 'ano_publicacao', 'sinopse']
        widgets = {
            'sinopse': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_ano_publicacao(self):
        ano = self.cleaned_data.get('ano_publicacao')
        if ano and ano > date.today().year:
            raise forms.ValidationError('O ano de publicação não pode estar no futuro.')
        return ano


class ResenhaForm(forms.ModelForm):
    class Meta:
        model = Resenha
        fields = ['nota', 'titulo', 'texto']
        widgets = {
            'nota': forms.RadioSelect,
            'texto': forms.Textarea(attrs={'rows': 8}),
        }
        labels = {'texto': 'Sua resenha'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tira a opção vazia "---------" que o Django coloca nos campos com choices
        self.fields['nota'].choices = Resenha.NOTAS
