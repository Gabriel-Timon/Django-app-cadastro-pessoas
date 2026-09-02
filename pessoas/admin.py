from django.contrib import admin
from .models import Pessoa

@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sobrenome', 'cpf_protegido', 'sexo', 'data_nascimento', 'idade')
    search_fields = ('nome', 'sobrenome', '=cpf')
    list_filter = ('sexo',)

    @admin.display(description='CPF')
    def cpf_protegido(self, pessoa):
        return pessoa.cpf_mascarado
