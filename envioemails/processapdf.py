from datetime import date, datetime
import re, PyPDF2, pdf2image
import tempfile
from pyzbar import pyzbar

from empbase.models import Imposto, TiposGuia

meses = {
    'Janeiro': '01',
    'Fevereiro': '02',
    'Março': '03',
    'Abril': '04',
    'Maio': '05',
    'Junho': '06',
    'Julho': '07',
    'Agosto': '08',
    'Setembro': '09',
    'Outubro': '10',
    'Novembro': '11',
    'Dezembro': '12'
}

def subs(x):
    t = re.sub(r'[^0-9]', '', x)
    return t


def ler_pdf(file):
    try:
        pdfFileObj = open(file, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[0]
        pdf = pageObj.extract_text()
        pdfFileObj.close()
        return pdf
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    

def extract_qr_code(pdf_path):
    images = pdf2image.convert_from_path(pdf_path)
    qr_codes = []
    for i, image in enumerate(images):
        qr_codes_on_page = []
        for barcode in pyzbar.decode(image):
            qr_codes_on_page.append(barcode.data.decode("utf-8"))
        qr_codes.append(qr_codes_on_page)
    return qr_codes


def define_guia(pdf):
    for tipo_guia in TiposGuia.objects.all():
        teste = tipo_guia.ident_tipo_guia.split(',') if ',' in tipo_guia.ident_tipo_guia else [tipo_guia.ident_tipo_guia]
        confirma = [x in pdf for x in teste]
        print(confirma)
        if all(confirma):
            return tipo_guia


def arquivos_temporarios(arquivos):
    temp_files = []
    for uploaded_file in arquivos:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        temp_file.flush()
        temp_file.seek(0)
        temp_files.append([temp_file, uploaded_file])
    return temp_files


def processa_guia(arquivos, user):
    arquivos = arquivos_temporarios(arquivos)
    for arquivo, guia in arquivos:
        pdf = ler_pdf(arquivo.name)
        tipo_guia = define_guia(pdf)
        print(tipo_guia.nome)
        padrao_cnpj_base = re.search(r'\d{2}.\d{3}.\d{3}', pdf)
        padrao_cpf = re.search(r'\d{3}.\d{3}.\d{3}-\d{2}', pdf)
        cnpj = padrao_cnpj_base.group() + '0001' if padrao_cnpj_base else padrao_cpf.group()
        emp = user.temacesso.emp.get(cnpj__contains=subs(cnpj))

        #acha o vencimento
        padrao_data = '\d{2}\/\d{2}\/\d{4}'
        datas = re.findall(padrao_data, pdf)
        date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in datas]
        biggest_date = max(date_objects)
        vcto = biggest_date 
        '''if biggest_date.date() < date.today(): 
            break'''

        #acha o valor
        valor_padrao = re.findall(r'\b\d+[\d,.]*,\d+\b', pdf)
        valor_float = [float(o.replace('.','').replace(',','.')) for o in valor_padrao]
        valor = max(valor_float)

        #acha competencia
        comp = re.search(tipo_guia.comp_regex, pdf).group()
        if re.search(r'[a-zA-Z]+', comp):
            compsplit = comp.split('/')
            comp = f'01/{subs(meses[compsplit[0]])}/{subs(compsplit[1])}'
        elif re.search(r'\d{2}/\d{4}', comp):
            comp = '01/' + re.search(r'\d{2}/\d{4}', comp).group()
        comp = datetime.strptime(comp, '%d/%m/%Y')
        #acha formas de pagamento 
        padrao_barcode = re.search(r'\d{11}\s\d\s\d{11}\s\d\s\d{11}\s\d\s\d{11}\s\d', pdf)
        codigo_barra = padrao_barcode.group() if padrao_barcode else None

        #acha o copia e cola pix
        copia_cola = [qrcode if 'gov.bcb.pix' in qrcode else None for qrcode in extract_qr_code(arquivo.name)[0]][0]
        identificador = re.search(tipo_guia.ident_cod_guia, pdf).group()
        '''pixini = re.search(r'\d{4}\d{15}[A-Za-z.]+', pdf).span()[0]
        pixfim = re.search(r'\*{3}\w{8}', pdf).span()[1]
        pix_copia = pdf[pixini-1:pixfim] if pixini and pixfim else None'''
        guias = emp.imposto_set.filter(tipoguia=tipo_guia, comp=comp)
        msg = []
        if guias:
            for guia in guias:
                if guia.identificador == identificador:
                    msg.append(f'Guia {guia.tipoguia.nome} da empresa {guia.emp.apelido} de {guia.comp.strftime("%m/%Y")} com identificador {guia.identificador} já existe')
        else:
            imposto = Imposto(
                emp=emp,
                tipoguia = tipo_guia,
                valor=f"{valor:.2f}",
                comp=comp.date(),
                vcto=vcto.date(),
                identificador=identificador,
                barcode=codigo_barra,
                pix=copia_cola,
                guia=guia
            )
            imposto.save()
            msg.append(f'Guia {imposto.tipoguia.nome} da empresa {imposto.emp.apelido} de {imposto.comp.strftime("%m/%Y")} com identificador {imposto.identificador} foi criada')
    return msg