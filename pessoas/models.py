from __future__ import annotations

from datetime import date
import re

from django.core.exceptions import ValidationError
from django.db import models


DEMO_KEY_PREFIX = 'portfolio-demo-'
DEMO_RECORD_COUNT = 50
DEMO_KEYS = tuple(
    f'{DEMO_KEY_PREFIX}{index:03d}' for index in range(1, DEMO_RECORD_COUNT + 1)
)


def validate_cpf(value: str) -> None:
    cpf = value or ''
    if not re.fullmatch(r'[0-9]{11}', cpf):
        raise ValidationError('CPF deve conter exatamente 11 dígitos ASCII.')
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')

    for tamanho in (9, 10):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf[:tamanho], range(tamanho + 1, 1, -1)))
        verificador = (soma * 10) % 11
        if verificador == 10:
            verificador = 0
        if verificador != int(cpf[tamanho]):
            raise ValidationError('CPF inválido.')


def validate_data_nascimento(value: date) -> None:
    if value > date.today():
        raise ValidationError('A data de nascimento não pode estar no futuro.')
    if value < date(1900, 1, 1):
        raise ValidationError('A data de nascimento deve ser posterior a 01/01/1900.')

class Pessoa(models.Model):
    SEXO_MASC = 'M'
    SEXO_FEM = 'F'
    SEXO_CHOICES = (
        (SEXO_MASC, 'Masculino'),
        (SEXO_FEM, 'Feminino'),
    )

    nome = models.CharField(max_length=120)
    sobrenome = models.CharField(max_length=120)
    data_nascimento = models.DateField(validators=[validate_data_nascimento])
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    cpf = models.CharField(max_length=11, unique=True, validators=[validate_cpf])
    demo_key = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        help_text='Identificador interno de registros sintéticos do portfólio.',
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome', 'sobrenome']
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        permissions = [
            ('export_pessoa', 'Pode exportar pessoas'),
        ]

    def __str__(self) -> str:
        return f"{self.nome} {self.sobrenome} ({self.cpf_mascarado})"

    @property
    def cpf_formatado(self) -> str:
        cpf = (self.cpf or '').zfill(11)
        return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

    @property
    def cpf_mascarado(self) -> str:
        return f'***.***.***-{(self.cpf or "").zfill(11)[-2:]}'

    @property
    def idade(self) -> int:
        """Idade em anos completos (mesma regra do seu projeto em CLI)."""
        if not self.data_nascimento:
            return 0
        hoje = date.today()
        nascimento = self.data_nascimento
        idade = hoje.year - nascimento.year
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1
        return int(idade)

    @property
    def sexo_extenso(self) -> str:
        return dict(self.SEXO_CHOICES).get(self.sexo, self.sexo)


class SignupThrottle(models.Model):
    key_hash = models.CharField(max_length=64, unique=True, editable=False)
    window_started_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = 'Limite de cadastro'
        verbose_name_plural = 'Limites de cadastro'

    def __str__(self) -> str:
        return f'Limite de cadastro ({self.attempts} tentativas)'
