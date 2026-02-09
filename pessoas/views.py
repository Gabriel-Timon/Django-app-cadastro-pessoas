from __future__ import annotations

import csv
import json
import re
from datetime import date
from io import BytesIO

from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from openpyxl import Workbook

from .forms import (
    BuscarCPFForm,
    MesForm,
    PessoaForm,
    EditarNomeForm,
    EditarSobrenomeForm,
    EditarNascimentoForm,
    EditarSexoForm,
    EditarCPFForm,
)
from .models import Pessoa


# -------------------------
# Helpers
# -------------------------
def normalize_cpf(value: str) -> str:
    return re.sub(r'\D+', '', value or '')

def years_ago(d: date, years: int) -> date:
    """Retorna uma data equivalente a 'd - years', ajustando 29/02 quando necessário."""
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        # Ex.: 29/02 -> 28/02
        return d.replace(month=2, day=28, year=d.year - years)

def calc_media_idade(pessoas: list[Pessoa]) -> float:
    if not pessoas:
        return 0.0
    return round(sum(p.idade for p in pessoas) / len(pessoas), 1)


# -------------------------
# Menu Principal
# -------------------------
def dashboard(request):
    pessoas_qs = Pessoa.objects.all()
    pessoas = list(pessoas_qs)
    total = len(pessoas)
    homens = sum(1 for p in pessoas if p.sexo == Pessoa.SEXO_MASC)
    mulheres = sum(1 for p in pessoas if p.sexo == Pessoa.SEXO_FEM)
    media_idade = calc_media_idade(pessoas)

    context = {
        'page_title': 'Menu Principal',
        'total': total,
        'homens': homens,
        'mulheres': mulheres,
        'media_idade': media_idade,
    }
    return render(request, 'pessoas/dashboard.html', context)

def sair(request):
    return render(request, 'pessoas/sair.html', {'page_title': 'Sair'})


# -------------------------
# Editar cadastro (menu equivalente ao CLI)
# -------------------------

def menu_edicao_cadastro(request):
    return render(request, 'pessoas/menu_edicao_cadastro.html', {'page_title': 'Editar cadastro'})


# -------------------------
# Cadastros (CRUD + Buscar CPF)
# -------------------------
def pessoa_list(request):
    q = (request.GET.get('q') or '').strip()
    pessoas_qs = Pessoa.objects.all()

    if q:
        q_norm = normalize_cpf(q)
        if q_norm.isdigit() and len(q_norm) == 11:
            pessoas_qs = pessoas_qs.filter(cpf=q_norm)
        else:
            pessoas_qs = pessoas_qs.filter(Q(nome__icontains=q) | Q(sobrenome__icontains=q))

    context = {
        'page_title': 'Todos os cadastros',
        'page_subtitle': 'Lista completa de pessoas cadastradas',
        'pessoas': pessoas_qs.order_by('nome', 'sobrenome'),
        'q': q,
    }
    return render(request, 'pessoas/pessoas_list.html', context)

def pessoa_create(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, '✅ Pessoa cadastrada com sucesso!')
            return redirect('pessoas:pessoa_detail', pk=pessoa.pk)
        messages.error(request, '❌ Corrija os erros do formulário.')
    else:
        form = PessoaForm()

    return render(request, 'pessoas/pessoa_form.html', {
        'page_title': 'Adicionar mais pessoas',
        'form': form,
        'submit_label': 'Cadastrar',
    })

def pessoa_detail(request, pk: int):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    return render(request, 'pessoas/pessoa_detail.html', {
        'page_title': 'Detalhes do cadastro',
        'pessoa': pessoa,
    })

def buscar_por_cpf(request):
    """Página única de busca por CPF.

    Use a querystring `?destino=detalhe|editar|excluir` para replicar os fluxos do menu em CLI.
    """
    destino = (request.GET.get('destino') or request.POST.get('destino') or 'detalhe').strip().lower()

    if request.method == 'POST':
        form = BuscarCPFForm(request.POST)
        if form.is_valid():
            cpf = form.cleaned_data['cpf']
            pessoa = Pessoa.objects.filter(cpf=cpf).first()
            if pessoa:
                messages.success(request, '✅ Cadastro encontrado!')

                if destino == 'editar':
                    return redirect('pessoas:pessoa_edicao_menu', pk=pessoa.pk)
                if destino == 'excluir':
                    return redirect('pessoas:pessoa_delete', pk=pessoa.pk)
                return redirect('pessoas:pessoa_detail', pk=pessoa.pk)

            messages.error(request, '❌ CPF não encontrado.')
    else:
        form = BuscarCPFForm()

    return render(request, 'pessoas/pessoa_buscar_cpf.html', {
        'page_title': 'Pesquisar por CPF',
        'form': form,
        'destino': destino,
    })


# -------------------------
# Edição (menu + edição por campo)
# -------------------------
def pessoa_edicao_menu(request, pk: int):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    return render(request, 'pessoas/pessoa_edicao_menu.html', {
        'page_title': 'Opções de edição',
        'pessoa': pessoa,
    })

def _editar_campo(request, pk: int, form_class, titulo: str, sucesso_msg: str):
    pessoa = get_object_or_404(Pessoa, pk=pk)

    if request.method == 'POST':
        form = form_class(request.POST, instance=pessoa)
        if form.is_valid():
            form.save()
            messages.success(request, sucesso_msg)
            return redirect('pessoas:pessoa_detail', pk=pessoa.pk)
        messages.error(request, '❌ Corrija os erros do formulário.')
    else:
        form = form_class(instance=pessoa)

    return render(request, 'pessoas/pessoa_field_form.html', {
        'page_title': titulo,
        'pessoa': pessoa,
        'form': form,
        'submit_label': 'Salvar alteração',
    })

def pessoa_edit_nome(request, pk: int):
    return _editar_campo(request, pk, EditarNomeForm, 'Editar Nome', '✅ Nome alterado com sucesso!')

def pessoa_edit_sobrenome(request, pk: int):
    return _editar_campo(request, pk, EditarSobrenomeForm, 'Editar Sobrenome', '✅ Sobrenome alterado com sucesso!')

def pessoa_edit_nascimento(request, pk: int):
    return _editar_campo(request, pk, EditarNascimentoForm, 'Editar Data de nascimento', '✅ Data de nascimento alterada com sucesso!')

def pessoa_edit_sexo(request, pk: int):
    return _editar_campo(request, pk, EditarSexoForm, 'Editar Sexo', '✅ Sexo alterado com sucesso!')

def pessoa_edit_cpf(request, pk: int):
    return _editar_campo(request, pk, EditarCPFForm, 'Editar CPF', '✅ CPF alterado com sucesso!')


# -------------------------
# Excluir
# -------------------------
def pessoa_delete(request, pk: int):
    pessoa = get_object_or_404(Pessoa, pk=pk)

    if request.method == 'POST':
        nome = str(pessoa)
        pessoa.delete()
        messages.success(request, f'✅ Cadastro removido com sucesso: {nome}')
        return redirect('pessoas:pessoa_list')

    return render(request, 'pessoas/pessoa_confirm_delete.html', {
        'page_title': 'Excluir uma pessoa',
        'pessoa': pessoa,
    })


# -------------------------
# Menus: Filtros / Estatísticas / Exportação
# -------------------------
def menu_filtros(request):
    return render(request, 'pessoas/menu_filtros.html', {'page_title': 'Menu de filtros'})

def menu_estatisticas(request):
    return render(request, 'pessoas/menu_estatisticas.html', {'page_title': 'Exibir estatísticas'})

def menu_exportacao(request):
    return render(request, 'pessoas/menu_exportacao.html', {'page_title': 'Opções de exportação'})


# -------------------------
# Filtros (equivalentes ao CLI)
# -------------------------
def filtro_homens(request):
    pessoas = Pessoa.objects.filter(sexo=Pessoa.SEXO_MASC).order_by('nome', 'sobrenome')
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir todos os Homens',
        'page_subtitle': 'Filtro: sexo masculino',
        'pessoas': pessoas,
        'q': '',
    })

def filtro_mulheres(request):
    pessoas = Pessoa.objects.filter(sexo=Pessoa.SEXO_FEM).order_by('nome', 'sobrenome')
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir todas as mulheres',
        'page_subtitle': 'Filtro: sexo feminino',
        'pessoas': pessoas,
        'q': '',
    })

def filtro_mais_velha(request):
    pessoa = Pessoa.objects.order_by('data_nascimento').first()
    if not pessoa:
        messages.warning(request, '⚠️ Não há cadastros ainda.')
        return redirect('pessoas:pessoa_list')
    return render(request, 'pessoas/pessoa_detail.html', {
        'page_title': 'Exibir pessoa mais velha',
        'pessoa': pessoa,
    })

def filtro_mais_nova(request):
    pessoa = Pessoa.objects.order_by('-data_nascimento').first()
    if not pessoa:
        messages.warning(request, '⚠️ Não há cadastros ainda.')
        return redirect('pessoas:pessoa_list')
    return render(request, 'pessoas/pessoa_detail.html', {
        'page_title': 'Exibir pessoa mais nova',
        'pessoa': pessoa,
    })

def filtro_menores(request):
    hoje = date.today()
    corte = years_ago(hoje, 18)  # nasceu depois disso => menor de 18
    pessoas = Pessoa.objects.filter(data_nascimento__gt=corte).order_by('data_nascimento')
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir pessoas com menos de 18 anos',
        'page_subtitle': f'Corte: nascidos após {corte.strftime("%d/%m/%Y")}',
        'pessoas': pessoas,
        'q': '',
    })

def filtro_acima_media(request):
    pessoas = list(Pessoa.objects.all())
    media = calc_media_idade(pessoas)
    acima = [p for p in pessoas if p.idade > media]
    acima.sort(key=lambda p: (-p.idade, p.nome))
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir pessoas com idade acima da média de idade',
        'page_subtitle': f'Média atual: {media} anos',
        'pessoas': acima,
    })

def filtro_aniversariantes_mes(request):
    form = MesForm(request.POST or None)
    pessoas = None
    mes_escolhido = None

    if request.method == 'POST' and form.is_valid():
        mes_escolhido = int(form.cleaned_data['mes'])
        pessoas = Pessoa.objects.filter(data_nascimento__month=mes_escolhido).order_by('data_nascimento')
        if not pessoas.exists():
            messages.info(request, 'ℹ️ Não há aniversariantes neste mês.')

    return render(request, 'pessoas/aniversariantes_mes.html', {
        'page_title': 'Exibir pessoas que fazem aniversário no mesmo mês',
        'form': form,
        'pessoas': pessoas,
        'mes_escolhido': mes_escolhido,
    })


# -------------------------
# Estatísticas (equivalentes ao CLI)
# -------------------------
def est_total_cadastros(request):
    total = Pessoa.objects.count()
    return render(request, 'pessoas/estatistica_total.html', {
        'page_title': 'Total de cadastros',
        'total': total,
    })

def est_homens_mulheres(request):
    homens = Pessoa.objects.filter(sexo=Pessoa.SEXO_MASC).count()
    mulheres = Pessoa.objects.filter(sexo=Pessoa.SEXO_FEM).count()
    return render(request, 'pessoas/estatistica_sexo.html', {
        'page_title': 'Quantidade de homens e mulheres',
        'homens': homens,
        'mulheres': mulheres,
    })

def est_media_idade(request):
    pessoas = list(Pessoa.objects.all())
    media = calc_media_idade(pessoas)
    return render(request, 'pessoas/estatistica_media_idade.html', {
        'page_title': 'Média de idade',
        'media': media,
    })

def est_maiores_menores(request):
    hoje = date.today()
    corte = years_ago(hoje, 18)
    menores = Pessoa.objects.filter(data_nascimento__gt=corte).count()
    maiores = Pessoa.objects.filter(data_nascimento__lte=corte).count()
    return render(request, 'pessoas/estatistica_maiores_menores.html', {
        'page_title': 'Quantidade de menores e maiores de idade',
        'menores': menores,
        'maiores': maiores,
        'corte': corte,
    })

def est_faixa_etaria(request):
    pessoas = list(Pessoa.objects.all())
    faixa_0_17 = sum(1 for p in pessoas if 0 <= p.idade <= 17)
    faixa_18_29 = sum(1 for p in pessoas if 18 <= p.idade <= 29)
    faixa_30_49 = sum(1 for p in pessoas if 30 <= p.idade <= 49)
    faixa_50_mais = sum(1 for p in pessoas if p.idade >= 50)

    faixas = {
        '0-17': faixa_0_17,
        '18-29': faixa_18_29,
        '30-49': faixa_30_49,
        '50+': faixa_50_mais,
    }
    return render(request, 'pessoas/estatistica_faixa_etaria.html', {
        'page_title': 'Quantidade por faixa etária',
        'faixas': faixas,
        'labels': list(faixas.keys()),
        'values': list(faixas.values()),
    })

def est_maior_menor_idade(request):
    pessoa_mais_velha = Pessoa.objects.order_by('data_nascimento').first()
    pessoa_mais_nova = Pessoa.objects.order_by('-data_nascimento').first()
    return render(request, 'pessoas/estatistica_maior_menor_idade.html', {
        'page_title': 'Maior e menor idade',
        'mais_velha': pessoa_mais_velha,
        'mais_nova': pessoa_mais_nova,
    })

def est_aniversariantes_mes(request):
    qs = (
        Pessoa.objects
        .annotate(mes=ExtractMonth('data_nascimento'))
        .values('mes')
        .annotate(qtd=Count('id'))
        .order_by('mes')
    )
    contagem = {i: 0 for i in range(1, 13)}
    for row in qs:
        contagem[int(row['mes'])] = int(row['qtd'])

    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    data_chart = [contagem[i] for i in range(1, 13)]

    linhas = [
    {"mes": meses[i-1], "qtd": contagem[i]}
    for i in range(1, 13)
    ]

    return render(request, 'pessoas/estatistica_aniversariantes_mes.html', {
    'page_title': 'Aniversariantes por mês',
    'meses': meses,
    'data_chart': data_chart,
    'contagem': contagem,
    'linhas': linhas,   # <-- add
    })


# -------------------------
# Exportação (equivalente ao CLI)
# -------------------------
def _pessoas_to_rows():
    pessoas = Pessoa.objects.all().order_by('nome', 'sobrenome')
    for p in pessoas:
        yield {
            'nome': p.nome,
            'sobrenome': p.sobrenome,
            'data_nascimento': p.data_nascimento.strftime('%d/%m/%Y'),
            'sexo': p.sexo_extenso,
            'cpf': (p.cpf or '').zfill(11),
            'idade': p.idade,
        }

def export_csv(request):
    dados = list(_pessoas_to_rows())
    if not dados:
        messages.error(request, '❌ Não há cadastros para exportar.')
        return redirect('pessoas:menu_exportacao')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="pessoas.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow(dados[0].keys())
    for row in dados:
        writer.writerow([row[k] for k in dados[0].keys()])

    return response

def export_json(request):
    dados = list(_pessoas_to_rows())
    if not dados:
        messages.error(request, '❌ Não há cadastros para exportar.')
        return redirect('pessoas:menu_exportacao')

    response = HttpResponse(
        json.dumps(dados, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="pessoas.json"'
    return response

def export_xlsx(request):
    dados = list(_pessoas_to_rows())
    if not dados:
        messages.error(request, '❌ Não há cadastros para exportar.')
        return redirect('pessoas:menu_exportacao')

    wb = Workbook()
    ws = wb.active
    ws.title = 'Pessoas'

    headers = list(dados[0].keys())
    ws.append(headers)
    for row in dados:
        ws.append([row[h] for h in headers])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="pessoas.xlsx"'
    return response
