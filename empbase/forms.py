from django import forms
from .models import Funcionario

'''class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        exclude = ['cod', 'demissao', 'demitido', 'usuario', 'emp', 'ativa']
        widgets = {
            'admissao': forms.DateInput(attrs={'type': 'date'}),
            'ctpsdata': forms.DateInput(attrs={'type': 'date'}),
            'rgemiss': forms.DateInput(attrs={'type': 'date'}),
            'datanasc': forms.DateInput(attrs={'type': 'date'}),
        }

        fieldsets = [
        ('Group 1', {'fields': ['nome', 'cpf', 'pis', 'admissao', 'salario', 'cargo', 'cbo', 'turno']}),
        ('Group 2', {'fields': ['rg', 'rgemiss', 'rgorgao', 'ctps', 'ctpsserie', 'ctpsdata', 'ctpsuf']}),
        ('Group 3', {'fields': ['logradouro', 'num', 'bairro', 'cidade', 'uf', 'cep']}),
        ('Group 4', {'fields': [ 'pai', 'mae', 'datanasc', 'cidadenasc', 'ufnasc', 'genero']}),
        ]'''


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        exclude = ['cod', 'demissao', 'demitido', 'usuario', 'emp', 'ativa']
        widgets = {
            'admissao': forms.DateInput(attrs={'type': 'date'}),
            'ctpsdata': forms.DateInput(attrs={'type': 'date'}),
            'rgemiss': forms.DateInput(attrs={'type': 'date'}),
            'datanasc': forms.DateInput(attrs={'type': 'date'}),
        }

        labels = {
            'nome': 'Nome',
            'cpf': 'CPF',
            'pis': 'PIS/PASEP',
            'admissao': 'Data de Admissão',
            'salario': 'Salário',
            'cargo': 'Cargo',
            'cbo': 'CBO',
            'rg': 'RG',
            'rgemiss': 'Emissão do RG',
            'rgorgao': 'Órgão Emissor do RG',
            'ctps': 'Nº da CTPS',
            'ctpsserie': 'Série da CTPS',
            'ctpsdata': 'Emissão da CTPS',
            'ctpsuf': 'UF da CTPS',
            'turno': 'Turno de Trabalho',
            'logradouro': 'Logradouro',
            'num': 'Número',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'uf': 'UF',
            'cep': 'CEP',
            'datanasc': 'Data de Nascimento',
            'cidadenasc': 'Cidade de Nascimento',
            'ufnasc': 'UF de Nascimento',
            'genero': 'Gênero',
            'pai': 'Nome do Pai',
            'mae': 'Nome da Mãe',
        }

    def __init__(self, *args, **kwargs):
        super(FuncionarioForm, self).__init__(*args, **kwargs)
        self.fields['pai'].required = False
        self.fields['pis'].required = False
        self.fields['ctps'].required = False
        self.fields['ctpsserie'].required = False
        self.fields['ctpsdata'].required = False
        self.fields['ctpsuf'].required = False