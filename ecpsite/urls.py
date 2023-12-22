from django.contrib import admin
from django.urls import path
from envioemails.views import Envioemails
from empbase.views import AlteraSenha, CartaoPonto, FuncionarioTodos, Index, Funcionario, Empresas, Notas, Obras, Alocacao, Impostos, Pagamentos, Ponto, RelatorioPonto, Tarefas, Usuarios, cadastrar, buscadados, alocacao_edit, logout_view, tramite_altera

urlpatterns = [
    path('ecp/', admin.site.urls),
    path('', Index.as_view(), name=''),
    path('empresas', Empresas.as_view(), name='empresas'),
    path('tarefas/<int:empid>/<str:comp>', Tarefas.as_view(), name='tarefas'),
    path('impostos/<int:empid>/<str:comp>', Impostos.as_view(), name='impostos'), 
    path('ponto', Ponto.as_view(), name='ponto'),
    path('relatorioponto/<int:empid>/<str:comp>', RelatorioPonto.as_view(), name='relatorioponto'),
    path('cartao_ponto/<int:empid>/<str:comp>', CartaoPonto.as_view(), name='cartao_ponto'),
    path('pagamentos/<int:empid>/<str:comp>', Pagamentos.as_view(), name='pagamentos'),
    path('funcionarios/<int:empid>', FuncionarioTodos.as_view(), name='funcionarios'),
    path('funcionarios/<int:empid>/<int:funcid>', Funcionario.as_view(), name='funcionarios'),
    path('obras/<int:empid>', Obras.as_view(), name='obras'),
    path('notas/<int:empid>/<str:comp>', Notas.as_view(), name='notas'),
    path('alocacoes/<int:empid>/<str:comp>', Alocacao.as_view(), name='alocacoes'),
    path('usuarios', Usuarios.as_view(), name='usuarios'),
    path('alterasenha', AlteraSenha.as_view(), name='alterasenha'),
    path('envioemails', Envioemails.as_view(), name='envioemails'),
    path('alocacao_edit/<int:empid>', alocacao_edit, name='alocacao_edit'),
    path('cadastrar', cadastrar, name='cadastrar'),
    path('buscadados/<int:empid>', buscadados, name='buscadados'),
    path('tramite_altera/<int:empid>/<str:comp>', tramite_altera, name='tramite_altera'),
    path('logout', logout_view, name='logout')
]
