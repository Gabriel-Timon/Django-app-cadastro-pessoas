from __future__ import annotations

import csv
import json
from datetime import date
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required, permission_required
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
    SignupForm,
    EditarNomeForm,
    EditarSobrenomeForm,
    EditarNascimentoForm,
    EditarSexoForm,
    EditarCPFForm,
)
from .models import DEMO_KEYS, Pessoa
from .throttling import consume_signup_attempt


view_pessoa_required = permission_required('pessoas.view_pessoa', raise_exception=True)
add_pessoa_required = permission_required('pessoas.add_pessoa', raise_exception=True)
change_pessoa_required = permission_required('pessoas.change_pessoa', raise_exception=True)
delete_pessoa_required = permission_required('pessoas.delete_pessoa', raise_exception=True)
export_pessoa_required = permission_required('pessoas.export_pessoa', raise_exception=True)


@login_not_required
def signup(request):
    if request.user.is_authenticated:
        return redirect('pessoas:dashboard')

    if request.method == 'POST':
        allowed, retry_after = consume_signup_attempt(request)
        if not allowed:
            response = render(
                request,
                'registration/signup.html',
                {
                    'form': SignupForm(),
                    'page_title': 'Criar conta',
                    'rate_limited': True,
                    'retry_after_minutes': max(1, (retry_after + 59) // 60),
                },
                status=429,
            )
            response.headers['Retry-After'] = str(retry_after)
            return response

    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Conta criada! Seu acesso é somente para consultas e dashboards.')
        return redirect('pessoas:dashboard')

    return render(
        request,
        'registration/signup.html',
        {'form': form, 'page_title': 'Criar conta'},
    )


# -------------------------
# Helpers
# -------------------------
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


def spreadsheet_safe(value):
    """Evita que planilhas interpretem texto controlado pelo usuário como fórmula."""
    if not isinstance(value, str):
        return value
    if value.startswith(('=', '+', '-', '@', '\t', '\r')):
        return f"'{value}"
    return value


def visible_pessoas(request):
    pessoas = Pessoa.objects.all()
    if not request.user.has_perm('pessoas.change_pessoa'):
        pessoas = pessoas.filter(demo_key__in=DEMO_KEYS)
    return pessoas


# -------------------------
# Menu Principal
# -------------------------
@view_pessoa_required
def dashboard(request):
    pessoas_qs = visible_pessoas(request)
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

@change_pessoa_required
def menu_edicao_cadastro(request):
    return render(request, 'pessoas/menu_edicao_cadastro.html', {'page_title': 'Editar cadastro'})


# -------------------------
# Cadastros (CRUD + Buscar CPF)
# -------------------------
@view_pessoa_required
def pessoa_list(request):
    q = (request.GET.get('q') or '').strip()
    pessoas_qs = visible_pessoas(request)

    if q:
        pessoas_qs = pessoas_qs.filter(Q(nome__icontains=q) | Q(sobrenome__icontains=q))

    context = {
        'page_title': 'Todos os cadastros',
        'page_subtitle': 'Lista completa de pessoas cadastradas',
        'pessoas': pessoas_qs.order_by('nome', 'sobrenome'),
        'q': q,
    }
    return render(request, 'pessoas/pessoas_list.html', context)

@add_pessoa_required
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

@view_pessoa_required
def pessoa_detail(request, pk: int):
    pessoa = get_object_or_404(visible_pessoas(request), pk=pk)
    return render(request, 'pessoas/pessoa_detail.html', {
        'page_title': 'Detalhes do cadastro',
        'pessoa': pessoa,
    })

@change_pessoa_required
def buscar_por_cpf(request):
    """Página única de busca por CPF.

    Use a querystring `?destino=detalhe|editar|excluir` para replicar os fluxos do menu em CLI.
    """
    destino = (request.GET.get('destino') or request.POST.get('destino') or 'detalhe').strip().lower()

    if request.method == 'POST':
        form = BuscarCPFForm(request.POST)
        if form.is_valid():
            cpf = form.cleaned_data['cpf']
            pessoa = visible_pessoas(request).filter(cpf=cpf).first()
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
@change_pessoa_required
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

@change_pessoa_required
def pessoa_edit_nome(request, pk: int):
    return _editar_campo(request, pk, EditarNomeForm, 'Editar Nome', '✅ Nome alterado com sucesso!')

@change_pessoa_required
def pessoa_edit_sobrenome(request, pk: int):
    return _editar_campo(request, pk, EditarSobrenomeForm, 'Editar Sobrenome', '✅ Sobrenome alterado com sucesso!')

@change_pessoa_required
def pessoa_edit_nascimento(request, pk: int):
    return _editar_campo(request, pk, EditarNascimentoForm, 'Editar Data de nascimento', '✅ Data de nascimento alterada com sucesso!')

@change_pessoa_required
def pessoa_edit_sexo(request, pk: int):
    return _editar_campo(request, pk, EditarSexoForm, 'Editar Sexo', '✅ Sexo alterado com sucesso!')

@change_pessoa_required
def pessoa_edit_cpf(request, pk: int):
    return _editar_campo(request, pk, EditarCPFForm, 'Editar CPF', '✅ CPF alterado com sucesso!')


# -------------------------
# Excluir
# -------------------------
@delete_pessoa_required
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
@view_pessoa_required
def menu_filtros(request):
    return render(request, 'pessoas/menu_filtros.html', {'page_title': 'Menu de filtros'})

@view_pessoa_required
def menu_estatisticas(request):
    return render(request, 'pessoas/menu_estatisticas.html', {'page_title': 'Exibir estatísticas'})

@export_pessoa_required
def menu_exportacao(request):
    return render(request, 'pessoas/menu_exportacao.html', {'page_title': 'Opções de exportação'})


# -------------------------
# Filtros (equivalentes ao CLI)
# -------------------------
@view_pessoa_required
def filtro_homens(request):
    pessoas = visible_pessoas(request).filter(sexo=Pessoa.SEXO_MASC).order_by('nome', 'sobrenome')
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir todos os Homens',
        'page_subtitle': 'Filtro: sexo masculino',
        'pessoas': pessoas,
        'q': '',
    })

@view_pessoa_required
def filtro_mulheres(request):
    pessoas = visible_pessoas(request).filter(sexo=Pessoa.SEXO_FEM).order_by('nome', 'sobrenome')
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir todas as mulheres',
        'page_subtitle': 'Filtro: sexo feminino',
        'pessoas': pessoas,
        'q': '',
    })

@view_pessoa_required
def filtro_mais_velha(request):
    pessoa = visible_pessoas(request).order_by('data_nascimento').first()
    if not pessoa:
        messages.warning(request, '⚠️ Não há cadastros ainda.')
        return redirect('pessoas:pessoa_list')
    return render(request, 'pessoas/pessoa_detail.html', {
        'page_title': 'Exibir pessoa mais velha',
        'pessoa': pessoa,
    })

@view_pessoa_required
def filtro_mais_nova(request):
    pessoa = visible_pessoas(request).order_by('-data_nascimento').first()
    if not pessoa:
        messages.warning(request, '⚠️ Não há cadastros ainda.')
        return redirect('pessoas:pessoa_list')
    return render(request, 'pessoas/pessoa_detail.html', {
        'page_title': 'Exibir pessoa mais nova',
        'pessoa': pessoa,
    })

@view_pessoa_required
def filtro_menores(request):
    hoje = date.today()
    corte = years_ago(hoje, 18)  # nasceu depois disso => menor de 18
    pessoas = visible_pessoas(request).filter(data_nascimento__gt=corte).order_by('data_nascimento')
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir pessoas com menos de 18 anos',
        'page_subtitle': f'Corte: nascidos após {corte.strftime("%d/%m/%Y")}',
        'pessoas': pessoas,
        'q': '',
    })

@view_pessoa_required
def filtro_acima_media(request):
    pessoas = list(visible_pessoas(request))
    media = calc_media_idade(pessoas)
    acima = [p for p in pessoas if p.idade > media]
    acima.sort(key=lambda p: (-p.idade, p.nome))
    return render(request, 'pessoas/pessoas_list.html', {
        'page_title': 'Exibir pessoas com idade acima da média de idade',
        'page_subtitle': f'Média atual: {media} anos',
        'pessoas': acima,
    })

@view_pessoa_required
def filtro_aniversariantes_mes(request):
    form = MesForm(request.POST or None)
    pessoas = None
    mes_escolhido = None

    if request.method == 'POST' and form.is_valid():
        mes_escolhido = int(form.cleaned_data['mes'])
        pessoas = visible_pessoas(request).filter(
            data_nascimento__month=mes_escolhido
        ).order_by('data_nascimento')
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
@view_pessoa_required
def est_total_cadastros(request):
    total = visible_pessoas(request).count()
    return render(request, 'pessoas/estatistica_total.html', {
        'page_title': 'Total de cadastros',
        'total': total,
    })

@view_pessoa_required
def est_homens_mulheres(request):
    pessoas = visible_pessoas(request)
    homens = pessoas.filter(sexo=Pessoa.SEXO_MASC).count()
    mulheres = pessoas.filter(sexo=Pessoa.SEXO_FEM).count()
    return render(request, 'pessoas/estatistica_sexo.html', {
        'page_title': 'Quantidade de homens e mulheres',
        'homens': homens,
        'mulheres': mulheres,
        'chart_data': {
            'type': 'doughnut',
            'labels': ['Homens', 'Mulheres'],
            'values': [homens, mulheres],
        },
    })

@view_pessoa_required
def est_media_idade(request):
    pessoas = list(visible_pessoas(request))
    media = calc_media_idade(pessoas)
    return render(request, 'pessoas/estatistica_media_idade.html', {
        'page_title': 'Média de idade',
        'media': media,
    })

@view_pessoa_required
def est_maiores_menores(request):
    hoje = date.today()
    corte = years_ago(hoje, 18)
    pessoas = visible_pessoas(request)
    menores = pessoas.filter(data_nascimento__gt=corte).count()
    maiores = pessoas.filter(data_nascimento__lte=corte).count()
    return render(request, 'pessoas/estatistica_maiores_menores.html', {
        'page_title': 'Quantidade de menores e maiores de idade',
        'menores': menores,
        'maiores': maiores,
        'corte': corte,
    })

@view_pessoa_required
def est_faixa_etaria(request):
    pessoas = list(visible_pessoas(request))
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
        'chart_data': {
            'type': 'bar',
            'labels': list(faixas.keys()),
            'values': list(faixas.values()),
        },
    })

@view_pessoa_required
def est_maior_menor_idade(request):
    pessoas = visible_pessoas(request)
    pessoa_mais_velha = pessoas.order_by('data_nascimento').first()
    pessoa_mais_nova = pessoas.order_by('-data_nascimento').first()
    return render(request, 'pessoas/estatistica_maior_menor_idade.html', {
        'page_title': 'Maior e menor idade',
        'mais_velha': pessoa_mais_velha,
        'mais_nova': pessoa_mais_nova,
    })

@view_pessoa_required
def est_aniversariantes_mes(request):
    qs = (
        visible_pessoas(request)
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
    'chart_data': {
        'type': 'line',
        'labels': meses,
        'values': data_chart,
    },
    })


# -------------------------
# Exportação (equivalente ao CLI)
# -------------------------
def _pessoas_to_rows(pessoas):
    pessoas = pessoas.order_by('nome', 'sobrenome')
    for p in pessoas:
        row = {
            'nome': p.nome,
            'sobrenome': p.sobrenome,
            'data_nascimento': p.data_nascimento.strftime('%d/%m/%Y'),
            'sexo': p.sexo_extenso,
            'cpf': p.cpf_mascarado,
            'idade': p.idade,
        }
        yield {key: spreadsheet_safe(value) for key, value in row.items()}

@export_pessoa_required
def export_csv(request):
    dados = list(_pessoas_to_rows(visible_pessoas(request)))
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

@export_pessoa_required
def export_json(request):
    dados = list(_pessoas_to_rows(visible_pessoas(request)))
    if not dados:
        messages.error(request, '❌ Não há cadastros para exportar.')
        return redirect('pessoas:menu_exportacao')

    response = HttpResponse(
        json.dumps(dados, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="pessoas.json"'
    return response

@export_pessoa_required
def export_xlsx(request):
    dados = list(_pessoas_to_rows(visible_pessoas(request)))
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
