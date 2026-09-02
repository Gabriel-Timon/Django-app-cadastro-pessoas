from __future__ import annotations

import hashlib
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pessoas.models import DEMO_KEYS, DEMO_RECORD_COUNT, Pessoa


DEMO_MARKER = 'Demonstração'
DEMO_REFERENCE_DATE = date(2026, 1, 1)
AGES_PER_GENDER = (6, 9, 12, 15, 17, 18, 21, 24, 27, 29, 31, 35, 39, 43, 47, 51, 56, 61, 66, 71, 76, 82, 88, 94, 99)
FEMALE_NAMES = (
    'Alice', 'Beatriz', 'Camila', 'Daniela', 'Elisa', 'Fernanda', 'Gabriela',
    'Helena', 'Isabela', 'Júlia', 'Larissa', 'Mariana', 'Natália', 'Olívia',
    'Patrícia', 'Rafaela', 'Sabrina', 'Talita', 'Valentina', 'Yasmin', 'Bianca',
    'Clara', 'Eduarda', 'Luana', 'Renata',
)
MALE_NAMES = (
    'Arthur', 'Bernardo', 'Caio', 'Diego', 'Eduardo', 'Felipe', 'Gustavo',
    'Henrique', 'Igor', 'João', 'Kauã', 'Leonardo', 'Matheus', 'Nicolas',
    'Otávio', 'Pedro', 'Rafael', 'Samuel', 'Thiago', 'Vinícius', 'Bruno',
    'Davi', 'Enzo', 'Lucas', 'Marcelo',
)


def _cpf_from_base(base: str) -> str:
    digits = [int(digit) for digit in base]
    for size in (9, 10):
        total = sum(
            digit * weight
            for digit, weight in zip(digits[:size], range(size + 1, 1, -1))
        )
        verifier = (total * 10) % 11
        digits.append(0 if verifier == 10 else verifier)
    return ''.join(str(digit) for digit in digits)


def _demo_cpf(index: int) -> str:
    digest = hashlib.sha256(f'portfolio-cadastro-pessoas-demo-v1:{index}'.encode()).hexdigest()
    base = f'{int(digest[:16], 16) % 1_000_000_000:09d}'
    if len(set(base)) == 1:
        base = f'{index * 7919:09d}'[-9:]
    return _cpf_from_base(base)


def _birth_date_for_age(age: int, index: int) -> date:
    month = (index % 12) + 1
    day = ((index * 7) % 28) + 1
    year = DEMO_REFERENCE_DATE.year - age
    if (month, day) > (DEMO_REFERENCE_DATE.month, DEMO_REFERENCE_DATE.day):
        year -= 1
    return date(year, month, day)


def demo_records():
    records = []
    index = 0
    for gender, names in (
        (Pessoa.SEXO_FEM, FEMALE_NAMES),
        (Pessoa.SEXO_MASC, MALE_NAMES),
    ):
        for name, age in zip(names, AGES_PER_GENDER):
            index += 1
            records.append(
                {
                    'demo_key': DEMO_KEYS[index - 1],
                    'nome': name,
                    'sobrenome': f'{DEMO_MARKER} {index:02d}',
                    'data_nascimento': _birth_date_for_age(age, index),
                    'sexo': gender,
                    'cpf': _demo_cpf(index),
                }
            )
    return records


class Command(BaseCommand):
    help = 'Cria ou atualiza 50 pessoas inequivocamente fictícias para a demonstração do portfólio.'

    @transaction.atomic
    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        unchanged_count = 0

        # Serializa execuções concorrentes no PostgreSQL usando uma linha estável.
        content_type = ContentType.objects.get_for_model(Pessoa)
        ContentType.objects.select_for_update().get(pk=content_type.pk)

        for record in demo_records():
            pessoa = Pessoa.objects.select_for_update().filter(
                demo_key=record['demo_key']
            ).first()
            cpf_owner = Pessoa.objects.filter(cpf=record['cpf']).exclude(
                demo_key=record['demo_key']
            ).first()
            if cpf_owner:
                raise CommandError(
                    'Um identificador sintético colidiu com um cadastro não demonstrativo. '
                    'Nenhum registro foi alterado.'
                )

            if pessoa is None:
                pessoa = Pessoa(**record)
                pessoa.full_clean()
                pessoa.save()
                created_count += 1
            else:
                changed_fields = []
                for field, value in record.items():
                    if getattr(pessoa, field) != value:
                        setattr(pessoa, field, value)
                        changed_fields.append(field)

                if changed_fields:
                    pessoa.full_clean()
                    pessoa.save(update_fields=[*changed_fields, 'atualizado_em'])
                    updated_count += 1
                else:
                    unchanged_count += 1

        if len(DEMO_KEYS) != DEMO_RECORD_COUNT:
            raise CommandError('Configuração inconsistente dos identificadores demo.')

        self.stdout.write(
            self.style.SUCCESS(
                f'Dados demo prontos: {DEMO_RECORD_COUNT} registros ({created_count} criados, '
                f'{updated_count} atualizados, {unchanged_count} inalterados), '
                'com 25 pessoas de cada gênero suportado.'
            )
        )
