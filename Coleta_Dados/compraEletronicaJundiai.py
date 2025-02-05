import requests
from bs4 import BeautifulSoup
import json
import uuid
import os
from datetime import date

s = requests.Session()

prodnum = '12345678'
id = '42092'
edital_anterior = '1/2024'
edital = edital_anterior.replace('/','_')

url = f"https://compraeletronica.jundiai.sp.gov.br/aberto/mural.aspx?cdcompra={id}"

ano = date.today().year
mes = date.today().month
nomeMeses = [
            'janeiro',
            'fevereiro',
            'marco',
            'abril',
            'maio',
            'junho',
            'julho',
            'agosto',
            'setembro',
            'outubro',
            'novembro',
            'dezembro'
        ]
nome_mes = nomeMeses[mes - 1]

dir_path = f'AtaJSON/{ano}/{nome_mes}'
os.makedirs(dir_path, exist_ok=True)

def limpar_valor(valor):
    if valor == "null":
        return 0.0
    valor_limpo = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0

try:
    response = requests.get(url)
    response.raise_for_status() 
    soup = BeautifulSoup(response.text, 'html.parser')

    produtos = []
    tabela = soup.find('table', id='TabContainer1_tabItens_grdItem')

    if tabela:
        for tr in tabela.find_all('tr')[1:]:
            cols = tr.find_all('td')
            if len(cols) > 2:
                item = cols[0].text.strip()
                produto_desc = cols[1].text.strip()
                quantidade = cols[2].text.strip()
                
                quantidade_num = int(quantidade.replace(',0000', ''))

                produto = {
                    'prodnum': prodnum,
                    'item': item,
                    'codigo': id,
                    'descricao': produto_desc,
                    'quantidade': quantidade,
                    'situacao': None,
                    'vencedor': None,
                    'valor_unitario': None,
                    'valor_total': None,
                }
                produtos.append(produto)

    lances = []
    i = 0
    while True:
        table_id = f'TabContainer1_tabLances_GridCompraMod1_rtpItens_ctl{i:02}_grdAnalise'
        tabela_lances = soup.find('table', id=table_id)

        if tabela_lances:
            rows = tabela_lances.find_all('tr')[1:]
            colocacao = 1
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    empresa = cols[0].text.strip() if len(cols) > 0 else "null"
                    lance_final = cols[2].text.strip() if len(cols) > 2 else "null"
                    marca = cols[3].text.strip() if len(cols) > 3 else "null"
                    
                    lance_final_num = limpar_valor(lance_final)
                    valor_total = lance_final_num * quantidade_num

                    if colocacao == 1:
                        produtos[i]['vencedor'] = empresa
                        produtos[i]['valor_unitario'] = lance_final_num
                        produtos[i]['valor_global'] = valor_total

                    if any('vencedor.gif' in img['src'] for img in cols[0].find_all('img')):
                        resultados = {
                            'prodnum': prodnum,
                            'item': i + 1,
                            'empresa': empresa,
                            'colocacao': '1',
                            'descricao': produto_desc,
                            'marca': marca,
                            'quantidade': quantidade_num,
                            'valor_unitario': lance_final_num,
                            'valor_total': valor_total,
                            'EAN': None
                        }
                        lances.append(resultados)
                    else:
                        lances.append({
                            'prodnum': prodnum,
                            'item': i + 1,
                            'empresa': empresa,
                            'colocacao': str(colocacao),
                            'descricao': produto_desc,
                            'marca': marca,
                            'quantidade': quantidade_num,
                            'valor_unitario': lance_final_num,
                            'valor_total': valor_total,
                        })
                    colocacao += 1

            ctl_num = f"ctl{str(i).zfill(2)}"
            span_id = f'TabContainer1_tabLances_GridCompraMod1_rtpItens_{ctl_num}_lblSituacaoItem'
            situacao_span = soup.find('span', id=span_id)
            if situacao_span:
                situacao = situacao_span.text.strip()
                produtos[i]['situacao'] = situacao
            else:
                produtos[i]['situacao'] = None

            i += 1
        else:
            break

    idUuid = uuid.uuid4()

    with open(f'AtaJSON/{ano}/{nome_mes}/resultados_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as f:
        json.dump({'resultados': lances}, f, ensure_ascii=False, indent=4)

    with open(f'AtaJSON/{ano}/{nome_mes}/itens_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as f:
        json.dump({'itens': produtos}, f, ensure_ascii=False, indent=4)

except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro: {e}")
