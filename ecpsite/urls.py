from django.contrib import admin
from django.urls import path
from envioemails.views import Envioemails
from empbase.views import AlteraSenha, CartaoPonto, FuncionarioTodos, Index, Funcionario, Empresas, Notas, Obras, Alocacao, Impostos, Pagamentos, Ponto, RelatorioPonto, Tarefas, Usuarios, cadastrar, buscadados, alocacao_edit, logout_view, tramite_altera

urlpatterns = [
    path('ecp/', admin.site.urls),
    path('', Index.as_view(), name=''),
    path('empresas', Empresas.as_view(), name='empresas'),
    path('tarefas', Tarefas.as_view(), name='tarefas'),
    path('impostos', Impostos.as_view(), name='impostos'), 
    path('ponto', Ponto.as_view(), name='ponto'),
    path('relatorioponto', RelatorioPonto.as_view(), name='relatorioponto'),
    path('cartao_ponto', CartaoPonto.as_view(), name='cartao_ponto'),
    path('pagamentos', Pagamentos.as_view(), name='pagamentos'),
    path('funcionarios', FuncionarioTodos.as_view(), name='funcionarios'),
    path('funcionarios/<int:id>', Funcionario.as_view(), name='funcionarios'),
    path('obras/<int:id>', Obras.as_view(), name='obras'),
    path('notas', Notas.as_view(), name='notas'),
    path('alocacoes/<int:id>', Alocacao.as_view(), name='alocacoes'),
    path('usuarios', Usuarios.as_view(), name='usuarios'),
    path('alterasenha', AlteraSenha.as_view(), name='alterasenha'),
    path('envioemails', Envioemails.as_view(), name='envioemails'),
    path('alocacao_edit', alocacao_edit, name='alocacao_edit'),
    path('cadastrar', cadastrar, name='cadastrar'),
    path('buscadados', buscadados, name='buscadados'),
    path('tramite_altera', tramite_altera, name='tramite_altera'),
    path('logout', logout_view, name='logout')
]
