import requests
from bs4 import BeautifulSoup
import pdfkit
import uuid

def convert_html_to_pdf(html_content, pdf_path):
    try:
        pdfkit.from_string(html_content, pdf_path, options={"enable-local-file-access": "", 'encoding': "UTF-8"})        
    except Exception as e:
        print(f"PDF generation failed: {e}")

s = requests.Session()

id = '22532'
modalidade = 'PRE'
url = f'https://www.publinexo.com.br/publinexo/jsp/publico/pb_popup_ata.jsp?prg_id={id}&tipo=SR&tipoAta={modalidade}'
ata = s.get(url)

ataSoup = BeautifulSoup(ata.content, "html.parser")
html_text = str(ataSoup)
token = uuid.uuid4()
pdf_path = f"AtaPDF/{id}_{modalidade}_{token}.pdf"
convert_html_to_pdf(html_text, pdf_path)

with open(f'AtaHTML/{id}_{modalidade}_{token}.html', 'w', encoding='utf-8') as handler:
        handler.write(str(ataSoup))