import requests
from bs4 import BeautifulSoup
import re
import json

uasg = 925033
prodnum = 123456
edital = 900202024

url = f"http://comprasnet.gov.br/ConsultaLicitacoes/download/download_editais_detalhe.asp?coduasg={uasg}&modprp=5&numprp={edital}"

try:
    response = requests.get(url)
    response.raise_for_status()
    limpeza_response = re.sub(r'\s+', ' ', response.text)
    
    itens_dados = []

    itens = re.findall(r'Itens\sde\sMaterial(.*?)<\/table>', limpeza_response)
 
    for item in itens:
        numero_produto_match = re.search(r'<span class=\'tex3b\'>(\d+).*?</span>', item)
        numero_produto = numero_produto_match.group(1).strip() if numero_produto_match else 0

        descricao_match = re.search(r'</span><br><span class=\'tex3\'>(.*?)<br>', item)
        descricao = descricao_match.group(1).strip() if descricao_match else 'null'

        tratamento_match = re.search(r'Tratamento Diferenciado:\s(.*?)-.*?<br>', item)
        tratamento = tratamento_match.group(1).strip() if tratamento_match else 'null'
        me_epp = 'S' if tratamento in ['Tipo I '] else 'N' 

        decreto_match = re.search(r'Aplicabilidade Decreto 7174:\s(.*?)<br>', item)
        decreto = decreto_match.group(1).strip() if decreto_match else 'null'

        margem_preferencial_match = re.search(r'Aplicabilidade Margem de Preferência:\s(.*?)<br>', item)
        margem_preferencial = margem_preferencial_match.group(1).strip() if margem_preferencial_match else 'null'

        quantidade_match = re.search(r'Quantidade:\s(\d+)<br>', item)
        quantidade = quantidade_match.group(1).strip() if quantidade_match else 'null'

        unidade_fornecimento_match = re.search(r'Unidade de fornecimento:\s(.*?)\s</span>', item)
        unidade_fornecimento = unidade_fornecimento_match.group(1).strip() if unidade_fornecimento_match else 'null'

        itens_dados.append({
            'prodnum': prodnum,
            'item': numero_produto,
            'codigo': uasg,
            'descricao': descricao,
            'unidade': unidade_fornecimento,
            'quantidade': quantidade,
            'me_epp': me_epp
        })

    with open(f"AtaJSON/itens_{prodnum}_{uasg}.json", "w", encoding="utf-8") as f:
        json.dump({"itens": itens_dados}, f, indent=4, ensure_ascii=False)

    soup = BeautifulSoup(limpeza_response, 'html.parser')
    with open('page.html', 'w', encoding='utf-8') as handler:
        handler.write(str(soup))

except Exception as e:
    print(f"Erro ao acessar o site: {e}")
