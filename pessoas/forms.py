from __future__ import annotations

import re
from django import forms
from django.core.exceptions import ValidationError

from .models import Pessoa

def normalize_cpf(value: str) -> str:
    return re.sub(r'\D+', '', value or '')

class PessoaForm(forms.ModelForm):
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd/mm/aaaa'})
    )
    sexo = forms.ChoiceField(
        choices=Pessoa.SEXO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Somente números (11 dígitos)'}),
    )

    class Meta:
        model = Pessoa
        fields = ['nome', 'sobrenome', 'data_nascimento', 'sexo', 'cpf']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nome(self):
        nome = (self.cleaned_data.get('nome') or '').strip()
        if not nome:
            raise ValidationError('Nome não pode ser vazio.')
        return nome.title()

    def clean_sobrenome(self):
        sobrenome = (self.cleaned_data.get('sobrenome') or '').strip()
        if not sobrenome:
            raise ValidationError('Sobrenome não pode ser vazio.')
        return sobrenome.title()

    def clean_cpf(self):
        cpf = normalize_cpf(self.cleaned_data.get('cpf'))
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValidationError('Formato inválido! Digite os 11 dígitos do CPF (somente números).')
        return cpf


class BuscarCPFForm(forms.Form):
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CPF (11 dígitos)'}),
    )

    def clean_cpf(self):
        cpf = normalize_cpf(self.cleaned_data.get('cpf'))
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValidationError('Inválido! Digite os 11 dígitos do CPF.')
        return cpf


class EditarCampoBaseForm(forms.ModelForm):
    """Base para os forms de edição por campo (replicando o menu de edição do CLI)."""
    class Meta:
        model = Pessoa
        fields: list[str] = []


class EditarNomeForm(EditarCampoBaseForm):
    class Meta(EditarCampoBaseForm.Meta):
        fields = ['nome']
        widgets = {'nome': forms.TextInput(attrs={'class': 'form-control'})}

    def clean_nome(self):
        nome = (self.cleaned_data.get('nome') or '').strip()
        if not nome:
            raise ValidationError('Nome não pode ser vazio.')
        return nome.title()


class EditarSobrenomeForm(EditarCampoBaseForm):
    class Meta(EditarCampoBaseForm.Meta):
        fields = ['sobrenome']
        widgets = {'sobrenome': forms.TextInput(attrs={'class': 'form-control'})}

    def clean_sobrenome(self):
        sobrenome = (self.cleaned_data.get('sobrenome') or '').strip()
        if not sobrenome:
            raise ValidationError('Sobrenome não pode ser vazio.')
        return sobrenome.title()


class EditarNascimentoForm(EditarCampoBaseForm):
    data_nascimento = forms.DateField(
        label='Data de nascimento',
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd/mm/aaaa'})
    )

    class Meta(EditarCampoBaseForm.Meta):
        fields = ['data_nascimento']


class EditarSexoForm(EditarCampoBaseForm):
    sexo = forms.ChoiceField(
        choices=Pessoa.SEXO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(EditarCampoBaseForm.Meta):
        fields = ['sexo']


class EditarCPFForm(EditarCampoBaseForm):
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Somente números (11 dígitos)'}),
    )

    class Meta(EditarCampoBaseForm.Meta):
        fields = ['cpf']

    def clean_cpf(self):
        cpf = normalize_cpf(self.cleaned_data.get('cpf'))
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValidationError('Formato inválido! Digite os 11 dígitos do CPF (somente números).')
        return cpf


MESES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
    (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]

class MesForm(forms.Form):
    mes = forms.ChoiceField(
        label='Mês',
        choices=MESES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
