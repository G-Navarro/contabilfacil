import calendar, hashlib, re, copy, pytz
from dateutil import parser
from datetime import date, time, timedelta, datetime
from empbase.forms import FuncionarioForm
from django.forms.models import model_to_dict
from empbase.imports import cad_imposto, criar_empresa, criar_funcionario, baixanotas, criar_obra, subs
from django.db.models.signals import pre_save
from django.db.models import Q
from django.dispatch import receiver
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from usuarios.models import Usuario, UsuarioManager
from empbase.models import Funcionario, Empresa, Holerite, Imposto, Notas, Obras, Ferias, Pagamento, Rescisao, Alocacao, Base, TemAcesso, UltimoAcesso

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
    ua = UltimoAcesso.objects.get(user=user)
    acesso = user.temacesso.emp.filter(escr=ua.escr)
    return ua, acesso


class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, **kwargs):
        context = {
            'hello':'Hello',
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        rpost = request.POST
        user = authenticate(username=rpost['usuario'], password=rpost['senha'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('funcionarios')
        else:
            context = {
            'msg':'Usuario e ou senha incorretos',
            }
            return render(request, self.template_name, context)


class Empresas(TemplateView):
    template_name = 'empresas.html'

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        context = {
            'ua': ua,
            'emps': acesso,
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

    

class Funcionario(TemplateView):
    template_name = 'funcionarios.html'
    model = Funcionario
    form_class = FuncionarioForm()

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        try:
            funcs = ua.emp.funcionario_set.order_by('-cod')    
        except:
            funcs = None
            
        context = {
            'ua': ua,
            'titulo': 'Funcionários - '+ua.emp.apelido,
            'funcs': funcs,
            'form': self.form_class
            }
        print(self.form_class.base_fields['nome'])
        return render(request, self.template_name, context)


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
            'funcs': ua.emp.funcionario_set.filter(Q(alocacao__comp__month=ua.comp.month) & Q(alocacao__comp__year=ua.comp.year), demitido=False).distinct(),
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


class Tarefas(TemplateView):
    template_name = 'tarefas.html'

    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        emps = acesso.filter(situacao='Ativa')
        for emp in emps:
            if not emp.imposto_set.filter(nome='DAS', comp=ua.comp):
                emp.imposto_set.create(nome='DAS', valor=0, comp=ua.comp)
            holerites = emp.holerite_set.filter(comp=ua.comp)
            funcs = emp.funcionario_set.filter(demitido=False).filter(admissao__lte=ua.comp)
            if not holerites and funcs:
                #cria adiantamento
                ad = emp.holerite_set.create(tipo=Holerite.Tipo.AD, comp=ua.comp)
                #cria vale
                fm = emp.holerite_set.create(tipo=Holerite.Tipo.FM, comp=ua.comp)
                for func in funcs:
                    pgad = Pagamento.objects.create(func=func)
                    ad.funcs.add(pgad)
                    pgfm = Pagamento.objects.create(func=func)
                    fm.funcs.add(pgfm)
                if ua.comp == 11:
                    ad13 = emp.holerite_set.create(tipo=Holerite.Tipo.AD13, comp=ua.comp)
                    for func in funcs:
                        pg = Pagamento.objects.create(func=func)
                        ad13.funcs.add(pg)
                if ua.comp == 12:
                    fm13 = emp.holerite_set.create(tipo=Holerite.Tipo.FM13, comp=ua.comp)
                    for func in funcs:
                        pg = Pagamento.objects.create(func=func)
                        fm13.funcs.add(pg)
            if emp == ua.emp:
                fpagamento = emp.holerite_set.filter(comp=ua.comp)
        #emps.filter(holerite__comp=ua.comp, holerite__emp=ua.emp).distinct()
        #ua.emp.funcionario_set.filter()
        context = {
            'ua': ua,
            'emps': acesso,
            'imposto': emps.filter(imposto__comp=ua.comp).distinct(),
            'holerite': emps.filter(holerite__comp=ua.comp).distinct(),
            'fpagamento': fpagamento,
            'titulo': 'Tarefas',
            }
        return render(request, self.template_name, context)
    
    def post(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        rpost = request.POST
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
        if 'pagamento' in rpost:
            pg = Pagamento.objects.get(id=rpost['pagamento'])
            if pg.pago:
                pg.pago = False
            else: 
                pg.pago = True
            pg.save()
            return JsonResponse({'status': pg.pago})


class Ponto(TemplateView):
    template_name = 'ponto.html'

    def cria_data(self, data, hora):
        dia = f"{data.strftime('%Y-%m-%d')} {hora}:00"
        jornada_datetime = datetime.strptime(dia, '%Y-%m-%d %H:%M:%S')
        print(jornada_datetime)
        jornada_datetime = jornada_datetime.astimezone(pytz.timezone('America/Sao_Paulo'))
        #print(data.tzinfo)
        print(jornada_datetime.tzinfo)
        return jornada_datetime

    def calcula_lancametos(self, diadetrabalho, jornada):
        print(diadetrabalho.entrada)
        jentrada = self.cria_data(diadetrabalho.entrada.date(), jornada.entrada if diadetrabalho.inicioem.weekday() <= 4 else jornada.entradafs) 
        jintervalo = self.cria_data(diadetrabalho.intervalo.date(), jornada.intervalo if diadetrabalho.inicioem.weekday() <= 4 else jornada.intervalofs)
        jfimintervalo = self.cria_data(diadetrabalho.fimintervalo.date(), jornada.fimintervalo if diadetrabalho.inicioem.weekday() <= 4 else jornada.fimintervalofs)
        jsaida = self.cria_data(diadetrabalho.saida.date(), jornada.saida if diadetrabalho.inicioem.weekday() <= 4 else jornada.saidafs)
        
        entrada = abs((jentrada - diadetrabalho.entrada).total_seconds())/3600
        intervalo = abs((jintervalo - diadetrabalho.intervalo).total_seconds())/3600
        fimintervalo = abs((jfimintervalo - diadetrabalho.fimintervalo).total_seconds())/3600
        saida = abs((jsaida - diadetrabalho.saida).total_seconds())/3600
        total = entrada + intervalo + fimintervalo + saida
        print(total)        
    
    def get(self, request, **kwargs):
        ua, acesso = getUA(request.user)
        funcs = ua.emp.funcionario_set.filter(demitido=False).order_by('nome')
        func = funcs.filter(id=request.GET['funcid'])[0] if 'funcid' in request.GET else funcs[0]
        _, qtde_dias = calendar.monthrange(ua.comp.year, ua.comp.month)
        #cria mes inteiro de dias de trabalho para o funcionario
        if not func.diadetrabalho_set.filter(inicioem__year=ua.comp.year, inicioem__month=ua.comp.month).order_by('inicioem'):
            for dia in range(qtde_dias):
                diacomp = date(ua.comp.year, ua.comp.month, dia+1)
                datetimecomp = datetime.combine(diacomp, datetime.min.time()) 
                datetimecomp = datetimecomp.astimezone(pytz.timezone('America/Sao_Paulo'))
                diadetrabalho = func.diadetrabalho_set.create(inicioem=diacomp, entrada=datetimecomp, intervalo=datetimecomp, fimintervalo=datetimecomp, saida=datetimecomp)
                #checa se já existe dia seguinte caso funcionario seja novo e comece dia 1, para evitar erros no código seguinte
                if diacomp.day == 1 and not func.diadetrabalho_set.filter(inicioem=diacomp-timedelta(days=1)):
                    diaantes = diacomp-timedelta(days=1)
                    diaantestime = datetime.combine(diaantes, datetime.min.time())
                    diaantestime = diaantestime.astimezone(pytz.timezone('America/Sao_Paulo'))                    
                    diadetrabalho = func.diadetrabalho_set.create(inicioem=diaantes, entrada=diaantestime, intervalo=diaantestime, fimintervalo=diaantestime, saida=diaantestime, encerrado=True)
                if diadetrabalho.inicioem < date.today():
                    diadetrabalho.encerrado = True
                    diadetrabalho.save()
        diaaberto = func.diadetrabalho_set.filter(entrou=True, encerrado=False).order_by('inicioem').last()
        diadetrabalho = func.diadetrabalho_set.filter(inicioem__year=ua.comp.year, inicioem__month=ua.comp.month).order_by('inicioem')
        listfuncs = list(funcs)
        indexfunc = listfuncs.index(func)
        idant = indexfunc - 1
        idseg = indexfunc + 1 if indexfunc < len(listfuncs)-1 else 0
        context = {
            'ua': ua,
            'funcs': funcs,
            'func': func,
            'idfuncanterior': listfuncs[idant].id,
            'idfuncseguinte': listfuncs[idseg].id,
            'agora': datetime.now(),
            'qtedias': range(qtde_dias),
            'diaaberto': diaaberto,
            'diadetrabalho': diadetrabalho,
            'titulo': 'Ponto',
            }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        rpost = request.POST
        ua, acesso = getUA(request.user)
        func = ua.emp.funcionario_set.get(id=rpost['funcid'])
        agora = datetime.now()
        agora = agora.astimezone(pytz.timezone('America/Sao_Paulo'))
        hoje = date.today()
        diadetrabalho = func.diadetrabalho_set.filter(inicioem=hoje).first()
        diaanterior = func.diadetrabalho_set.filter(inicioem=diadetrabalho.inicioem-timedelta(days=1)).first()
        nada_alterado = False
        if rpost['tipo'] == 'entrada':
            #checa se hoje tem diadetrabalho aberto
            if not diadetrabalho.entrou and not diadetrabalho.encerrado:
                diadetrabalho.entrada = agora
                diadetrabalho.entrou = True
                print('entrou')
            else: 
                nada_alterado = True
        if rpost['tipo'] == 'intervalo':
            #checagem seguranca caso o intervalo seja no dia seguinte ao dia de inicio caso trabalhe de madrugada
            if diadetrabalho.entrou and not diadetrabalho.encerrado and diaanterior.intervalo.time() == time(3, 0, 0):
                diadetrabalho.intervalo = agora
                #se for na madrugada pega o dia anterior
            elif diaanterior.entrou and diaanterior.intervalo.time() == time(3, 0, 0):
                #checa se o dia anterior tem diadetrabalho aberto e se já não foi marcado
                diaanterior.intervalo = agora
            else: 
                nada_alterado = True
        if rpost['tipo'] == 'fimintervalo':
            #checagem seguranca caso o intervalo seja no dia seguinte ao dia de inicio caso trabalhe de madrugada
            if diadetrabalho.entrou and not diadetrabalho.encerrado and diaanterior.fimintervalo.time() == time(3, 0, 0):
                diadetrabalho.fimintervalo = agora
                #se for na madrugada pega o dia anterior
            elif diaanterior.entrou and not diaanterior.encerrado and diaanterior.fimintervalo.time() == time(3, 0, 0):
                #checa se o dia anterior tem diadetrabalho aberto e se já não foi marcado
                diaanterior.fimintervalo = agora
            else: 
                nada_alterado = True
        if rpost['tipo'] == 'saida':
            jornada = func.jornada
            print(diadetrabalho.inicioem)
            print(diaanterior.inicioem)
            print(not diaanterior.encerrado)
            print(diaanterior.saida.time() == time(3, 0, 0))
            if diadetrabalho.entrou and not diadetrabalho.encerrado:
                diadetrabalho.saida = agora
                diadetrabalho.encerrado = True
                self.calcula_lancametos(diadetrabalho, func.jornada)
                #diferenca_entrada = diadetrabalho.entrada - jornada.entrada
            elif diaanterior.entrou and not diaanterior.encerrado and diaanterior.saida.time() == time(3, 0, 0):
                    diaanterior.saida = agora
                    diaanterior.encerrado = True
                    print('saidaanterior')
                    self.calcula_lancametos(diaanterior, func.jornada)
            else: 
                nada_alterado = True
        if not nada_alterado:
            diadetrabalho.save()
            diaanterior.save()
            return JsonResponse({'dia': agora.strftime('%d'), 'hora': f'{agora.strftime("%H:%M")}', 'model': model_to_dict(diadetrabalho)})
        else:
            return JsonResponse({'msg': 'Nada alterado'})
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
            useraltera = ua.escr.temacesso_set.get_object_or_404(user__id=get_original_id(rget['userid'], allusers)).user
        if user.eh_supervisor and useraltera.is_superuser:
            useraltera = ''
        context = {
            'ua': ua,
            'acesso': acesso,
            'is_superuser': allusers.filter(is_superuser=True),
            'eh_supervisor': allusers.filter(eh_supervisor=True),
            'eh_gerente': allusers.filter(eh_gerente=True),
            'eh_auxiliar': allusers.filter(eh_auxiliar=True),
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
                user.set_password(rpost['senha'])
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
            return HttpResponseRedirect(f'usuarios?userid={hash_id(user.id)}')


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
        print(emp)
        return JsonResponse({'msg': 'sucesso'})
    if rpost['modelo'] == 'notas':
        emp, comp = baixanotas(request.FILES['arquivo'], request.user)
        atu_ultimoacesso(emp, comp)
        return JsonResponse({'msg': 'sucesso'})
    if rpost['modelo'] == 'obras':
        resp = criar_obra(request.FILES['arquivo'], request.user)
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
            context = {'msg': 'Nenuhma obra cadastrada'}
        return JsonResponse(context, safe=False)

    if tipo == "funcnome":
        context = []
        func = emp.funcionario_set.filter(demitido=False)
        func = func.filter(nome__contains=val.upper()).order_by('nome')
        print(len(func) == 0)
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
        obra = ua.emp.alocacao_set.filter(obra__id=rget['obraid'])
        obra = obra.filter(comp__year=ua.comp.year)
        obra = obra.filter(comp__month=ua.comp.month)
        f = ua.emp.funcionario_set.get(id=rget['funcid'])
        obra[0].func.add(rget['funcid'])
        context = {'id': f.id, 'cod': f.cod, 'nome': f.nome}
        return JsonResponse(context, safe=False)
    if rget['tipo'] == 'excluir':
        obra = ua.emp.alocacao_set.filter(obra__id=rget['obraid'])
        obra = obra.filter(comp__year=ua.comp.year)
        obra = obra.filter(comp__month=ua.comp.month)
        print(obra[0])
        print(obra[0].func.get_queryset())
        obra[0].func.remove(rget['funcid'])
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

'''from usuarios.models import UsuarioManager
u = UsuarioManager()
u.create_superuser('guilherme@paulista.cnt.br', '19989434443', 'Guilherme', 'Guilherme', 'Navarro', 'uiui')
'''