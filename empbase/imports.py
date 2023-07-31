import re, io, pandas as pd
from django.db.models import F
from xml.dom.minidom import parse
from openpyxl.utils import get_column_letter
from xls2xlsx import XLS2XLSX
from empbase.models import Alocacao, Funcionario, Empresa, Imposto, Notas, Obras, Contribuintes

def xls_to_xlsx(xls_file_path, sheet_name='Sheet1'):
    # Read the .xls file into a pandas DataFrame
    xls_data = pd.read_excel(xls_file_path, sheet_name=sheet_name)

    # Convert the DataFrame to .xlsx format in memory
    xlsx_data = io.BytesIO()
    with pd.ExcelWriter(xlsx_data, engine='xlsxwriter') as writer:
        xls_data.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.save()

    # Reset the buffer position
    xlsx_data.seek(0)

    # Use the converted .xlsx data as needed (e.g., pass it to another function)
    # For example, you can read the converted data using pandas again:
    xlsx_df = pd.read_excel(xlsx_data, sheet_name=sheet_name)

    # Close the buffer
    xlsx_data.close()

    # Return the converted DataFrame
    return xlsx_df

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

def convertxlsx(arq):
    x2x = XLS2XLSX(arq)
    wb = x2x.to_xlsx()
    return wb

def criar_empresa(arq, usuario):
    if not '.xlsx' in arq.name:
        arq = xls_to_xlsx(arq)
    df = lerexcel(arq)
    col = pd.read_excel(arq, usecols='a')
    for i in range(len(col)):
        if col.iloc[i - 1][0] == 'DADOS CADASTRAIS':
            n = i - 4
            if df.loc[n + 5, 'E'] == '1000':
                break
            responsavel = df.loc[n + 21, 'J']
            iniciodata = df.loc[n + 5, 'J'].split('/')
            capital = df.loc[n + 25, 'J'].replace('.','').replace(',','.') if not isinstance(df.loc[n + 25, 'J'], float) != 'nan' else 0.0
            try:
                contribuinte = Contribuintes.objects.get(nome=responsavel)
            except:
                contribuinte = Contribuintes(nome=responsavel)
                contribuinte.save()
            try:
                empresa = Empresa.objects.get(cnpj = subs(df.loc[n + 24, 'E']))
            except:
                emp = Empresa(
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
                email = df.loc[n + 22, 'E'],
                responsavel = contribuinte)
                emp.usuario = usuario
                try:
                    empcadastrada = Empresa.objects.get(cnpj=emp.cnpj)
                    if empcadastrada.rsocial != emp.rsocial:
                        empcadastrada = emp
                        empcadastrada.usuario = usuario
                        empcadastrada.save()
                    if empcadastrada.cep != emp.cep:
                        empcadastrada = emp
                        empcadastrada.usuario = usuario
                        empcadastrada.save()
                except:
                    emp.save()


def criar_funcionario(arq, usuario):
    if not '.xlsx' in arq.name:
        arq = xls_to_xlsx(arq)
    df = lerexcel(arq)
    col = pd.read_excel(arq, usecols='am')
    for i in range(len(col)):
        if col.iloc[i - 1][0] == 'REGISTRO DE EMPREGADO':
            n = i-1
            cpfint = int(df.loc[n + 27, 'BP'])
            end = df.loc[n + 15, 'C'].split(',')
            localnasc = df.loc[n + 18, 'AN'].split(' - ') if not isinstance(df.loc[n + 18, 'AN'], float) else ['N defindo', 'N defindo']
            cnpj = str(df.loc[n + 7, 'CN']).replace('.0','')
            if len(cnpj) == 13:
                cnpj = '0' + cnpj
            contratante = usuario.temacesso.emp.get(cnpj=cnpj)
            demissao = None
            vezes = 0
            for y in range(20):
                vezes += 1
                y = y + n + 45
                if y <= len(col):
                    teste = df.loc[y, 'BX']
                    if not isinstance(teste, float):
                        if 'RESCISÃO DE CONTRATO DE TRABALHO' in teste:
                            demissao = df.loc[y + 2, 'CC'].strftime("%Y-%m-%d") if not isinstance(df.loc[y + 2, 'CC'], float) else None
                            print(df.loc[n + 4, 'AE'])
                            print(df.loc[y + 2, 'CC'])

            
            func = Funcionario(
            emp = contratante,
            cod = df.loc[n + 4, 'AE'],
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
            turno = df.loc[n + 36, 'BA'].replace('das ', ''),
            logradouro = end[0],
            num = end[1],
            bairro = end[-4],
            cidade = end[-3],
            uf = end[-2],
            cep = subs(end[-1]),
            datanasc = df.loc[n + 18, 'R'].strftime("%Y-%m-%d"),
            cidadenasc = localnasc[0],
            ufnasc = localnasc[1],
            genero = df.loc[n + 29, 'BR'],
            pai = df.loc[n + 20, 'AC'],
            mae = df.loc[n + 23, 'AC'],
            demissao = demissao, demitido = False if demissao == None else True)
            func.usuario = usuario

            funccad = contratante.funcionario_set.get(cod=func.cod)
            funccad.demitido = func.demitido
            funccad.salario = func.salario
            funccad.cargo = func.cargo
            funccad.cbo = func.cbo
            funccad.save()
    return contratante


def criar_obra(arq, usuario):
    if not '.xlsx' in arq.name:
        arq = xls_to_xlsx(arq)
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
    return "sucesso"


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
        comp = nf.getElementsByTagName('Competencia')[0].firstChild.nodeValue[:-9]
        valor = nf.getElementsByTagName('ValorServicos')[0].firstChild.nodeValue
        inss = nf.getElementsByTagName('ValorInss')[0].firstChild.nodeValue
        iss = nf.getElementsByTagName('ValorIss')[0].firstChild.nodeValue
        if numero in canceladalist:
            canc = 1
            valor = 0
            inss = 0
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
        try:
            if cnonum:
                servico = emp.obras_set.filter(cno__contains=subs(cnonum))[0]
            else:
                servico = emp.obras_set.filter(cnpj__contains=subs(cnpjtom))
                for o in servico:
                    if o.cno == None:
                        servico = o 
        except:
            pass
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
            aloc = emp.alocacao_set.filter(obra=servico, comp=comp[0:7]+'01')
            if not aloc: 
                Alocacao.objects.create(emp=emp, nota=nota, obra=servico, comp=comp[0:7]+'01')
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
    #arq = 'Y:\_Arquivo_envio\Resumo Mensal.xlsx'
    if not '.xlsx' in arq.name:
        arq = xls_to_xlsx(arq)
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

