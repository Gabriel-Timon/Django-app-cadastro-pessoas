from __future__ import annotations

from datetime import date
from django.core.validators import RegexValidator
from django.db import models

cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message='CPF deve conter exatamente 11 dígitos numéricos (somente números).'
)

class Pessoa(models.Model):
    SEXO_MASC = 'M'
    SEXO_FEM = 'F'
    SEXO_CHOICES = (
        (SEXO_MASC, 'Masculino'),
        (SEXO_FEM, 'Feminino'),
    )

    nome = models.CharField(max_length=120)
    sobrenome = models.CharField(max_length=120)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    cpf = models.CharField(max_length=11, unique=True, validators=[cpf_validator])

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome', 'sobrenome']
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

    def __str__(self) -> str:
        return f"{self.nome} {self.sobrenome} ({self.cpf_formatado})"

    @property
    def cpf_formatado(self) -> str:
        cpf = (self.cpf or '').zfill(11)
        return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

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
