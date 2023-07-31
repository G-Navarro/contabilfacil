from django.contrib import admin
from empbase.models import Alocacao, Empresa, Funcionario, Notas, Obras, Escritorio, TemAcesso, Imposto, UltimoAcesso

admin.site.register(Escritorio)
admin.site.register(Empresa)
admin.site.register(Funcionario)
admin.site.register(Notas)
admin.site.register(UltimoAcesso)
admin.site.register(TemAcesso)
admin.site.register(Imposto)
admin.site.register(Obras)
admin.site.register(Alocacao)