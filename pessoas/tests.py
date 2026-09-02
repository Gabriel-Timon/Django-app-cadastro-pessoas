import json
from datetime import date
from io import BytesIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from .forms import PessoaForm
from .models import Pessoa


class PessoaModelTests(TestCase):
    def test_properties_format_cpf_translate_sexo_and_calculate_age(self):
        hoje = date.today()
        pessoa = Pessoa(
            nome='Ana',
            sobrenome='Silva',
            data_nascimento=date(hoje.year - 30, hoje.month, hoje.day),
            sexo=Pessoa.SEXO_FEM,
            cpf='12345678901',
        )

        self.assertEqual(pessoa.cpf_formatado, '123.456.789-01')
        self.assertEqual(pessoa.sexo_extenso, 'Feminino')
        self.assertEqual(pessoa.idade, 30)
        self.assertEqual(str(pessoa), 'Ana Silva (123.456.789-01)')


class PessoaFormTests(TestCase):
    def test_form_normalizes_names_and_formatted_cpf(self):
        form = PessoaForm(
            data={
                'nome': '  ana  ',
                'sobrenome': ' silva ',
                'data_nascimento': '10/02/1990',
                'sexo': Pessoa.SEXO_FEM,
                'cpf': '123.456.789-01',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        pessoa = form.save()

        self.assertEqual(pessoa.nome, 'Ana')
        self.assertEqual(pessoa.sobrenome, 'Silva')
        self.assertEqual(pessoa.cpf, '12345678901')

    def test_form_rejects_invalid_cpf_and_empty_name(self):
        form = PessoaForm(
            data={
                'nome': ' ',
                'sobrenome': 'Silva',
                'data_nascimento': '10/02/1990',
                'sexo': Pessoa.SEXO_FEM,
                'cpf': '123',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
        self.assertIn('cpf', form.errors)


class SeedCommandTests(TestCase):
    def test_seed_command_is_idempotent(self):
        call_command('seed_pessoas')
        quantidade_inicial = Pessoa.objects.count()

        call_command('seed_pessoas')

        self.assertGreater(quantidade_inicial, 0)
        self.assertEqual(Pessoa.objects.count(), quantidade_inicial)


class PessoaViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pessoa = Pessoa.objects.create(
            nome='Ana',
            sobrenome='Silva',
            data_nascimento=date(1990, 1, 10),
            sexo=Pessoa.SEXO_FEM,
            cpf='12345678901',
        )
        cls.outro = Pessoa.objects.create(
            nome='Bruno',
            sobrenome='Santos',
            data_nascimento=date(1985, 5, 20),
            sexo=Pessoa.SEXO_MASC,
            cpf='98765432109',
        )

    def test_dashboard_displays_summary(self):
        response = self.client.get(reverse('pessoas:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], 2)
        self.assertEqual(response.context['homens'], 1)
        self.assertEqual(response.context['mulheres'], 1)
        self.assertContains(response, 'Menu Principal')

    def test_list_search_accepts_formatted_cpf(self):
        response = self.client.get(
            reverse('pessoas:pessoa_list'),
            {'q': '123.456.789-01'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana')
        self.assertNotContains(response, 'Bruno')

    def test_create_view_persists_person_and_redirects_to_detail(self):
        response = self.client.post(
            reverse('pessoas:pessoa_create'),
            {
                'nome': 'carla',
                'sobrenome': 'souza',
                'data_nascimento': '01/01/2000',
                'sexo': Pessoa.SEXO_FEM,
                'cpf': '11122233344',
            },
        )

        pessoa = Pessoa.objects.get(cpf='11122233344')
        self.assertRedirects(
            response,
            reverse('pessoas:pessoa_detail', kwargs={'pk': pessoa.pk}),
        )
        self.assertEqual(pessoa.nome, 'Carla')

    def test_edit_name_view_updates_person(self):
        response = self.client.post(
            reverse('pessoas:pessoa_edit_nome', kwargs={'pk': self.pessoa.pk}),
            {'nome': 'beatriz'},
        )

        self.assertRedirects(
            response,
            reverse('pessoas:pessoa_detail', kwargs={'pk': self.pessoa.pk}),
        )
        self.pessoa.refresh_from_db()
        self.assertEqual(self.pessoa.nome, 'Beatriz')

    def test_search_by_cpf_redirects_to_person_detail(self):
        response = self.client.post(
            reverse('pessoas:buscar_por_cpf'),
            {'cpf': '123.456.789-01'},
        )

        self.assertRedirects(
            response,
            reverse('pessoas:pessoa_detail', kwargs={'pk': self.pessoa.pk}),
        )

    def test_delete_view_removes_person(self):
        response = self.client.post(
            reverse('pessoas:pessoa_delete', kwargs={'pk': self.outro.pk}),
        )

        self.assertRedirects(response, reverse('pessoas:pessoa_list'))
        self.assertFalse(Pessoa.objects.filter(pk=self.outro.pk).exists())

    def test_filter_and_statistics_views(self):
        response = self.client.get(reverse('pessoas:filtro_homens'))
        self.assertContains(response, 'Bruno')
        self.assertNotContains(response, 'Ana')

        response = self.client.get(reverse('pessoas:est_total_cadastros'))
        self.assertContains(response, '2')

    def test_export_views_return_expected_formats(self):
        csv_response = self.client.get(reverse('pessoas:export_csv'))
        self.assertEqual(csv_response.status_code, 200)
        self.assertTrue(csv_response['Content-Type'].startswith('text/csv'))
        self.assertIn('Ana', csv_response.content.decode('utf-8'))

        json_response = self.client.get(reverse('pessoas:export_json'))
        self.assertEqual(json_response.status_code, 200)
        self.assertEqual(json.loads(json_response.content)[0]['nome'], 'Ana')

        xlsx_response = self.client.get(reverse('pessoas:export_xlsx'))
        self.assertEqual(xlsx_response.status_code, 200)
        workbook = load_workbook(BytesIO(xlsx_response.content), read_only=True)
        self.assertEqual(workbook.sheetnames, ['Pessoas'])
        self.assertEqual(workbook.active['A2'].value, 'Ana')
        workbook.close()
