import PyPDF2

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
    
