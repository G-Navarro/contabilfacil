from django.contrib import admin
from empbase.models import Alocacao, Base, Empresa, Funcionario, Holerite, Notas, Obras, Escritorio, Pagamento, TemAcesso, Imposto, Turno, UltimoAcesso

admin.site.register(Escritorio)
admin.site.register(Empresa)
admin.site.register(Funcionario)
admin.site.register(Notas)
admin.site.register(UltimoAcesso)
admin.site.register(TemAcesso)
admin.site.register(Imposto)
admin.site.register(Obras)
admin.site.register(Turno)
admin.site.register(Holerite)
admin.site.register(Pagamento)
admin.site.register(Base)