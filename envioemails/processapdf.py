from datetime import datetime
import re, PyPDF2

def ler_pdf(file):
    try:
        pdfFileObj = open(file, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[0]
        pdf = pageObj.extract_text()
        pdf_split = pdf.split('\n')
        pdfFileObj.close()
        return pdf, pdf_split
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    

def processa_guia(arquivo, user):
    pdf, pdf_split = ler_pdf(arquivo)
    padrao_cnpj = '\d{2}.\d{3}.\d{3}/\d{4}-\d{2}'
    cnpj = re.search(padrao_cnpj, pdf)
    emp = user.temacesso.emp.get(cnpj=cnpj)
    if 'Documento de Arrecadação do Simples Nacional' in pdf:
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
        #acha o codigo de barra
        codigo_barra = re.search('\d{11}\s\d\s\d{11}\s\d\s\d{11}\s\d\s\d{11}\s\d', pdf)
        #acha o copia e cola pix
        pixini = re.search(r'\d{4}\d{15}[A-Za-z.]+', pdf).span()[0]
        pixfim = re.search(r'\*{3}\d{4}[A-Z]{2}\d{2}', pdf).span()[1]
        pix_copia = pdf[pixini-1:pixfim]

