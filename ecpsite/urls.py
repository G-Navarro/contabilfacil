from django.contrib import admin
from django.urls import path
from envioemails.views import Envioemails
from empbase.views import Index, Funcionario, Empresas, Notas, Obras, Alocacao, Impostos, Ponto, Tarefas, Usuarios, cadastrar, buscadados, alocacao_edit

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index.as_view(), name=''),
    path('empresas', Empresas.as_view(), name='empresas'),
    path('tarefas', Tarefas.as_view(), name='tarefas'),
    path('impostos', Impostos.as_view(), name='impostos'),
    path('ponto', Ponto.as_view(), name='ponto'),
    path('funcionarios', Funcionario.as_view(), name='funcionarios'),
    path('obras/<int:id>', Obras.as_view(), name='obras'),
    path('notas', Notas.as_view(), name='notas'),
    path('alocacoes/<int:id>', Alocacao.as_view(), name='alocacoes'),
    path('usuarios', Usuarios.as_view(), name='usuarios'),
    path('alocacao_edit', alocacao_edit, name='alocacao_edit'),
    path('cadastrar', cadastrar, name='cadastrar'),
    path('buscadados', buscadados, name='buscadados'),
    path('envioemails', Envioemails.as_view(), name='envioemails'),
]
