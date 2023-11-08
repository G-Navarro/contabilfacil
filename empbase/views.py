import calendar, hashlib, re, copy, pytz
from typing import Any
from django import http
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import date, time, timedelta, datetime
from empbase.forms import FuncionarioForm, ImpostoForm
from django.forms.models import model_to_dict
from empbase.imports import cad_imposto, criar_empresa, criar_funcionario, baixanotas, criar_obra, subs
from django.db.models import Q
from django.dispatch import receiver
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from usuarios.models import Usuario
from django.contrib.auth.models import Permission
from empbase.models import Funcionario, Empresa, Holerite, Imposto, Notas, Obras, Ferias, Pagamento, PeriodoAquisitivo, Rescisao, Alocacao, Base, Rubrica, TemAcesso, Tramites, UltimoAcesso

def hash_id(id):
    # Convert the ID to a string
    id_string = str(id)
    # Create a hashlib object using the SHA256 algorithm
    hash_object = hashlib.sha256(id_string.encode())
    # Get the hexadecimal representation of the hash
    hash_value = hash_object.hexdigest()
    # Return the hash value
    return hash_value

def get_original_id(hashed_id, objects):
    for obj in objects:
        # Get the ID of the object
        id = obj.id
        # Convert the ID to a string
        id_string = str(id)
        # Create a hashlib object using the SHA256 algorithm
        hash_object = hashlib.sha256(id_string.encode())
        # Get the hexadecimal representation of the hash
        hash_value = hash_object.hexdigest()
        # Compare the hashed ID with the stored hashed ID
        if hash_value == hashed_id:
            return id
    
    return None  # Return None if no match is found

def getUA(user):
    ua = UltimoAcesso.objects.filter(user=user).first()
    acesso = user.temacesso.emp.filter(escr=ua.escr)
    return ua, acesso


class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, **kwargs):
        context = {
            'hello':'Hello',
            }
        if request.user.is_authenticated and request.user.eh_funcionario:
            return HttpResponseRedirect('ponto')
        elif request.user.is_authenticated:
            return HttpResponseRedirect('empresas')
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        rpost = request.POST
        user = authenticate(username=rpost['usuario'], password=rpost['senha'])       
        if user is not None:
            login(request, user)
            if user.eh_funcionario:
                return HttpResponseRedirect('ponto') 
            return HttpResponseRedirect('funcionarios')
        else:
            context = {
            'msg':'Usuario e ou senha incorretos',
            }
            return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class Empresas(TemplateView):
    template_name = 'empresas.html'

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        context = {
            'ua': ua,
            'emps': acesso.filter(situacao='Ativa'),
            'titulo': ua.escr.nome,
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if 'comp' in rpost:
            ua.comp = f"{rpost['comp']}-01"
            ua.save()
            return JsonResponse({'msg':'sucesso'})
        if 'idemp' in rpost:
            emp = request.user.temacesso.emp.get(id=rpost['idemp'])
            h = date.today()
            h = f'{h.year}-{h.month}-{h.day}'
            ua, acesso = getUA(request.user)
            ua.emp = emp
            ua.save()
            return HttpResponseRedirect('funcionarios')


@method_decorator(login_required, name='dispatch')
class FuncionarioTodos(TemplateView):
    template_name = 'funcionarios_todos.html'
    model = Funcionario
    form_class = FuncionarioForm()

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        funcs = ua.emp.funcionario_set.all().order_by('-cod')
        if funcs:
            func = None if funcs == 0 else funcs.filter(cod=request.GET['funcid'])[0] if 'funcid' in request.GET else funcs[0]
            listfuncs = list(funcs)
            indexfunc = listfuncs.index(func)
            idant = indexfunc - 1
            idseg = indexfunc + 1 if indexfunc < len(listfuncs)-1 else 0
            rescisoes = Rescisao.objects.filter(func__emp=ua.emp)
            rescisoes_abertas = rescisoes.exclude(tramite__nome='Cancelado')
            rescisoes_canceladas = rescisoes.filter(tramite__nome='Cancelado')
            feriasaberta = PeriodoAquisitivo.objects.filter(func__emp=ua.emp, func__demitido=False, diasdedireito__gt=0).order_by('periodoinicio')
            context = {
                'ua': ua,       
                'titulo': 'Funcionários - ' + ua.emp.apelido,
                'funcs': funcs,
                'idfuncanterior': listfuncs[idant].id,
                'idfuncseguinte': listfuncs[idseg].id,                
                'rescisao': Rescisao(),
                'rescisoes_abertas': rescisoes_abertas,
                'rescisoes_canceladas': rescisoes_canceladas,
                'feriasaberta': feriasaberta            
            }
        else:
            context = {
                'ua': ua,       
                'titulo': 'Funcionários - ' + ua.emp.apelido,
                }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class Funcionario(TemplateView):
    template_name = 'funcionario.html'
    model = Funcionario
    form_class = FuncionarioForm()

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        funcs = ua.emp.funcionario_set.all().order_by('-cod')
        func = funcs.get(cod=kwargs['id'])
        context = {
            'ua': ua,
            'titulo': func,
            'funcs': funcs,
            'func': func,
            'periodo_aq': func.periodoaquisitivo_set.all().order_by('periodoinicio'),
            'faltas': func.lancamento_set.filter(rub__name__contains='Faltas').order_by('diatrabalhado__inicioem'),
            'rescisao': Rescisao(),
            'form': self.form_class
            }
        if func.rescisao_set.all():
            if func.rescisao_set.exclude(tramite__nome='Cancelado'):
                demissao = func.rescisao_set.exclude(tramite__nome='Cancelado').first()
                context['demissao'] = demissao
            if func.rescisao_set.filter(tramite__nome='Cancelado'):
                demissao_cancelada = func.rescisao_set.filter(tramite__nome='Cancelado')
                context['demissao_cancelada'] = demissao_cancelada
        if 'ferias' in request.GET:
            ferias = func.ferias_set.get(inicio=datetime.strptime(request.GET['ferias'], '%Y-%m-%d'))
            context['feriasedit'] = ferias
            context['tramite']  = ferias.tramite.get_queryset()
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        ponto = Ponto()
        if 'falta' in rpost:
            rubrica = Rubrica.objects.get_or_create(emp=ua.emp, name='Horas Faltas', cod=40)
            func = ua.emp.funcionario_set.get(cod=kwargs['id'])
            falta = datetime.strptime(rpost['falta'], '%Y-%m-%d').date()
            diadetrabalho = func.diadetrabalho_set.filter(inicioem=falta)
            #aqui cria mes caso nao exista
            if not diadetrabalho:
                ponto.cria_mes_dias(falta, func)
            if rpost['faltaate']:
                faltaate = datetime.strptime(rpost['faltaate'], '%Y-%m-%d').date()
                totalfaltas = range(((faltaate + timedelta(days=1)) - falta).days)
                #aqui cria mes caso seja maior que a competencia definida
                if faltaate.month > ua.comp.month and faltaate.year > ua.comp.year:
                    ponto.cria_mes_dias(faltaate, func)
                #loop para lancar varias faltas de uma vez
                for i in totalfaltas:
                    ponto.lanca_faltas(func, falta + timedelta(days=i))
                return HttpResponseRedirect(f'{func.cod}')
            else:
                ponto.lanca_faltas(func, falta)
                return HttpResponseRedirect(f'{func.cod}')
        if 'datademissao' in rpost:
            tiporescisao = Rescisao.Tipo[rpost['tiporescisao']]
            tipoaviso = rpost['tipoaviso']
            avisodemissao = datetime.strptime(rpost['avisodemissao'], '%Y-%m-%d').date() if 'avisodemissao' in rpost else None
            datademissao = datetime.strptime(rpost['datademissao'], '%Y-%m-%d').date()
            if 'tiporeducao' in rpost:
                if rpost['tiporeducao'] == '7dias':
                    reducao = datademissao - timedelta(days=7)
            else:
                reducao = None
            func = ua.emp.funcionario_set.get(cod=kwargs['id'])
            rescisao = func.rescisao_set.create(
                emp = func.emp,
                tiporescisao = tiporescisao,
                tipoaviso = tipoaviso,
                reducao = reducao,
                aviso = avisodemissao,
                final = datademissao
            )
            rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Solicitação', finalizado = True, usuario=request.user))
            rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Visualizado'))
            rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Recibo'))
            rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Atualização CTPS'))
            if tiporescisao == '2' or tiporescisao == '4':
                rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Guia GRRF'))
                rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Chave FGTS'))
            if tiporescisao == '2':
                rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Seguro Desemprego'))
            rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Esocial'))
            rescisao.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Finalizado'))
            func.demitido = True 
            func.demissao = datademissao
            func.save()
            return HttpResponseRedirect(f'{func.cod}')
        if 'cancelarrescisao' in rpost:
            func = ua.emp.funcionario_set.get(cod=rpost['cancelarrescisao'])
            rescisao = func.rescisao_set.exclude(tramite__nome='Cancelado').first()
            tramite_cancelado = Tramites.objects.create(emp=ua.emp, nome='Cancelado', finalizado = True, usuario=request.user)
            tramite_cancelado.save()
            rescisao.tramite.add(tramite_cancelado)
            func.demitido = False
            func.demissao = None
            func.save()
            return HttpResponseRedirect(f'{func.cod}')
        if 'periodo_aq_inicio' in rpost:
            func = ua.emp.funcionario_set.get(cod=kwargs['id'])
            periodo = datetime.strptime(rpost['periodo_aq_inicio'], '%Y-%m-%d').date()
            periodo_aq = func.periodoaquisitivo_set.get(periodoinicio=periodo)
            inicioferias = datetime.strptime(rpost['inicioferias'], '%Y-%m-%d').date()
            diasferias = int(rpost['diasdedireito'])
            ferias = periodo_aq.ferias_set.create(
                aviso = inicioferias - timedelta(days=30),
                inicio = inicioferias,
                final = inicioferias + timedelta(days=diasferias),
            )
            ferias.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Solicitação', finalizado=True, usuario=request.user))
            ferias.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Visualizado'))
            ferias.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Aviso'))
            ferias.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Recibo'))
            ferias.tramite.add(Tramites.objects.create(emp=ua.emp, nome='Finalizado'))
            periodo_aq.diasdedireito -= diasferias
            periodo_aq.save()
            periodonovo = periodo.replace(year=periodo.year + 1)
            if not func.periodoaquisitivo_set.filter(periodoinicio=periodonovo):
                periodoclass= PeriodoAquisitivo()
                periodofim = periodonovo.replace(year=periodonovo.year + 1) - timedelta(days=1)
                func.periodoaquisitivo_set.create(
                    emp = func.emp,
                    periodoinicio = periodonovo,
                    periodofim = periodofim,
                    datamaxima = periodoclass.datamaxima_calc(periodofim),
                )
            return HttpResponseRedirect(f'{func.cod}')


@method_decorator(login_required, name='dispatch')
class Pagamentos(TemplateView):
    template_name = 'pagamentos.html'
    model = Funcionario
    form_class = FuncionarioForm()

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)            
        holerites = ua.emp.holerite_set.filter(comp=ua.comp)
        funcs = ua.emp.funcionario_set.filter(demitido=False).filter(admissao__lte=ua.comp)
        if not holerites and funcs:
            #cria adiantamento
            ad = ua.emp.holerite_set.create(tipo=Holerite.Tipo.AD, comp=ua.comp)
            #cria folha mensal
            fm = ua.emp.holerite_set.create(tipo=Holerite.Tipo.FM, comp=ua.comp)
            for func in funcs:
                pgad = Pagamento.objects.create(func=func)
                ad.funcs.add(pgad)
                pgfm = Pagamento.objects.create(func=func)
                fm.funcs.add(pgfm)
            if ua.comp.month == 11:
                ad13 = ua.emp.holerite_set.create(tipo=Holerite.Tipo.AD13, comp=ua.comp)
                for func in funcs:
                    pg = Pagamento.objects.create(func=func)
                    ad13.funcs.add(pg)
            if ua.comp.month == 12:
                fm13 = ua.emp.holerite_set.create(tipo=Holerite.Tipo.FM13, comp=ua.comp)
                for func in funcs:
                    pg = Pagamento.objects.create(func=func)
                    fm13.funcs.add(pg)
        context = {
            'ua': ua,
            'titulo': 'Pagamentos - ' + ua.emp.apelido
        }
        adiantamento = ua.emp.holerite_set.filter(comp=ua.comp, tipo='ADIANTAMENTO').first()
        if adiantamento:
            context['adiantamento'] = adiantamento.funcs.exclude(pago=True).order_by('func__nome')
            context['adiantamento_pago'] = adiantamento.funcs.filter(pago=True).order_by('func__nome')
        folha_mensal = ua.emp.holerite_set.filter(comp=ua.comp, tipo='FOLHA MENSAL').first()
        if folha_mensal:
            context['folha_mensal'] = folha_mensal.funcs.exclude(pago=True).order_by('func__nome')
            context['folha_mensal_pago'] = folha_mensal.funcs.filter(pago=True).order_by('func__nome') 
        adiantamento13 = ua.emp.holerite_set.filter(comp=ua.comp, tipo='ADIANTAMENTO 13º').first()
        if adiantamento13:
            adiantamento13 = adiantamento13.funcs.get_queryset().order_by('func__nome')
            context['adiantamento13'] = adiantamento13.order_by('pago')
        pagamento13 = ua.emp.holerite_set.filter(comp=ua.comp, tipo='PAGAMENTO 13º').first()
        if pagamento13:
            pagamento13 = pagamento13.funcs.get_queryset().order_by('func__nome')
            context['pagamento13'] = pagamento13.order_by('pago')
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if 'pagamento' in rpost:
            pg = Pagamento.objects.get(id=rpost['pagamento'])
            if pg.pago:
                pg.pago = False
            else: 
                pg.pago = True
            pg.save()
            return JsonResponse({'status': pg.pago})

@method_decorator(login_required, name='dispatch')
class Notas(TemplateView):
    template_name = 'notas.html'
    
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        notas = ua.emp.notas_set.filter(comp__year=ua.comp.year)
        notas = notas.filter(comp__month=ua.comp.month)
        notas = notas.order_by('-numero')
        total = 0
        inss = 0
        iss = 0 

        active = ''
        if 'id' in request.GET:
            alterar = ua.emp.notas_set.get(id=request.GET['id'])
            active = 'active'
        else:
            alterar = ua.emp.notas_set.last()

        for nota in notas:
            total += nota.valor
            inss += nota.inss
            iss += nota.iss
        if len(notas) == 0:
            notas = None
        
        context = {
            'ua': ua,
            'titulo': 'Notas - '+ua.emp.apelido,
            'notas': notas,
            'total': total,
            'inss': inss,
            'iss': iss,
            'alterar': alterar,
            'active': active
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if rpost['comp']:
            ua.comp = f"{rpost['comp']}-01"
            ua.save()
            return HttpResponseRedirect('notas')


@method_decorator(login_required, name='dispatch')
class Obras(TemplateView):
    template_name = 'obras.html'
    
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        active = ''
        alterar = ''
        if kwargs['id'] != 0:
            alterar = ua.emp.obras_set.get(id=kwargs['id'])
            active = 'active'
        obras = ua.emp.obras_set.order_by('-cod')
            
        context = {
            'ua': ua,
            'titulo': 'Obras - '+ua.emp.apelido,
            'obras': obras,
            'alterar': alterar,
            'active': active
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        obra = ua.emp.obras_set.get(id=rpost['id'])
        if rpost['cod'] != 'None':
            obra.cod=rpost['cod']
        obra.nome=rpost['nome'] 
        obra.cnpj=rpost['cnpj']
        obra.cno=rpost['cno']
        obra.save()
        return HttpResponseRedirect(rpost['id'])


@method_decorator(login_required, name='dispatch')
class Alocacao(TemplateView):
    template_name = 'alocacoes.html'
    
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        alocs = ua.emp.alocacao_set.filter(comp__year=ua.comp.year)
        alocs = alocs.filter(comp__month=ua.comp.month).order_by('nota__numero')

        if kwargs['id'] != 0:
            alterar = ua.emp.alocacao_set.get(id=kwargs['id'])
        else:
            alterar = None
        if len(alocs) == 0:
            alocs = None
        context = {
            'titulo': 'Alocações - '+ua.emp.apelido,
            'alocacoes': alocs,
            'funcs': ua.emp.funcionario_set.filter(Q(demitido=False) | Q(demissao__gte=ua.comp)).distinct(),
            'ua': ua,
            'alterar': alterar
        }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if 'num' in rpost:
            num = subs(rpost['num'])
            if len(num) == 14:
                try:
                    obra = ua.emp.obras_set.get(cnpj__contains=num)
                except:
                    return HttpResponseRedirect('0', {'msg': 'Obra não existe'})
            if len(num) == 12:
                try:
                    obra = ua.emp.obras_set.get(cno__contains=num)
                except:
                    return HttpResponseRedirect('0', {'msg': 'Obra não existe'})
            if obra:
                try:
                    alocs = ua.emp.alocacao_set.filter(comp__year=ua.comp.year)
                    alocs = alocs.filter(comp__month=ua.comp.month)
                    alocs = alocs.get(obra=obra)
                    return HttpResponseRedirect('0', {'msg': 'Obra não existe'})
                except:
                    obracriada = ua.emp.alocacao_set.create(emp=ua.emp, obra=obra, comp=ua.comp)
                    return HttpResponseRedirect(f'{obracriada.id}')
            else:
                return HttpResponseRedirect('0')


@method_decorator(login_required, name='dispatch')
class Impostos(TemplateView):
    template_name = 'impostos.html'
    
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        context = {
            'ua': ua,
            'impostos': ua.emp.imposto_set.order_by('comp'),
            'titulo': 'Impostos - '+ua.emp.apelido,
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
            ua, acesso = getUA(request.user)
            rpost = request.POST
            if 'imposto' in rpost:
                imp = ua.emp.imposto_set.get(id=rpost['imposto'])
                if imp.pago:
                    imp.pago = False
                else: 
                    imp.pago = True
                imp.save()
                return JsonResponse({'status': imp.pago})


@method_decorator(login_required, name='dispatch')
class Tarefas(TemplateView):
    template_name = 'tarefas.html'

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rget = request.GET
        emps = acesso.filter(situacao='Ativa')
        form = ImpostoForm()
        for emp in emps:
            if not emp.imposto_set.filter(nome='DAS', comp=ua.comp):
                emp.imposto_set.create(nome='DAS', valor=0, comp=ua.comp)
            if not emp.holerite_set.filter(tipo=Holerite.Tipo.AD, comp=ua.comp):
                emp.holerite_set.create(tipo=Holerite.Tipo.AD, comp=ua.comp)
            #cria folha mensal
            if not emp.holerite_set.filter(tipo=Holerite.Tipo.FM, comp=ua.comp):
                emp.holerite_set.create(tipo=Holerite.Tipo.FM, comp=ua.comp)
        context = {
            'ua': ua,
            'emps': acesso,
            'imposto': emps.filter(imposto__comp=ua.comp).distinct(),
            'holerites': emps.filter(holerite__comp=ua.comp).distinct(),
            'rescisoes': Rescisao.objects.exclude(tramite__nome='Cancelado', tramite__finalizado=True).distinct(),
            'ferias': PeriodoAquisitivo.objects.filter(ferias__tramite__finalizado=False).distinct(),
            'form': form,
            'titulo': 'Tarefas',
            }
        if 'impid' in rget:
            imp = Imposto.objects.filter(id=rget['impid'], emp__escr=ua.escr).first()
            context['imp_edit'] = imp
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if 'deletar' in rpost:
            imp = Imposto.objects.get(id=rpost['deletar'], emp__escr=ua.escr)
            imp.delete()
            return JsonResponse({'msg': 'sucesso'})
        if 'editid' in rpost:
            imp = Imposto.objects.get(id=rpost['editid'], emp__escr=ua.escr)
            valor = float(rpost['editimpvalor'].replace(',', '.'))
            impvcto = datetime.strptime(rpost['editimpvcto'], '%Y-%m-%d').date() if rpost['editimpvcto'] else None
            imp.nome, imp.valor, imp.vcto = rpost['editimpnome'], valor, impvcto
            imp.save()
            return HttpResponseRedirect(f'tarefas?empref={imp.emp.cod}')
        if 'empresa' in rpost:
            impemp = acesso.get(id=rpost['empresa'])
            impvalor = rpost['valorimposto'].replace(',', '.') if rpost['valorimposto'] else 0.0
            impvcto = datetime.strptime(rpost['vctoimposto'], '%Y-%m-%d').date() if rpost['vctoimposto'] else None
            Imposto.objects.create(nome=rpost['nomeimposto'], valor=impvalor, comp=ua.comp, emp=impemp, vcto=impvcto)
            return HttpResponseRedirect(f'tarefas?empref={impemp.cod}')
        if 'imposto' in rpost:
            imp = Imposto.objects.get(id=rpost['imposto'])
            if imp.enviado:
                imp.enviado = False
            else: 
                imp.enviado = True
            imp.save()
            return JsonResponse({'status': imp.enviado})
        if 'holerite' in rpost:
            hol = Holerite.objects.get(id=rpost['holerite'])
            if hol.enviado:
                hol.enviado = False
            else: 
                hol.enviado = True
            hol.save()
            return JsonResponse({'status': hol.enviado})


@method_decorator(login_required, name='dispatch')
class RelatorioPonto(TemplateView):
    template_name = 'relatorio_ponto.html'
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        funcs = ua.emp.funcionario_set.filter(Q(demitido=False) | Q(demissao__gte=ua.comp)).distinct().order_by('nome')
        context = {
            'ua': ua,
            'funcs': funcs,
            'titulo': 'Relatório Ponto',
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class CartaoPonto(TemplateView):
    template_name = 'cartao_ponto.html'
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)            
        funcs = ua.emp.funcionario_set.filter(Q(demitido=False) | Q(demissao__gte=ua.comp)).distinct().order_by('nome')
        func = None if not funcs else funcs.filter(cod=request.GET['funcid'])[0] if 'funcid' in request.GET else funcs[0]
        if ua.comp >= func.admissao:
            if func:
                ponto = Ponto()
                ponto.cria_mes_dias(ua.comp, func)
        _, qtde_dias = calendar.monthrange(ua.comp.year, ua.comp.month)
        diadetrabalho = func.diadetrabalho_set.filter(inicioem__year=ua.comp.year, inicioem__month=ua.comp.month).order_by('inicioem')
        dias_encerrar = func.diadetrabalho_set.filter(entrou=False, encerrado=False, inicioem__lte=date.today() - timedelta(days=3))
        if dias_encerrar:
            for dia in dias_encerrar:
                dia.encerrado = True
                dia.save()
        lancamentos = func.lancamento_set.filter(comp__year=ua.comp.year, comp__month=ua.comp.month).order_by('comp')
        somavalores = {}
        for lancamento in lancamentos:
            nome = f'{lancamento.rub.cod} - {lancamento.rub.name}'
            valor = lancamento.valor
            if nome in somavalores:
                somavalores[nome] += valor
            else:
                somavalores[nome] = valor
        horastrabalhadas = 0
        for dia in diadetrabalho:
            horastrabalhadas += dia.horastrabalhadas
        listfuncs = list(funcs)
        indexfunc = listfuncs.index(func)
        idant = indexfunc - 1
        idseg = indexfunc + 1 if indexfunc < len(listfuncs)-1 else 0
        context = {
            'ua': ua,
            'funcs': funcs,
            'func': func,
            'somavalores': somavalores,
            'lancamentos': lancamentos,
            'idfuncanterior': listfuncs[idant].cod,
            'idfuncseguinte': listfuncs[idseg].cod,
            'qtedias': range(qtde_dias),
            'diadetrabalho': diadetrabalho,
            'horastrabalhadas': horastrabalhadas,
            'titulo': 'Cartão Ponto',
            }
        if 'diainicio' in request.GET and request.GET['diainicio']:
            diainicio = datetime.strptime(request.GET['diainicio'], '%Y-%m-%d')
            diadetrabalhoinfo = func.diadetrabalho_set.get(inicioem=diainicio)
            context['diadetrabalhoinfo'] = diadetrabalhoinfo
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if 'diadetrabalhoinfoinicioem' in rpost and 'funcid' in rpost:
            func = ua.emp.funcionario_set.get(cod=rpost['funcid'])
            diadetrabalho = func.diadetrabalho_set.get(inicioem=datetime.strptime(rpost['diadetrabalhoinfoinicioem'], '%d/%m/%Y'))
            diadetrabalho.encerrado = False
            diadetrabalho.retificar = True
            diadetrabalho.save()
            return HttpResponseRedirect(f'cartao_ponto?funcid={func.cod}')
        #lanca faltas
        if rpost['tipo'] == 'falta':
            func = ua.emp.funcionario_set.get(cod=rpost['funcid'])
            falta = datetime.strptime(rpost['falta'], '%d/%m/%Y').date()
            ponto = Ponto()
            ponto.lanca_faltas(func, falta)
            return JsonResponse({'status': 'ok'})
        

@method_decorator(login_required, name='dispatch')
class Ponto(TemplateView):
    template_name = 'ponto.html'

    def is_apos22(self, horario, inicioem, intervalo=False):
        apos22 = datetime.combine(inicioem, time(22,0,0))
        segundos = (horario - apos22).total_seconds()
        if segundos > 0:
            if intervalo:
                return -segundos
            return segundos
        else:
            return 0
           
    def calcula_lancametos(self, diadetrabalho, jornada, func):
        if diadetrabalho.inicioem.weekday() <= 4:
            cargahoraria = jornada.semana
            jornadaintervalo = jornada.intervalosemana
        else:
            cargahoraria = jornada.fsemana
            jornadaintervalo = jornada.intervalofsemana
        
        diafolga = jornada.diafolga
        diadetrabalho.lancamento_set.all().delete()
        #calcula se teve hora extra ou falta
        horasdodia = abs((diadetrabalho.entrada - diadetrabalho.saida).total_seconds())/3600 if diadetrabalho.entrada and diadetrabalho.saida else 0
        intervalo = abs((diadetrabalho.intervalo - diadetrabalho.fimintervalo).total_seconds())/3600 if diadetrabalho.intervalo else 0
        teveintervalo = True if intervalo > 0 else False

        #se nao teve intervalo subtrai o horario do intervalo para nao lancar duplicado
        totalcargahoraria = horasdodia - intervalo if teveintervalo else horasdodia
        diadetrabalho.horastrabalhadas = totalcargahoraria
        #se nao teve intervalo lanca uma intrajornada igual ao intervalo no contrato
        if horasdodia > cargahoraria and not teveintervalo and jornadaintervalo != 0:
            rub = Rubrica.objects.get_or_create(emp=func.emp, name='Intrajornada', cod=201)[0]
            lanc = func.lancamento_set.create(rub=rub, valor=jornadaintervalo, comp=diadetrabalho.inicioem, diatrabalhado=diadetrabalho)
        if totalcargahoraria - cargahoraria > 0.16:
            rub = Rubrica.objects.get_or_create(emp=func.emp, name='Hora Extra', cod=150)[0]
            lanc = func.lancamento_set.create(rub=rub, valor=totalcargahoraria - cargahoraria, comp=diadetrabalho.inicioem, diatrabalhado=diadetrabalho)
        if diadetrabalho.inicioem.weekday() != diafolga:
            if cargahoraria - totalcargahoraria > 0.16:
                rub = Rubrica.objects.get_or_create(emp=func.emp, name='Horas Faltas', cod=40)[0]
                lanc = func.lancamento_set.create(rub=rub, valor=cargahoraria - totalcargahoraria, comp=diadetrabalho.inicioem, diatrabalhado=diadetrabalho)
        if func.emp.paga_vr:
            if totalcargahoraria >= 6:
                rub = Rubrica.objects.get_or_create(emp=func.emp, name='Vale Refeição', cod=205)[0]
                lanc = func.lancamento_set.create(rub=rub, valor=1, comp=diadetrabalho.inicioem, diatrabalhado=diadetrabalho)
        if totalcargahoraria > 0:
            if func.vt:
                rub = Rubrica.objects.get_or_create(emp=func.emp, name='Vale Transporte', cod=48)[0]
                lanc = func.lancamento_set.create(rub=rub, valor=1, comp=diadetrabalho.inicioem, diatrabalhado=diadetrabalho)

            #agora calcula se trabalhou depois das 22h para lancar adicional noturno
            entrada = self.is_apos22(diadetrabalho.entrada, diadetrabalho.inicioem)
            intervalo = self.is_apos22(diadetrabalho.intervalo, diadetrabalho.inicioem, True) if diadetrabalho.intervalo else 0
            fimintervalo = self.is_apos22(diadetrabalho.fimintervalo, diadetrabalho.inicioem, True) if diadetrabalho.fimintervalo else 0
            saida = self.is_apos22(diadetrabalho.saida, diadetrabalho.inicioem)
            horasapos22 = (entrada + (intervalo + (fimintervalo + saida)))
            if teveintervalo:
                horasapos22 -= jornadaintervalo
            adicnoturno = horasapos22/3600
            if adicnoturno > 0:
                rub = Rubrica.objects.get_or_create(emp=func.emp, name='Adicional Noturno', cod=25)[0]
                lanc = func.lancamento_set.create(rub=rub, valor=adicnoturno, comp=diadetrabalho.inicioem, diatrabalhado=diadetrabalho)
            
    def cria_mes_dias(self, mes, func):
        if not func.diadetrabalho_set.filter(inicioem__year=mes.year, inicioem__month=mes.month).order_by('inicioem'):
            _, qtde_dias = calendar.monthrange(mes.year, mes.month)
            for dia in range(qtde_dias):
                diacomp = date(mes.year, mes.month, dia+1)
                #cria dia com hora minuto segundo 0:0:0
                datetimecomp = datetime.combine(diacomp, datetime.min.time()) 
                #datetimecomp = datetimecomp.astimezone(pytz.timezone('America/Sao_Paulo'))
                diadetrabalho = func.diadetrabalho_set.create(inicioem=diacomp, entrada=None, intervalo=None, fimintervalo=None, saida=None)
                #checa se já existe dia seguinte caso funcionario seja novo e comece dia 1, para evitar erros no código seguinte
                if diacomp.day == 1 and not func.diadetrabalho_set.filter(inicioem=diacomp-timedelta(days=1)):
                    diaantes = diacomp-timedelta(days=1)
                    diaantestime = datetime.combine(diaantes, datetime.min.time())
                    #diaantestime = diaantestime.astimezone(pytz.timezone('America/Sao_Paulo'))                    
                    diadetrabalho = func.diadetrabalho_set.create(inicioem=diaantes, entrada=None, intervalo=None, fimintervalo=None, saida=None, encerrado=True)
                if diadetrabalho.inicioem < date.today():
                    diadetrabalho.encerrado = True
                    diadetrabalho.save()

    def lanca_faltas(self, func, falta):
        dia5 = date(falta.year, falta.month + 1 if falta.month < 12 else 1, 5)
        hoje = date.today()
        if hoje > dia5:
            pass
        else:
            diadetrabalho = func.diadetrabalho_set.get(inicioem=falta)
            temfalta = diadetrabalho.lancamento_set.filter(rub__name='Horas Faltas')
            if not temfalta:
                diadetrabalho.entrada = None
                diadetrabalho.intervalo = None
                diadetrabalho.fimintervalo = None
                diadetrabalho.saida = None
                self.calcula_lancametos(diadetrabalho, func.jornada, func)
                diadetrabalho.encerrado = True
                diadetrabalho.save()

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        func = request.user.funcionario_set.get()
        hoje = date.today()
        #cria mes inteiro de dias de trabalho para o funcionario
        if ua.comp >= func.admissao:
            self.cria_mes_dias(ua.comp, func)
        diasabertos = func.diadetrabalho_set.filter(entrou=False, encerrado=False, inicioem__lte=date.today() - timedelta(days=3))
        if diasabertos:
            for dia in diasabertos:
                dia.encerrado = True
                dia.save()
        diaaberto = func.diadetrabalho_set.filter(encerrado=False, inicioem__lte=date.today()).order_by('inicioem').first()
        diadetrabalho = func.diadetrabalho_set.filter(inicioem__year=ua.comp.year, inicioem__month=ua.comp.month).order_by('inicioem')
        _, qtde_dias = calendar.monthrange(ua.comp.year, ua.comp.month)
        context = {
            'ua': ua,
            'func': func,
            'agora': datetime.now(),
            'qtedias': range(qtde_dias),
            'diaaberto': diaaberto,
            'diadetrabalho': diadetrabalho,
            'titulo': 'Ponto',
            }
        diaedit = func.diadetrabalho_set.filter(retificar=True, inicioem__month__gte=ua.comp.month, inicioem__year__gte=ua.comp.year)
        if diaedit:            
            context['diaedit'] = diaedit.first()
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        rpost = request.POST
        ua, acesso = getUA(request.user)
        func = ua.emp.funcionario_set.get(cod=request.user.funcionario_set.get().cod)
        #agora = agora.astimezone(timezone_emp)
        hoje = date.today()
        #aqui retifica horário ou marca atrasado
        if 'diafolga' in rpost:
            diafolga = datetime.strptime(rpost['diafolga'], '%Y-%m-%d').date()
            dia = func.diadetrabalho_set.filter(inicioem=diafolga).first()
            dia.encerrado = True
            dia.folga = True
            dia.save()
            return HttpResponseRedirect('ponto')
        if 'inicioem' in rpost:
            inicioem = rpost['inicioem']
            dateedit = datetime.strptime(inicioem, '%Y-%m-%d').date()
            diadetrabalho = func.diadetrabalho_set.get(inicioem=dateedit)
            if diadetrabalho:
                #faz object datetime 
                entradaedit = datetime.strptime(rpost['entrada'], '%Y-%m-%dT%H:%M')
                intervaloedit = datetime.strptime(rpost['intervalo'], '%Y-%m-%dT%H:%M') if rpost['intervalo'] else None
                fimintervaloedit = datetime.strptime(rpost['fimintervalo'], '%Y-%m-%dT%H:%M') if rpost['fimintervalo'] else None
                saidaedit = datetime.strptime(rpost['saida'], '%Y-%m-%dT%H:%M')
                teveintervalo = intervaloedit and fimintervaloedit
                if entradaedit.date() == dateedit:
                    diadetrabalho.entrada = entradaedit
                if fimintervaloedit == intervaloedit and intervaloedit:
                    diadetrabalho.intervalo = intervaloedit.replace(hour=0, minute=0, second=0)
                    diadetrabalho.fimintervalo = fimintervaloedit.replace(hour=0, minute=0, second=0)
                elif fimintervaloedit != intervaloedit:
                    if intervaloedit > entradaedit and intervaloedit.date() <= dateedit + timedelta(days=1): 
                        diadetrabalho.intervalo = intervaloedit
                    if fimintervaloedit.date() <= dateedit + timedelta(days=1):
                        diadetrabalho.fimintervalo = fimintervaloedit
                if teveintervalo:
                    if saidaedit >= fimintervaloedit and saidaedit.date() <= dateedit + timedelta(days=1):
                        go = True
                    if rpost['saida'] != '00:00' or rpost['saida'] != '':
                        go = True
                else:
                    if saidaedit > entradaedit and saidaedit.date() <= dateedit + timedelta(days=1):
                        go = True        
                if go:
                    diadetrabalho.saida = saidaedit
                    diadetrabalho.encerrado = True
                    diadetrabalho.retificar = False
                    diadetrabalho.lancamento_set.all().delete()
                    self.calcula_lancametos(diadetrabalho, func.jornada, func)
                diadetrabalho.save()
                return HttpResponseRedirect('ponto')
        msg = False
        #lanca faltas
        if rpost['tipo'] == 'falta':
            falta = datetime.strptime(rpost['falta'], '%d/%m/%Y').date()
            self.lanca_faltas(func, falta)
            return JsonResponse({'status': 'ok'})
        #exclui lancamentos
        if rpost['tipo'] == 'excluir_lanc':
            func.lancamento_set.filter(id=rpost['lancid']).delete()
            return JsonResponse({'status': 'ok'})
        diapostedit = rpost['horario'].replace('T', ' ')
        diapost = datetime.strptime(diapostedit, '%Y-%m-%d %H:%M')
        diainicio = datetime.strptime(rpost['datainicio'], '%Y-%m-%d')
        diadetrabalho = func.diadetrabalho_set.filter(inicioem=diainicio).first()
        diaanterior = func.diadetrabalho_set.filter(inicioem=diadetrabalho.inicioem-timedelta(days=1)).first()
        #marca ponto
        if rpost['tipo'] == 'entrada':
            #checa se hoje tem diadetrabalho aberto
            if not diadetrabalho.entrou and not diadetrabalho.encerrado and diadetrabalho.inicioem == diapost.date():
                diadetrabalho.entrada = diapost
                diadetrabalho.entrou = True
            elif diadetrabalho.encerrado:
                msg = 'Dia de trabalho encerrado'
            else: 
                msg = 'Você já marcou entrada'
        if rpost['tipo'] == 'intervalo':
            #checagem seguranca caso o intervalo seja no dia seguinte ao dia de inicio caso trabalhe de madrugada
            if diadetrabalho.entrou and not diadetrabalho.encerrado and diadetrabalho.inicioem <= diapost.date():
                if diadetrabalho.entrada > diapost:
                    msg = 'Entrada maior que o intervalo'
                else:   
                    diadetrabalho.intervalo = diapost
                #se for na madrugada pega o dia anterior
            elif diaanterior.entrou and not diaanterior.encerrado:
                #checa se o dia anterior tem diadetrabalho aberto e se já não foi marcado
                diaanterior.intervalo = diapost
            else: 
                if diadetrabalho.encerrado:
                    msg = 'Dia de trabalho encerrado'
                else:
                    msg = 'Você deve marcar entrada'
        if rpost['tipo'] == 'fimintervalo':
            #checagem seguranca caso o intervalo seja no dia seguinte ao dia de inicio caso trabalhe de madrugada
            if diadetrabalho.entrou and not diadetrabalho.encerrado and diadetrabalho.inicioem <= diapost.date():
                if diadetrabalho.intervalo:
                    if diadetrabalho.intervalo > diapost:
                        msg = 'Intervalo maior que o fim intervalo'
                    else:
                        diadetrabalho.fimintervalo = diapost
                else:
                    msg = 'Você deve marcar o intervalo'
                #se for na madrugada pega o dia anterior
            elif diaanterior.entrou and not diaanterior.encerrado:
                #checa se o dia anterior tem diadetrabalho aberto e se já não foi marcado
                diaanterior.fimintervalo = diapost
            else: 
                if not diadetrabalho.entrou:
                    msg = 'Você deve marcar entrada'
                elif diadetrabalho.encerrado:
                    msg = 'Dia de trabalho encerrado'
                else:
                    msg = 'Você deve marcar o início do intervalo'
        if rpost['tipo'] == 'saida':
            #intervalo = diadetrabalho.intervalo.time() != time(0, 0, 0)
            #fimintervalo = diadetrabalho.fimintervalo.time() != time(0, 0, 0)
            #intervaloanterior = diaanterior.intervalo.time() != time(0, 0, 0)
            #fimintervaloanterior = diaanterior.fimintervalo.time() != time(0, 0, 0)
            #if intervalo == fimintervalo and intervaloanterior == fimintervaloanterior and diadetrabalho.inicioem <= diapost.date():
            if diadetrabalho.entrou and not diadetrabalho.encerrado:
                if diadetrabalho.fimintervalo != diadetrabalho.intervalo:
                    if not diadetrabalho.fimintervalo:
                        msg = 'Você deve marcar o fim do intervalo'  
                        go = False
                    elif diadetrabalho.fimintervalo > diapost:
                        msg = 'Fim do intervalo maior que a saida'       
                        go = False
                    else:
                        go = True
                else:
                    go = True
                if diadetrabalho.entrada <= diapost and go:
                    diadetrabalho.saida = diapost
                    diadetrabalho.encerrado = True
                    self.calcula_lancametos(diadetrabalho, func.jornada, func)
                
                #diferenca_entrada = diadetrabalho.entrada - jornada.entrada
            elif diaanterior.entrou and not diaanterior.encerrado and diaanterior.saida.time() == time(0, 0, 0):
                    diaanterior.saida = diapost
                    diaanterior.encerrado = True
                    self.calcula_lancametos(diaanterior, func.jornada, func)
            elif diadetrabalho.encerrado:
                msg = 'Dia de trabalho encerrado'
            elif not diadetrabalho.entrou or not diaanterior.entrou: 
                msg = 'Você deve marcar entrada'
            #elif intervalo and not fimintervalo or intervaloanterior and not fimintervaloanterior:
                #msg = 'Você deve marcar o fim do intervalo'
            
        if not msg:
            if ua.comp.month != diadetrabalho.inicioem.month or ua.comp.year != diadetrabalho.inicioem.year:
                ua = UltimoAcesso.objects.filter(user=request.user).first()
                ua.comp = f'{diadetrabalho.inicioem.year}-{diadetrabalho.inicioem.month}-01'
                ua.save()
            diadetrabalho.save() 
            diaanterior.save()
            return JsonResponse({'dia': diapost.strftime('%d'), 'hora': f'{diapost.strftime("%H:%M")}', 'model': model_to_dict(diadetrabalho)})
        else:            
            return JsonResponse({'msg': msg})
        

@method_decorator(login_required, name='dispatch')
class Usuarios(TemplateView):
    template_name = 'usuarios.html'
    
    def get(self, request, **kwargs):
        user = request.user
        ua, acesso = getUA(request.user)
        rget = request.GET
        if user.eh_auxiliar:
            return HttpResponseRedirect('funcionarios')
        if 'nome_user' in rget:
            try:
                Usuario.objects.get(usuario=rget['nome_user'])
                return JsonResponse({'msg': 'existe'})
            except:
                return JsonResponse({'msg': 'n_existe'})
        useraltera = '' 
        allusers = Usuario.objects.filter(temacesso__emp__cod=ua.emp.cod)      
        if 'userid' in rget:
            useraltera = ua.escr.temacesso_set.get(user__id=get_original_id(rget['userid'], allusers)).user
            if user.eh_supervisor and useraltera.is_superuser:
                useraltera = ''
        context = {
            'ua': ua,
            'acesso': acesso,
            'is_superuser': allusers.filter(is_superuser=True),
            'eh_supervisor': allusers.filter(eh_supervisor=True),
            'eh_gerente': allusers.filter(eh_gerente=True),
            'eh_auxiliar': allusers.filter(eh_auxiliar=True),
            'eh_funcionario': ua.emp.funcionario_set.exclude(funcacesso__isnull=True).order_by('nome'),
            'titulo': 'Usuários',
            'useraltera': useraltera
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
        if 'bloqueiauser' in rpost:
            #bloqueia usuario
            users = Usuario.objects.filter(temacesso__emp__cod=ua.emp.cod)
            id = get_original_id(rpost['bloqueiauser'], users)
            user = Usuario.objects.get(id=id)
            user.is_active = False if user.is_active else True
            user.save()
            return JsonResponse({'status': user.is_active})
        if 'val_add' in rpost:
            #adciona acessos
            users = Usuario.objects.filter(temacesso__emp__cod=ua.emp.cod)
            id = get_original_id(rpost['userid'], users)
            user = Usuario.objects.get(id=id)
            emp = ua.escr.empresa_set.get(id=rpost['val_add'])
            user.temacesso.emp.add(emp)
            useracesso = user.temacesso.emp.get_queryset()
            emps = ''
            for acesso in useracesso:
                emps += f'<p style="margin: 0.5rem 0 0 0;">{acesso.cod} - {acesso.nome}</p>'
            return JsonResponse({'msg':'sucesso', 'emp': f'<div>{emps}</div>'})
        if 'userid' in rpost and rpost['userid'] != '':
            #atualiza usuario
            users = Usuario.objects.filter(temacesso__emp__cod=ua.emp.cod)
            id = get_original_id(rpost['userid'], users)
            user = Usuario.objects.get(id=id)
            user.nome = rpost['nomealtera']
            user.snome = rpost['snomealtera']
            user.email = rpost['emailaltera'].lower()
            user.fone = re.sub('[^0-9]', '', rpost['fonealtera'])
            user.is_superuser = True if 'is_superuseraltera' in rpost and rpost['is_superuseraltera'] == 'on' else False
            user.eh_supervisor = True if 'eh_supervisoraltera' in rpost and rpost['eh_supervisoraltera'] == 'on' else False
            user.eh_auxiliar = True if 'eh_auxiliaraltera' in rpost and rpost['eh_auxiliaraltera'] == 'on' else False
            user.eh_gerente = True if 'eh_gerentealtera' in rpost and rpost['eh_gerentealtera'] == 'on' else False
            if rpost['senhaaltera'] != '':
                user.set_password(rpost['senhaaltera'])
            user.save()
            return HttpResponseRedirect(f'usuarios?userid={hash_id(user.id)}')
        if 'usuario' in rpost:
            #cria novo usuario
            fone = re.sub('[^0-9]', '', rpost['fone'])
            if 'is_superuser' in rpost and rpost['is_superuser'] == 'on':
                user = Usuario.objects.create_superuser(email=rpost['email'].lower(), fone=fone, usuario=rpost['usuario'], nome=rpost['nome'], snome=rpost['snome'], password=rpost['senha'])
            if 'eh_supervisor' in rpost and rpost['eh_supervisor'] == 'on':
                user = Usuario.objects.create_supervisor(email=rpost['email'].lower(), fone=fone, usuario=rpost['usuario'], nome=rpost['nome'], snome=rpost['snome'], password=rpost['senha'])
            if 'eh_auxiliar' in rpost and rpost['eh_auxiliar'] == 'on':
                user = Usuario.objects.create_auxiliar(email=rpost['email'].lower(), fone=fone, usuario=rpost['usuario'], nome=rpost['nome'], snome=rpost['snome'], password=rpost['senha'])
            if 'eh_gerente' in rpost and rpost['eh_gerente'] == 'on':
                user = Usuario.objects.create_gerente(email=rpost['email'].lower(), fone=fone, usuario=rpost['usuario'], nome=rpost['nome'], snome=rpost['snome'], password=rpost['senha'])
            #cria_acesso
            TemAcesso.objects.create(user=user)
            user.temacesso.escr.add(ua.escr)
            user.temacesso.emp.add(ua.emp)
            UltimoAcesso.objects.create(escr=ua.escr,emp=ua.emp,user=user,comp=ua.comp)
            return HttpResponseRedirect(f'usuarios?userid={hash_id(user.id)}')


@method_decorator(login_required, name='dispatch')
class AlteraSenha(TemplateView):
    template_name = 'alterasenha.html'

    def get(self, request,**kwargs):
        ua, acesso = getUA(request.user)
        context = {
            'ua': ua,
            'acesso': acesso,
            'titulo': 'Alterar senha'
            }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):        
        if request.user.eh_funcionario:
            rpost = request.POST
            novasenha = rpost['novasenha']
            novasenhaconfere = rpost['novasenhaconfere']
            if novasenha == novasenhaconfere:
                request.user.set_password(novasenha)
                request.user.save()
            return HttpResponseRedirect(f'ponto')


def logout_view(request):
    logout(request)
    return redirect('')


def cadastrar(request):
    rpost = request.POST
    ua, acesso = getUA(request.user)
    def atu_ultimoacesso(emp, comp=None):
        ua.emp = emp
        if comp:
            ua.comp = comp
        ua.save()
    if rpost['modelo'] == 'empresas':
        emp = criar_empresa(request.FILES['arquivo'], request.user)
        return JsonResponse({'msg': 'sucesso'})
    if rpost['modelo'] == 'funcionarios':
        emp = criar_funcionario(request.FILES['arquivo'], request.user)
        atu_ultimoacesso(emp)
        return JsonResponse({'msg': 'sucesso'})
    if rpost['modelo'] == 'notas':
        emp, comp = baixanotas(request.FILES['arquivo'], request.user)
        atu_ultimoacesso(emp, comp)
        return JsonResponse({'msg': 'sucesso'})
    if rpost['modelo'] == 'obras':
        emp = criar_obra(request.FILES['arquivo'], request.user)
        atu_ultimoacesso(emp)
        return JsonResponse({'msg': 'sucesso'})
    if rpost['modelo'] == 'impostos':
        cad_imposto(request.FILES['arquivo'], request.user)
        return JsonResponse({'msg': 'sucesso'})
    

def buscadados(request):
    ua, acesso = getUA(request.user)
    emp = ua.emp
    tipo = request.GET['tipo']
    val = request.GET['val']

    if tipo == "obracod":
        context = []
        obra= emp.obras_set.filter()
        cnpj = emp.obras_set.filter(cnpj__contains=subs(val))
        cno = emp.obras_set.filter(cno__contains=subs(val))
        if len(cnpj) != 0:
            for cnpj in cnpj:
                context.append({'id': cnpj.id, 'nome': cnpj.nome, 'num': cnpj.cnpj, 'cod': cnpj.cod})
        elif len(cno) != 0:
            for cno in cno:
                context.append({'id': cno.id, 'nome': cno.nome, 'num': cno.cno, 'cod': cno.cod})
        else:
            context = {'msg': 'Nenhuma obra cadastrada'}
        return JsonResponse(context, safe=False)

    if tipo == "funcnome":
        context = []
        func = emp.funcionario_set.filter(Q(demissao__gte=ua.comp) | Q(demitido=False))
        func = func.filter(nome__contains=val.upper()).order_by('nome')
        if len(func) == 0:
            context = {'msg': 'Nenhum funcionário trabalhando com esse nome'}
        else:
            for f in func:
                context.append({'id': f.id, 'nome': f.nome})
        return JsonResponse(context, safe=False)


def alocacao_edit(request):
    ua, acesso = getUA(request.user)
    rget = request.GET
    if rget['tipo'] == 'cadastrar':
        obra = ua.emp.alocacao_set.get(obra__id=rget['obraid'], comp__year=ua.comp.year, comp__month=ua.comp.month)
        f = ua.emp.funcionario_set.get(id=rget['funcid'])
        if obra.func.contains(f):
            return JsonResponse({'msg':'Funcionário já está na alocação'})
        obra.func.add(rget['funcid'])
        context = {'id': f.id, 'cod': f.cod, 'nome': f.nome}
        return JsonResponse(context, safe=False)
    if rget['tipo'] == 'excluir':
        obra = ua.emp.alocacao_set.get(obra__id=rget['obraid'], comp__year=ua.comp.year, comp__month=ua.comp.month)
        obra.func.remove(rget['funcid'])
        return JsonResponse({'res':'sucesso'})
    if rget['tipo'] == 'alteranota':
        nota = ua.emp.notas_set.get(id=rget['idnota'])
        obra = ua.emp.obras_set.get(id=rget['idobra'])
        nota.tomador = obra
        nota.save()
        try: 
            alocacao = nota.alocacao
            alocacao.obra = obra
            alocacao.save()
        except:
            pass
        return JsonResponse({'res':'sucesso'})
    
def tramite_altera(request):
    ua, acesso = getUA(request.user)
    rpost = request.POST
    tramiteid = rpost['tramite']
    emp = acesso.filter(cod=rpost['emp']).first()
    tramite = emp.tramites_set.filter(id=tramiteid).first()
    if tramite:
        if tramite.finalizado:
            tramite.finalizado = False
            tramite.datafinalizado = None
        else:
            tramite.finalizado = True
            tramite.datafinalizado = date.today()
        tramite.usuario = request.user
        tramite.save()
        return JsonResponse({'status': tramite.finalizado})
    return JsonResponse({'res': 'ERRO'})

'''from usuarios.models import UsuarioManager
u = UsuarioManager()
u.create_superuser('guilherme@paulista.cnt.br', '19989434443', 'Guilherme', 'Guilherme', 'Navarro', 'uiui')
'''
