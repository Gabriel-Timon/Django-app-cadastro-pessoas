from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Menus principais (equivalentes aos menus do CLI)
    path('filtros/', views.menu_filtros, name='menu_filtros'),
    path('cadastro/', views.menu_edicao_cadastro, name='menu_edicao_cadastro'),
    path('estatisticas/', views.menu_estatisticas, name='menu_estatisticas'),
    path('exportacao/', views.menu_exportacao, name='menu_exportacao'),
    path('sair/', views.sair, name='sair'),

    # Cadastros (listar / criar / detalhe)
    path('pessoas/', views.pessoa_list, name='pessoa_list'),
    path('pessoas/nova/', views.pessoa_create, name='pessoa_create'),
    path('pessoas/<int:pk>/', views.pessoa_detail, name='pessoa_detail'),

    # Buscar por CPF (replica a opção "Pesquisar por CPF" do CLI)
    path('cadastro/buscar/', views.buscar_por_cpf, name='buscar_por_cpf'),

    # Edição por campo (menu "O que deseja editar?")
    path('pessoas/<int:pk>/editar/', views.pessoa_edicao_menu, name='pessoa_edicao_menu'),
    path('pessoas/<int:pk>/editar/nome/', views.pessoa_edit_nome, name='pessoa_edit_nome'),
    path('pessoas/<int:pk>/editar/sobrenome/', views.pessoa_edit_sobrenome, name='pessoa_edit_sobrenome'),
    path('pessoas/<int:pk>/editar/nascimento/', views.pessoa_edit_nascimento, name='pessoa_edit_nascimento'),
    path('pessoas/<int:pk>/editar/sexo/', views.pessoa_edit_sexo, name='pessoa_edit_sexo'),
    path('pessoas/<int:pk>/editar/cpf/', views.pessoa_edit_cpf, name='pessoa_edit_cpf'),

    # Excluir
    path('pessoas/<int:pk>/excluir/', views.pessoa_delete, name='pessoa_delete'),

    # Filtros
    path('filtros/homens/', views.filtro_homens, name='filtro_homens'),
    path('filtros/mulheres/', views.filtro_mulheres, name='filtro_mulheres'),
    path('filtros/mais-velha/', views.filtro_mais_velha, name='filtro_mais_velha'),
    path('filtros/mais-nova/', views.filtro_mais_nova, name='filtro_mais_nova'),
    path('filtros/menores/', views.filtro_menores, name='filtro_menores'),
    path('filtros/acima-media/', views.filtro_acima_media, name='filtro_acima_media'),
    path('filtros/aniversariantes/', views.filtro_aniversariantes_mes, name='filtro_aniversariantes_mes'),

    # Estatísticas
    path('estatisticas/total/', views.est_total_cadastros, name='est_total_cadastros'),
    path('estatisticas/sexo/', views.est_homens_mulheres, name='est_homens_mulheres'),
    path('estatisticas/media-idade/', views.est_media_idade, name='est_media_idade'),
    path('estatisticas/maiores-menores/', views.est_maiores_menores, name='est_maiores_menores'),
    path('estatisticas/faixa-etaria/', views.est_faixa_etaria, name='est_faixa_etaria'),
    path('estatisticas/maior-menor-idade/', views.est_maior_menor_idade, name='est_maior_menor_idade'),
    path('estatisticas/aniversariantes-mes/', views.est_aniversariantes_mes, name='est_aniversariantes_mes'),

    # Exportação
    path('exportacao/csv/', views.export_csv, name='export_csv'),
    path('exportacao/xlsx/', views.export_xlsx, name='export_xlsx'),
    path('exportacao/json/', views.export_json, name='export_json'),
]
