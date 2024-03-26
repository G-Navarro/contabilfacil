from datetime import date, datetime, timedelta
import re, io, pandas as pd
import numpy as np
from django.db.models import F
from xml.dom.minidom import parse
from openpyxl.utils import get_column_letter
from empbase.models import Alocacao, Funcionario, Empresa, Holerite, Imposto, Notas, Obras, Contribuintes, PeriodoAquisitivo, TemAcesso, Tramites, Turno, UltimoAcesso, ValeTransporte
from usuarios.models import Usuario

def lerexcel(nome):
    df = pd.read_excel(nome, header=None)
    col_names = [get_column_letter(col_num) for col_num in range(1, len(df.columns)+1)]
    df.columns = col_names
    return df


def subs(x):
    t = re.sub(r'[^0-9]', '', x)
    return t

def convertedata(data):
    print(data)
    print(type(data))
    data = data.split('/')
    data = f'{data[2]}-{data[1]}-{data[0]}'
    return data


def criar_empresa(arq, usuario):
    df = lerexcel(arq)
    col = pd.read_excel(arq, usecols='a')
    escritorio = usuario.ultimoacesso.escr
    for i in range(len(col)):
        if col.iloc[i - 1][0] == 'DADOS CADASTRAIS':
            n = i - 4
            if df.loc[n + 5, 'E'] == '1000':
                break
            responsavel = df.loc[n + 21, 'J']
            iniciodata = df.loc[n + 5, 'J'].split('/') if not isinstance(df.loc[n + 5, 'J'], float) else ['01','01','1900']
            capital = df.loc[n + 25, 'J'].replace('.','').replace(',','.') if not isinstance(df.loc[n + 25, 'J'], float) != 'nan' else 0.0
            try:
                contribuinte = Contribuintes.objects.get(nome=responsavel)
            except:
                contribuinte = Contribuintes(nome=responsavel)
                contribuinte.save()
            
            empresa = escritorio.empresa_set.filter(cnpj = subs(df.loc[n + 24, 'E']))
            if not empresa:
                emp = escritorio.empresa_set.create(
                cod = df.loc[n + 5, 'E'],
                cnpj = subs(df.loc[n + 24, 'E']),
                inscest = subs(df.loc[n + 25, 'E']) if not isinstance(df.loc[n + 25, 'E'], float) else None,
                inscmun = subs(df.loc[n + 26, 'E']) if not isinstance(df.loc[n + 26, 'E'], float) else None,
                inscjunta = subs(df.loc[n + 27, 'E']) if not isinstance(df.loc[n + 27, 'E'], float) else None,
                apelido = df.loc[n + 6, 'E'],
                nome = df.loc[n + 7, 'E'],
                rsocial = df.loc[n + 8, 'E'],
                natjuridica = df.loc[n + 8, 'J'],
                inicio = f'{iniciodata[2]}-{iniciodata[1]}-{iniciodata[0]}',
                tipoend = df.loc[n + 10, 'E'],
                endereco = df.loc[n + 11, 'E'],
                num = df.loc[n + 12, 'E'],
                bairro = df.loc[n + 13, 'E'],
                municipio = df.loc[n + 15, 'E'],
                uf = df.loc[n + 16, 'E'],
                pais = df.loc[n + 19, 'E'],
                cep = df.loc[n + 17, 'E'],
                cnae = df.loc[n + 18, 'J'],
                capital = capital,
                situacao = df.loc[n + 12, 'J'],
                email = df.loc[n + 22, 'E'],
                escr = escritorio,
                responsavel = contribuinte)
                emp.usuario = usuario
                usuario.temacesso.emp.add(emp)

def cria_periodo(func, periodoinicio):
    datainicio = periodoinicio
    if periodoinicio.day == 29 and periodoinicio.month == 2:
        periodoinicio = periodoinicio.replace(day=28)
    teste = periodoinicio.replace(year=periodoinicio.year + 1)
    periodofim = teste - timedelta(days=1)
    datamaximacalc = PeriodoAquisitivo()
    if func.demitido:
        diasdedireito = 0
    else:
        diasdedireito = 30
    return func.periodoaquisitivo_set.create(emp=func.emp, periodoinicio=datainicio, periodofim=periodofim, datamaxima = datamaximacalc.datamaxima_calc(periodofim), diasdedireito=diasdedireito)

def cria_ferias(periodo, inicio, final):
    feriasnova = periodo.ferias_set.create(
            aviso = inicio - timedelta(days=30),
            inicio = inicio,
            final = final
            )
    feriasnova.tramite.add(Tramites.objects.create(
        emp = periodo.func.emp,
        nome = 'Finalizado',
        finalizado = True))
    dias = (final - inicio).days
    if periodo.diasdedireito > 0:
        periodo.diasdedireito -= (dias + 1)
    periodo.save()
    return feriasnova


def criar_funcionario(arq, usuario):
    df = lerexcel(arq)
    if type(df.loc[2, 'F']) == str:
        if 'RELACAO PARA COMPRA' in df.loc[2, 'F']:
            col = pd.read_excel(arq, usecols='a')
            tamanho = range(len(col))
            contratante = usuario.temacesso.emp.get(nome=df.loc[0, 'A'])
            for i in tamanho:
                if type(df.loc[i, 'A']) != float:
                    if subs(df.loc[i, 'A']):
                        vtinfo = df.loc[i + 1, 'C']
                        print(subs(df.loc[i, 'A']))
                        vt, vtcriado = ValeTransporte.objects.get_or_create(emp=contratante, nome=vtinfo, valor=df.loc[i + 1, 'I'])
                        func = contratante.funcionario_set.filter(cod=subs(df.loc[i, 'A']))
                        if func:
                            func[0].vt = vt if vt else vtcriado
                            func[0].save()
            return contratante
        
    if type(df.loc[3, 'H']) == str:
        if 'FÉRIAS CALCULADAS' in df.loc[3, 'H']:
            col = pd.read_excel(arq, usecols='a')
            tamanho = range(len(col))
            for i in tamanho:
                celula = df.loc[i, 'A'] if type(df.loc[i, 'A']) == str else 'gangnam style'
                if 'CNPJ' in celula:
                    cnpj = subs(df.loc[i, 'D'])
                    contratante = usuario.temacesso.emp.get(cnpj=cnpj)
                    for n in tamanho:
                        n = n + i + 1
                        if n == len(col):
                            break
                        celula = df.loc[n, 'A'] if type(df.loc[n, 'A']) != float else ''
                        try: 
                            celula = int(celula)
                        except:
                            pass
                        
                        if type(celula) == int:
                            func = contratante.funcionario_set.get(cod=df.loc[n, 'A'])
                            periodoinicio = datetime.strptime(df.loc[n, 'K'], '%d/%m/%Y').date(),
                            periodofim = datetime.strptime(df.loc[n + 1, 'K'], '%d/%m/%Y').date(),
                            inicio = datetime.strptime(df.loc[n, 'N'], '%d/%m/%Y').date(),
                            final = datetime.strptime(df.loc[n + 1, 'N'], '%d/%m/%Y').date(),
                            periodo = func.periodoaquisitivo_set.filter(periodoinicio = periodoinicio[0]).first()
                            if periodoinicio[0].day == 29 and periodoinicio[0].month == 2:
                                periodoinicio = periodoinicio[0].replace(day=28)
                            else:
                                periodoinicio = periodoinicio[0]
                            if periodo:
                                ferias = periodo.ferias_set.filter(inicio = inicio[0])
                                if not ferias:
                                    ferias = cria_ferias(periodo, inicio[0], final[0])
                                periodo = func.periodoaquisitivo_set.filter(periodoinicio = periodoinicio.replace(year=periodoinicio.year + 1)).first()
                                if not periodo:
                                    cria_periodo(func, periodoinicio.replace(year=periodoinicio.year + 1))
                            else:
                                periodo = cria_periodo(func, periodoinicio)
                                ferias = cria_ferias(periodo, inicio[0], final[0])
                            if func.demitido:
                                feriasabertas = func.periodoaquisitivo_set.filter(diasdedireito__gt=0)
                                for ferias in feriasabertas:
                                    ferias.diasdedireito = 0
                                    ferias.save()
                        if 'CNPJ' in str(celula) and cnpj != subs(df.loc[n, 'D']):
                            break
                    return contratante
                
    col = pd.read_excel(arq, usecols='am')
    for i in range(len(col)):
        if col.iloc[i - 1][0] == 'REGISTRO DE EMPREGADO':
            n = i-1
            cpfint = int(df.loc[n + 27, 'BP'])
            end = df.loc[n + 15, 'C'].split(',')
            localnasc = df.loc[n + 18, 'AN'].split(' - ') if not isinstance(df.loc[n + 18, 'AN'], float) else ['N defindo', 'N defindo']
            cnpj = str(df.loc[n + 7, 'CO']).replace('.0','')
            if len(cnpj) == 13:
                cnpj = '0' + cnpj
            contratante = usuario.temacesso.emp.get(cnpj=cnpj)
            jornadapadrao = Turno.objects.filter(emp=contratante).first()
            if not jornadapadrao:
                jornadapadrao = Turno.objects.create(emp=contratante)
            demissao = None
            vezes = 0
            for y in range(20):
                vezes += 1
                y = y + n + 45
                if y <= len(col):
                    teste = df.loc[y, 'BX']
                    if not isinstance(teste, float):
                        if 'RESCISÃO DE CONTRATO DE TRABALHO' in teste:
                            if not isinstance(df.loc[y + 2, 'CC'], float):
                                demissao = df.loc[y + 2, 'CC']


            if not pd.isna(df.loc[n + 18, 'S']):
                datanasc = df.loc[n + 18, 'S'].strftime("%Y-%m-%d")
            else:
                datanasc = df.loc[n + 18, 'R'].strftime("%Y-%m-%d")
            func = Funcionario(
            emp = contratante,
            cod = df.loc[n + 4, 'CY'],
            matesocial = df.loc[n + 4, 'AE'],
            nome = df.loc[n + 13, 'C'],
            cpf = str(cpfint) if len(str(cpfint)) == 11 else '0' + str(cpfint),
            pis = df.loc[n + 43, 'O'],
            admissao = df.loc[n + 36, 'C'].strftime("%Y-%m-%d"),
            salario = df.loc[n + 36, 'Y'],
            cargo = df.loc[n + 33, 'S'],
            cbo = df.loc[n + 33, 'CV'],
            rg = df.loc[n + 25, 'R'],
            rgemiss = df.loc[n + 25, 'AN'].strftime("%Y-%m-%d") if not pd.isna(df.loc[n + 25, 'AN']) else None,
            rgorgao = df.loc[n + 25, 'AZ'],
            ctps = df.loc[n + 27, 'R'],
            ctpsserie = df.loc[n + 27, 'AE'],
            ctpsdata = df.loc[n + 27, 'AP'].strftime("%Y-%m-%d") if not pd.isna(df.loc[n + 27, 'AP']) else None,
            ctpsuf = df.loc[n + 27, 'BH'],
            jornada = jornadapadrao,
            logradouro = end[0],
            num = end[1],
            bairro = end[-4],
            cidade = end[-3],
            uf = end[-2],
            cep = subs(end[-1]),
            datanasc = datanasc,
            cidadenasc = localnasc[0],
            ufnasc = localnasc[1],
            genero = df.loc[n + 29, 'BR'],
            pai = df.loc[n + 20, 'AC'],
            mae = df.loc[n + 23, 'AC'],
            demissao = demissao, demitido = False if demissao == None else True,)
            func.usuario = usuario
            funccad = contratante.funcionario_set.filter(cpf=func.cpf, admissao=func.admissao).first()
            if funccad:
                funccad.cod = func.cod
                funccad.matesocial = func.matesocial
                funccad.demissao = func.demissao
                funccad.demitido = func.demitido
                funccad.salario = func.salario
                funccad.cargo = func.cargo
                funccad.cbo = func.cbo
                funccad.save()
                if not funccad.periodoaquisitivo_set.filter(periodoinicio=func.admissao):
                    datacalculo = funccad.admissao
                    cria_periodo(funccad, datacalculo)
            else:
                if not func.demitido:
                    func.funcacesso = Usuario.objects.create_funcionario(usuario=str(contratante.cod) + func.cod + func.nome.split(' ')[0], nome=func.nome.split(' ')[0], snome=func.nome.split(' ')[-1], password=func.cpf[0:6])
                    UltimoAcesso.objects.create(escr=contratante.escr,emp=contratante,user=func.funcacesso,comp=date.today())
                    temacesso = TemAcesso.objects.create(user=func.funcacesso)
                    temacesso.escr.add(contratante.escr)
                    temacesso.emp.add(contratante)
                func.save()
                datacalculo = datetime.strptime(func.admissao, '%Y-%m-%d')
                cria_periodo(func, datacalculo)
    return contratante


def criar_obra(arq, usuario):
    df = lerexcel(arq)
    col = pd.read_excel(arq, usecols='b')
    emp = str(df.loc[17, 'I']).replace('.0', '')
    if emp != None:
        emp = '0'+emp if len(emp) == 13 else emp
    emp = usuario.temacesso.emp.get(cnpj=emp)
    for i in range(len(col)):
        if col.iloc[i-2][0] == 'Código............:':
            n = i-6
            tipo = df.loc[n + 18, 'E']
            cnpj = str(df.loc[n + 18, 'I']).replace('.0', '') if 'CNPJ' in tipo else None
            cno = str(df.loc[n + 18, 'I']).replace('.0', '') if not 'CNPJ' in tipo else None
            if cnpj != None:
                cnpj = '0'+cnpj if len(cnpj) == 13 else cnpj
            if 'CNPJ' in tipo:
                obra_existe = emp.obras_set.filter(cnpj=cnpj)
            else:
                obra_existe = emp.obras_set.filter(cno=cno)
            
            if len(obra_existe) > 1:
                print(obra_existe)
            if len(obra_existe) == 1:
                obra_existe.update(
                    cod = df.loc[n + 5, 'E'],
                    endereco = df.loc[n + 9, 'E'],
                    num = df.loc[n + 10, 'E'],
                    bairro = df.loc[n + 12, 'E'],
                    municipio = df.loc[n + 13, 'E'],
                    uf = df.loc[n + 14, 'E'],
                    cep = df.loc[n + 15, 'E'])
            elif len(obra_existe) == 0:
                Obras.objects.create(cod = df.loc[n + 5, 'E'],
                cnpj = cnpj,
                cno = cno,
                nome = df.loc[n + 6, 'E'],
                endereco = df.loc[n + 9, 'E'],
                num = df.loc[n + 10, 'E'],
                bairro = df.loc[n + 12, 'E'],
                municipio = df.loc[n + 13, 'E'],
                uf = df.loc[n + 14, 'E'],
                cep = df.loc[n + 15, 'E'],
                emp = emp, 
                usuario = usuario)
    return emp


def baixanotas(arquivo, usuario):
    xml = parse(arquivo)
    print(arquivo)
    nfs = xml.getElementsByTagName('InfNfse')
    nfscancelada = xml.getElementsByTagName('CancelamentoNfse')
    canceladalist = []
    nfdic = []
    valortotal = 0
    valoriss = 0
    valorinss = 0
    vezes = 1

    for nf in nfscancelada:
        canceladalist.append(nf.getElementsByTagName('Numero')[0].firstChild.nodeValue)

    for nf in nfs:
        vezes += 1
        emp = subs(nf.getElementsByTagName('Cnpj')[0].firstChild.nodeValue)
        if emp != None:
            emp = '0'+emp if len(emp) == 13 else emp
        emp = usuario.temacesso.emp.get(cnpj=emp)
        canc = 0
        numero = nf.getElementsByTagName('Numero')[0].firstChild.nodeValue
        comp = datetime.strptime(nf.getElementsByTagName('Competencia')[0].firstChild.nodeValue.split('T')[0], "%Y-%m-%d")
        valor = nf.getElementsByTagName('ValorServicos')[0].firstChild.nodeValue
        inss = nf.getElementsByTagName('ValorInss')[0].firstChild.nodeValue
        iss = nf.getElementsByTagName('ValorIss')[0].firstChild.nodeValue

        if numero in canceladalist:
            canc = 1
        try:
            cnpjtom = nf.getElementsByTagName('Cnpj')[2].firstChild.nodeValue
        except IndexError:
            cnpjtom = nf.getElementsByTagName('Cpf')[0].firstChild.nodeValue
        nometom = nf.getElementsByTagName('RazaoSocial')[1].firstChild.nodeValue
        endtom = nf.getElementsByTagName('Endereco')[2]
        ruatom = endtom.getElementsByTagName('Endereco')[0].firstChild.nodeValue
        try:
            numtom = nf.getElementsByTagName('Numero')[2].firstChild.nodeValue
        except AttributeError:
            numtom = 'Não definido'
        bairrotom = nf.getElementsByTagName('Bairro')[1].firstChild.nodeValue
        uftom = nf.getElementsByTagName('Uf')[2].firstChild.nodeValue
        try:    
            ceptom = nf.getElementsByTagName('Cep')[1].firstChild.nodeValue
        except:
            ceptom = None
        descr = nf.getElementsByTagName('Discriminacao')[0].firstChild.nodeValue.lower()
        descricao = descr.replace('.', '').lower()
        descricao = descricao.split(' ')
        cno = "Não tem CNO"
        cnonum = None
        if canc == 0:
            valortotal = valortotal + float(valor)
            valoriss = valoriss + float(iss)
            valorinss = valorinss + float(inss)

        if 'cno' in descr:
            cno = 'cno'
        elif 'c.n.o' in descr:
            cno = 'c.n.o'
        elif 'cei' in descr:
            cno = 'cei'
        elif 'c.e.i' in descr:
            cno = 'c.e.i'
        for index in descricao:
            if '/' in index and len(re.sub(r'[^0-9]', '', index)) == 12:
                cnonum = re.sub(r'[^0-9]', '', index)

        if cnonum:
            servico = emp.obras_set.filter(cno__contains=subs(cnonum)).first()
        else:
            servico = emp.obras_set.filter(cnpj__contains=subs(cnpjtom)).filter(cno=None).first()

        if not servico:
            servico = emp.obras_set.create(emp=emp, cod=None, cnpj=subs(cnpjtom), cno=cnonum, nome=nometom,
                endereco=ruatom, num=numtom, bairro=bairrotom, uf=uftom, cep=ceptom)
        
        try: 
            nota = emp.notas_set.get(numero=numero)
            if nota.canc == 0 and canc == 1:
                nota.canc = 1
                nota.save()  
        except:
            nota = emp.notas_set.create(emp=emp, numero=numero, canc=canc, comp=comp, valor=valor, inss=inss, iss=iss, tomador=servico)
        
        aloc = emp.alocacao_set.filter(obra=servico, comp=comp)
        if not aloc:          
            Alocacao.objects.create(emp=emp, nota=nota, obra=servico, comp=comp)

    return emp, comp

class conferencia():
    cnpj = ''


def cria_imposto(emp, nome, valor, comp):
    imposto = emp.imposto_set.filter(nome=nome, comp=comp)
    if imposto:
        imposto = imposto[0]
        imposto.valor = valor
        imposto.save()
    if not imposto:
        return Imposto.objects.create(emp=emp, nome=nome, valor=valor, comp=comp)


def cad_imposto(arq, user):
    df = lerexcel(arq)
    col = pd.read_excel(arq, usecols='a')
    confere = conferencia()
    if 'RESUMO DA FOLHA' in df.loc[6, 'A']:
        for i in range(len(col)):
            base = col.iloc[i][0]
            base = '' if  isinstance(base, float) or isinstance(base, int) else base
            if 'CNPJ:' in base:
                n = i - 1
                cnpj = df.loc[n + 2, 'E']
                if confere.cnpj == cnpj:
                    pass
                else:
                    confere.cnpj = cnpj
                    emp = user.temacesso.emp.get(cnpj=cnpj)
                    comp = df.loc[n + 4, 'E']
                    for x in range(300):
                        y = x + n + 2
                        if y >= len(col):
                            break
                        m = '' if isinstance(df.loc[y, 'M'], (float, int)) else df.loc[y, 'M']
                        z = '' if isinstance(df.loc[y, 'Z'], (float, int)) else df.loc[y, 'Z']

                            
                        if 'Total INSS:' in m:
                            nome = 'INSS'
                            valor = df.loc[y, 'Q']
                            if valor != 0:
                                if emp.exonera_folha:
                                    notas = emp.notas_set.filter(comp__year=comp.year, comp__month=comp.month)
                                    total = 0.0
                                    for nota in notas:
                                        total += nota.valor
                                    valor = total*0.045 + (valor - total*0.035)
                                cria_imposto(emp, nome, "{:.2f}".format(valor), comp)
                        if 'Valor Total do IRRF:' in z:
                            nome = 'IR'
                            valor = df.loc[y, 'AK']
                            if valor != 0:
                                cria_imposto(emp, nome, "{:.2f}".format(valor), comp)
                        if 'Valor do FGTS:' in z:
                            nome = 'FGTS'
                            valor = df.loc[y, 'AK']
                            if valor != 0:
                                fgts = cria_imposto(emp, nome, "{:.2f}".format(valor), comp)
                            break
    return 'sucesso'


def cad_pagamento(arq, user):    
    df = lerexcel(arq)
    col = pd.read_excel(arq, usecols='a')
    tamanho_col = len(col) - 2
    for i in range(tamanho_col):
        base = col.iloc[i][0]
        base = base if isinstance(base, str) else ''
        if 'CNPJ:' in base:
            i=i+1
            cnpj = subs(df.loc[i, 'J'])
            emp = user.temacesso.emp.get(cnpj=cnpj)
            tipo = df.loc[i + 1, 'J']
            if tipo == 'Adiantamento':
                tipo = Holerite.Tipo.AD
            elif tipo == 'Folha Mensal':
                tipo = Holerite.Tipo.FM
            elif tipo == '13o. Adiantamento':
                tipo = Holerite.Tipo.AD13
            elif tipo == '13o. Integral':
                tipo = Holerite.Tipo.FM13
            comp = df.loc[i, 'AM']
            comp = datetime.strptime('01' + comp[2:10], "%d/%m/%Y")
            holerite = emp.holerite_set.filter(tipo=tipo, comp=comp).first()
            if not holerite:
                holerite = emp.holerite_set.create(tipo=tipo, comp=comp)
            for x in range(tamanho_col - i):
                x = x + i + 2
                cod = '' if isinstance(df.loc[x, 'A'], float) else df.loc[x, 'A']
                if 'CNPJ:' in cod:
                    break
                else:
                    try:                      
                        func = emp.funcionario_set.get(cod=int(cod))
                        val_paga = float(df.loc[x, 'AG'].replace('.', '').replace(',', '.'))
                        pagamento = holerite.funcs.filter(func=func).first()
                        if not pagamento:
                            pagamento = func.pagamento_set.create(valor=val_paga)
                            holerite.funcs.add(pagamento)
                        else:
                            pagamento.valor = val_paga
                            pagamento.save()
                    except ValueError as e:
                        pass
    return emp, comp
