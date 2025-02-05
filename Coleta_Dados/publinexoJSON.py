from bs4 import BeautifulSoup
import re
import json

def extrair_cnpj(text):
    match = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', text)
    return match.group(0) if match else None

with open('AtaHTML/22532_PRE_835a0400-8997-4310-b8c1-411414f15e9e.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

prodnum = 5638773
itens = []
propostas = []
empresas = []
lances = []
resultados = []

tables = soup.find_all('table')

for table in tables:
    rows = table.find_all('tr')

    for row in rows:
        cells = row.find_all('td')

        if len(cells) > 1 and 'Código:' in row.text and 'Quantidade:' in row.text:
            codigo_match = re.search(r'Código:\s*(\d+)', row.text)
            quantidade_match = re.search(r'Quantidade:\s*(\d+)', row.text)
            descricao_match = re.search(r'(.*)\s*Código:', row.text) 

            codigo = codigo_match.group(1) if codigo_match else 'N/A'
            quantidade = quantidade_match.group(1) if quantidade_match else 'N/A'
            numero_item = cells[0].text.strip()
            produto = descricao_match.group(1) if descricao_match else 'null'
            
            item_info = {
                'prodnum': prodnum,
                'item': numero_item,
                'codigo': codigo,
                'descricao': produto,
                'quantidade': quantidade,
                'vencedor': 'null',
                'valor_unitario': 'null',

            }
            itens.append(item_info)

        if len(cells) == 5:
            fornecedor_text = cells[0].text.strip()
            preco = cells[1].text.strip()
            valor_total = cells[2].text.strip()
            marca = cells[3].text.strip()

            proposta_info = {
                'prodnum': prodnum,
                'item': numero_item,
                'empresa': fornecedor_text.split(' - ')[0],
                'me_epp': 'null',
                'quantidade': quantidade,
                'valor_unitario': preco,
                'valor_total': valor_total,
                'descricao': produto,
                'marca': marca,
            }
            propostas.append(proposta_info)

            cnpj = extrair_cnpj(fornecedor_text)
            fornecedor_empresa = fornecedor_text.split(' - ')[0]
            empresa_info = {
                'cnpj': cnpj,
                'empresa': fornecedor_empresa,
            }
            empresas.append(empresa_info)

        if 'Lances / Ocorrências' in row.text:
            for lance_row in rows[rows.index(row) + 1:]:
                lance_cells = lance_row.find_all('td')
                if len(lance_cells) == 3:
                    fornecedor = lance_cells[0].text.strip()
                    hora = lance_cells[1].text.strip()
                    valor_lance = lance_cells[2].text.strip()

                    lances.append({
                        'prodnum': prodnum,
                        'item': numero_item,
                        'empresa': fornecedor,
                        'valor': valor_lance,
                        'data': hora,
                    })

        if 'Fornecedores vencedores da disputa:' in row.text:
            for resultado_row in rows[rows.index(row) + 1:]:
                resultado_cells = resultado_row.find_all('td')
                if len(resultado_cells) == 8:
                    numero_resultado = resultado_cells[0].text.strip()
                    empresa_resultado = resultado_cells[4].text.strip()
                    descricao_resultado = resultado_cells[2].text.strip()
                    marca_resultado = resultado_cells[7].text.strip()
                    quantidade_resultado = resultado_cells[3].text.strip()
                    valor_unitario_resultado = resultado_cells[5].text.strip()
                    quantidade_resultado_limpeza = float(quantidade_resultado.replace('.', '').replace(',', '.'))

                    for item in itens:
                        if item['item'] == numero_resultado:
                            item['vencedor'] = empresa_resultado
                            item['valor_unitario'] = valor_unitario_resultado

                    resultado_info = {
                        'prodnum': prodnum,
                        'item': numero_resultado,
                        'empresa': empresa_resultado,
                        'colocacao': 1,
                        'descricao': descricao_resultado,
                        'marca': marca_resultado,
                        'fabricante': 'null',
                        'modelo': 'null',
                        'quantidade': quantidade_resultado_limpeza,
                        'Valor_unitario': valor_unitario_resultado,
                    }
                    resultados.append(resultado_info)
    

with open(f'AtaJSON/Itens_{prodnum}.json', 'w', encoding='utf-8') as json_file:
    json.dump({'Itens': itens}, json_file, indent=4, ensure_ascii=False)

with open(f'AtaJSON/Propostas_{prodnum}.json', 'w', encoding='utf-8') as json_file:
    json.dump({'Propostas': propostas}, json_file, indent=4, ensure_ascii=False)

with open(f'AtaJSON/Empresas_{prodnum}.json', 'w', encoding='utf-8') as json_file:
    json.dump({'Empresas': empresas}, json_file, indent=4, ensure_ascii=False)

with open(f'AtaJSON/Lances_{prodnum}.json', 'w', encoding='utf-8') as json_file:
    json.dump({'Lances': lances}, json_file, indent=4, ensure_ascii=False)

with open(f'AtaJSON/Resultados_{prodnum}.json', 'w', encoding='utf-8') as json_file:
    json.dump(resultados, json_file, indent=4, ensure_ascii=False)

print("Dados extraídos e salvos com sucesso!")