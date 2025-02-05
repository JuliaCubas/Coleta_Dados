import requests
from bs4 import BeautifulSoup
from datetime import date
import json
import re
import uuid
import os

s = requests.Session()

id = '210907'
edital_anterior = '897/2020'
edital = edital_anterior.replace('/','_')

url = f'https://www.e-compras.am.gov.br/publico/licitacoes_acompanhamento.asp?ident={id}'

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

try:
    response = s.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    produtos = []

    tabelas_produtos = soup.find_all('table', {'id': 'tbl_item'})

    item_numero = 1

    for tabela in tabelas_produtos:
        linhas = tabela.find_all('tr')

        if len(linhas) >= 2:
            descricao = linhas[0].find(class_='descricao_item').get_text(strip=True)
            
            situacao_element = linhas[0].find_next('td', class_='descricao_item').find_next_sibling('td')
            situacao = situacao_element.get_text(strip=True) if situacao_element else "Situação não encontrada"

            descricao = re.sub(r'\(ID-\d+\)\s*', '', descricao)

            nome_produto = descricao.split(',')[0].strip()
            
            quantidade_texto = linhas[1].find(class_='descricao_item').get_text(strip=True)

            match = re.search(r'(\d+)\s*([\w\s]+)', quantidade_texto)
            if match:
                quantidade = match.group(1)
                unidade_medida = match.group(2).strip()
            else:
                quantidade = "Não encontrada"
                unidade_medida = "Não encontrada"

            produtos.append({
                'item': item_numero,
                'codigo': id,
                'descricao': descricao,
                'unidade': unidade_medida,
                'quantidade': quantidade,
                'situacao': situacao,
                'vencedor': None,
                'valor_unitario': None,
                'valor_global': None,
            })

            item_numero += 1

    lances = []

    tabelas_lances = soup.find_all('table', {'id': lambda x: x and x.startswith('tbl_lances')})

    for tabela in tabelas_lances:
        item_numero = tabela['id'].split('-')[-1]

        produto_correspondente = next((produto for produto in produtos if str(produto['item']) == item_numero), None)
        quantidade_item = produto_correspondente['quantidade'] if produto_correspondente else "Não encontrada"
        descricao_item = produto_correspondente['descricao'] if produto_correspondente else "Descrição não encontrada"

        linhas = tabela.find_all('tr', bgcolor=['#E6E6E6', '#FFFFFF'])

        primeiro_colocado = None
        outros_lances = []

        for i, linha in enumerate(linhas):
            colunas = linha.find_all('td')

            fornecedor = colunas[0].get_text(strip=True)
            fornecedor = re.sub(r'^\d+\s*-\s*', '', fornecedor)

            vlr_unit = colunas[4].get_text(strip=True)
            vlr_total = colunas[5].get_text(strip=True)

            vlr_negociado = colunas[7].get_text(strip=True) if len(colunas) > 7 else None

            try:
                if vlr_negociado and quantidade_item and quantidade_item != "Não encontrada":
                    
                    vlr_negociado_calculo = vlr_negociado.replace('.', '').replace(',', '.')
                    valor_unitario_negociado = float(vlr_negociado_calculo) / int(quantidade_item)
                    valor_unitario_negociado = f"{valor_unitario_negociado:.2f}".replace('.', ',')
                else:
                    valor_unitario_negociado = "Não disponível"
            except ValueError:
                valor_unitario_negociado = "Não disponível"

            if linha.find('img', src='images/trofeu.gif'):
                primeiro_colocado = {
                    'item': item_numero,
                    'empresa': fornecedor,
                    'colocacao': '1',
                    'descricao': descricao_item,
                    'quantidade':quantidade_item,
                    'valor_unitario': valor_unitario_negociado if valor_unitario_negociado else vlr_unit,
                    'valor_total': vlr_negociado if vlr_negociado else vlr_total,
                }

                if produto_correspondente:
                    produto_correspondente['vencedor'] = fornecedor
                    produto_correspondente['valor_unitario'] = valor_unitario_negociado if valor_unitario_negociado else vlr_unit
                    produto_correspondente['valor_global'] = vlr_negociado if vlr_negociado else vlr_total

            else:
                outros_lances.append({
                    'item': item_numero,
                    'empresa': fornecedor,
                    'colocacao': f'{len(outros_lances) + 2}',
                    'descricao': descricao_item,
                    'quantidade':quantidade_item,
                    'valor_unitario': vlr_unit,
                    'valor_total': vlr_total,
                })

        if primeiro_colocado:
            lances.append(primeiro_colocado)
        lances.extend(outros_lances[:2])

    idUuid = uuid.uuid4()

    with open(f'AtaJSON/{ano}/{nome_mes}/resultados_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as json_file:
        json.dump({'resultados': lances}, json_file, ensure_ascii=False, indent=4)

    with open(f'AtaJSON/{ano}/{nome_mes}/itens_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as json_file:
        json.dump({'itens': produtos}, json_file, ensure_ascii=False, indent=4)

except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro: {e}")
