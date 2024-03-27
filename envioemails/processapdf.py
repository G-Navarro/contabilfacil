from datetime import datetime
import re, PyPDF2, pdf2image
from pyzbar import pyzbar

from empbase.models import TiposGuia

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
        passe = [True if teste in pdf else False for teste in teste]
        print(passe, teste)
        return tipo_guia
        
def processa_guia(arquivos, user):
    for arquivo in arquivos:
        pdf = ler_pdf(arquivo.name)
        print(pdf)
        tipo_guia = define_guia(pdf)
        print(tipo_guia)
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

        #acha o valor
        valor_padrao = re.findall(r'\b\d+[\d,.]*,\d+\b', pdf)
        valor_float = [float(o.replace('.','').replace(',','.')) for o in valor_padrao]
        valor = max(valor_float)

        #acha competencia
        comp = re.search(tipo_guia.comp_regex, pdf).group()

        #acha formas de pagamento 
        padrao_barcode = re.search(r'\d{11}\s\d\s\d{11}\s\d\s\d{11}\s\d\s\d{11}\s\d', pdf)
        codigo_barra = padrao_barcode.group() if padrao_barcode else None

        #acha o copia e cola pix
        copia_cola = [qrcode if 'gov.bcb.pix' in qrcode else None for qrcode in extract_qr_code(arquivo)[0]][0]
        '''pixini = re.search(r'\d{4}\d{15}[A-Za-z.]+', pdf).span()[0]
        pixfim = re.search(r'\*{3}\w{8}', pdf).span()[1]
        pix_copia = pdf[pixini-1:pixfim] if pixini and pixfim else None'''
        imposto = emp.imposto_set.create(
            nome = 'FGTS Digital',
            valor=valor,
            comp=comp,
            vcto=vcto,
            identificador='1',
            barcode=codigo_barra,
            pix=copia_cola,
            guia=arquivo
        )
    return emp
