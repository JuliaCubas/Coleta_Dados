import requests
import json
import uuid
import os
from datetime import date

prodnum = '12345678'
id = '53011'
edital_anterior = '1/2024'
edital = edital_anterior.replace('/','_')

url = f'https://wstransparencia.vitoria.es.gov.br/api/Licitacao/{id}/LoteItensParticipantesNovo'

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

response = requests.get(url)

item_numero = 1

if response.status_code == 200:
    data = response.json()

    produtos = []
    propostas = []
    empresas = []

    for lote in data:
        numero_lote = lote["nome"]

        for item in lote["lista"]:
            vencedor = "null"
            valor_total_vencedor = "null"
            situacao_vencedor = "null"
            valor_inicial = "null"

            quantidade_item = item.get('quantidade', 1)

            if lote["participantes"]:
                primeiro_participante = lote["participantes"][0]
                vencedor = primeiro_participante.get('nome', 'null').strip()
                valor_total_vencedor = primeiro_participante.get('valorTotal', 0)

                if quantidade_item > 0 and valor_total_vencedor > 0:
                    valor_inicial = valor_total_vencedor / quantidade_item

                situacao_vencedor = primeiro_participante.get('situacao', 'null')

            produtos.append({
                'prodnum': prodnum,
                'item': item_numero,
                'codigo': id,
                'descricao': item.get('nome', 'null').strip(),
                'unidade': item.get('unidade', 'null').strip(),
                'quantidade': quantidade_item,
                'situacao': situacao_vencedor,
                'vencedor': vencedor,
                'valor_unitario': valor_inicial,
                'valor_total': valor_total_vencedor,
                'lote': numero_lote
            })

            for idx, lance in enumerate(lote["participantes"]):
                if idx < 3:
                    propostas.append({
                        'prodnum': prodnum,
                        'item': item_numero,
                        'empresa': lance.get('nome', 'null').strip(),
                        'colocacao': idx + 1,
                        'descricao': item.get('nome', 'null').strip(),
                        'quantidade': quantidade_item,
                        'valor_unitario': valor_inicial,
                        'valor_total': lance.get('valorTotal', 'null'),
                    })

                    empresas.append({
                        'cnpj': lance.get('cpfCnpj', 'null'),
                        'empresa': lance.get('nome', 'null').strip(),
                    })

            item_numero += 1

    final_json_itens = {'itens': produtos}
    final_json_lances = {'lances': propostas}
    final_json_empresas = {'empresas': empresas}

    idUuid = uuid.uuid4()

    with open(f'AtaJSON/{ano}/{nome_mes}/itens_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as json_file:
        json.dump(final_json_itens, json_file, indent=4, ensure_ascii=False)

    with open(f'AtaJSON/{ano}/{nome_mes}/resultados_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as json_file:
        json.dump(final_json_lances, json_file, indent=4, ensure_ascii=False)

    with open(f'AtaJSON/{ano}/{nome_mes}/empresas_{idUuid}_{id}_{edital}.json', 'w', encoding='utf-8') as json_file:
        json.dump(final_json_empresas, json_file, indent=4, ensure_ascii=False)

    print("JSONs formatados e salvos com sucesso.")
else:
    print(f"Erro ao acessar a API. Status code: {response.status_code}")
