from __future__ import annotations

from datetime import datetime
from django.core.management.base import BaseCommand
from pessoas.models import Pessoa

SEED = [
    # nome, sobrenome, data_nascimento (dd/mm/aaaa), sexo, cpf
    ("gabriel", "timon", "03/09/1999", "M", "16559687775"),
    ("sérgio", "timon", "23/12/1965", "M", "92738461520"),
    ("júlia", "lanzoni", "12/07/2004", "F", "48195027633"),
    ("cassiane", "lanzoni", "03/02/1969", "F", "58900217020"),
    ("arthur", "timon", "01/01/2015", "M", "73019462855"),
    ("miguel", "lanzoni", "01/01/2019", "M", "60294718301"),
    ("mariana", "souza", "15/05/1995", "F", "19485720366"),
    ("roberto", "almeida", "22/11/1988", "M", "53820697144"),
    ("fernanda", "pereira", "09/03/2002", "F", "71549286013"),
    ("lucas", "oliveira", "30/08/2010", "M", "40928573691"),
    ("beatriz", "costa", "17/04/1997", "F", "86031749205"),
    ("joao", "silva", "05/06/1980", "M", "27590148362"),
    ("carla", "mendes", "27/10/1975", "F", "91467235088"),
    ("thiago", "ferreira", "11/01/2008", "M", "36850917420"),
    ("patricia", "rocha", "19/09/1992", "F", "59281473066"),
    ("vinicius", "ribeiro", "02/02/2001", "M", "80732619455"),
    ("camila", "lima", "14/12/1999", "F", "15693074281"),
    ("eduardo", "martins", "25/07/1985", "M", "67420591837"),
    ("isabela", "barbosa", "08/08/2016", "F", "31985720644"),
    ("gustavo", "carvalho", "03/03/1990", "M", "90214673851"),
    ("aline", "dias", "21/06/2006", "F", "48017593622"),
    ("rafael", "santos", "10/10/1970", "M", "61594820733"),
    ("daniela", "castro", "28/02/1983", "F", "29374615089"),
    ("pedro", "nascimento", "07/07/2012", "M", "74192860511"),
    ("leticia", "teixeira", "16/11/2009", "F", "50937186244"),
    ("bruno", "gomes", "01/04/1994", "M", "86730491572"),
]

class Command(BaseCommand):
    help = 'Popula o banco com dados de exemplo (equivalente ao seed() do projeto em CLI).'

    def handle(self, *args, **options):
        criados = 0
        for nome, sobrenome, nasc_str, sexo, cpf in SEED:
            dt = datetime.strptime(nasc_str, '%d/%m/%Y').date()
            obj, created = Pessoa.objects.get_or_create(
                cpf=cpf,
                defaults={
                    'nome': nome.title(),
                    'sobrenome': sobrenome.title(),
                    'data_nascimento': dt,
                    'sexo': sexo,
                }
            )
            if created:
                criados += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Seed concluído: {criados} novos cadastros criados.'))
