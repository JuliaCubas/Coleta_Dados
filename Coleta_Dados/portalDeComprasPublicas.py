import requests
import json
from datetime import date
import uuid
import os

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

diretorio = f'AtaJSON/{ano}/{nome_mes}'
os.makedirs(diretorio, exist_ok=True)

codigo = 123456
idPCP = 332501
chave = os.getenv('PUBLIC_KEY')

url = f'https://apipcp.portaldecompraspublicas.com.br/publico/obterProcesso?publicKey={chave}&idLicitacao={idPCP}'

response = requests.get(url)

if response.status_code == 200:
    
    data = response.json()
    itens = []
    resultados = []
    todas_propostas = []
    empresas = []
    todos_lances = []

    for lote in data['lotes']:
        numero_lote = lote['NR_LOTE']
        vencedores_lote = {vencedor['IdItem']: vencedor for vencedor in lote.get('Vencedores', [])}

        for item in lote['itens']:
            vencedor = vencedores_lote.get(item['IdItem'], {})
            beneficio = item.get('EXCLUSIVOMPE')
            me_epp = 'S' if beneficio in ['true'] else 'N'
            propostas = item.get('Propostas', {})

            item_dados = {
                'codigo': codigo,
                'item': item['NR_ITEM'],
                'codigo': idPCP,
                'descricao': item['DS_ITEM'],
                'unidade': item['SG_UNIDADE_MEDIDA'],
                'quantidade': item['QT_ITENS'],
                'me_epp': me_epp,
                'situacao': data['situacao'],
                'vencedor': None,
                'CNPJ': vencedor.get('IdFornecedor', None),
                'valor_unitario': vencedor.get('ValorUnitario', None),
                'valor_total': vencedor.get('ValorTotal', None),
                'lote': numero_lote,

            }
            itens.append(item_dados)

            resultados_dados = {
                'codigo': codigo,
                'item': item['NR_ITEM'],
                'empresa': None,
                'CNPJ': vencedor.get('IdFornecedor', None),
                'colocacao': 1,
                'descricao': item['DS_ITEM'],
                'marca': None,
                'fabricante': None,
                'modelo': None,
                'quantidade': item['QT_ITENS'],
                'valor_unitario': vencedor.get('ValorUnitario', None),
                'valor_total': vencedor.get('ValorTotal', None),

            }
            resultados.append(resultados_dados)

            for proposta in propostas:
                proposta_dados = {
                    'codigo': codigo,
                    'item': item['NR_ITEM'],
                    'empresa': None,
                    'CNPJ': proposta.get('IdFornecedor', None),
                    'me_epp': me_epp,
                    'quantidade': proposta['Quantidade'],
                    'valor_unitario': proposta['ValorUnitario'],
                    'valor_total': proposta['ValorTotal'],
                    'descricao': proposta['Detalhamento'],
                    'marca': proposta['Marca'],
                    'fabricante': proposta['Fabricante'],
                    'modelo': proposta['Modelo']
                }
                todas_propostas.append(proposta_dados)

            for lances in item.get('Lances', []):

                situacao_inicial = lances.get('Valido')
                situacao = 'Valido' if beneficio in ['true'] else 'Cancelado'
                lance_dados = {
                    'codigo': codigo,
                    'item': item['NR_ITEM'],
                    'empresa': None,
                    'CNPJ': lances.get('IdFornecedor'),
                    'valor': lances.get('ValorTotal'),
                    'data':  lances.get('Data'),
                    'situacao': situacao
                }
                todos_lances.append(lance_dados)

            for participante in data.get('Participantes', []):
                representantes = participante.get('RepresentanteLegal', {})
                nome = representantes.get('Nome')

                empresa_dados = {
                    'CNPJ': participante.get('CNPJ'),
                    'empresa': participante.get('RazaoSocial'),
                    'me_epp': me_epp,
                    'contato': representantes.get('Nome'),
                    'telefone': participante.get('Telefone'),
                    'email': participante.get('Email')
                }
                empresas.append(empresa_dados)

    def preencher_nome_empresa(dados, empresas):
        for dado in dados:
            for empresa in empresas:
                if dado['CNPJ'] == empresa['CNPJ']:
                    dado['empresa'] = empresa['empresa']

    preencher_nome_empresa(resultados, empresas)        
    for item in itens:
        for empresa in empresas:
            if item['CNPJ'] == empresa['CNPJ']:
                item['vencedor'] = empresa['empresa']
    preencher_nome_empresa(todas_propostas, empresas)
    preencher_nome_empresa(todos_lances, empresas)

    for resultado in resultados:
        cnpj_resultado = resultado.get('CNPJ')
        item_resultado = resultado.get('item')
    
        for proposta in todas_propostas:
            cnpj_proposta = proposta.get('CNPJ')
            item_proposta = proposta.get('item')
        
            if cnpj_resultado == cnpj_proposta and item_resultado == item_proposta:
                resultado['modelo'] = proposta.get('modelo')
                resultado['marca'] = proposta.get('marca')
                resultado['fabricante'] = proposta.get('fabricante')
                break

    idUuid = uuid.uuid4()
    nomeArquivosItem = f'/itens_{idUuid}_{codigo}.json'
    nomeArquivosResultado = f'/resultados_{idUuid}_{codigo}.json'
    nomeArquivosLance = f'/lances_{idUuid}_{codigo}.json'
    nomeArquivosProposta = f'/propostas_{idUuid}_{codigo}.json'
    nomeArquivosEmpresa = f'/empresas_{idUuid}_{codigo}.json'    

    with open(f'{diretorio}{nomeArquivosItem}', 'w', encoding='utf-8') as json_file:
        json.dump({'itens': itens}, json_file, indent=4, ensure_ascii=False)

    with open(f'{diretorio}{nomeArquivosResultado}', 'w', encoding='utf-8') as json_file:
        json.dump({'resultados': resultados}, json_file, indent=4, ensure_ascii=False)

    with open(f'{diretorio}{nomeArquivosProposta}', 'w', encoding='utf-8') as json_file:
        json.dump({'propostas': todas_propostas}, json_file, indent=4, ensure_ascii=False)

    with open(f'{diretorio}{nomeArquivosEmpresa}', 'w', encoding='utf-8') as json_file:
        json.dump({'empresas': empresas}, json_file, indent=4, ensure_ascii=False)

    with open(f'{diretorio}{nomeArquivosLance}', 'w', encoding='utf-8') as json_file:
        json.dump({'lances': todos_lances}, json_file, indent=4, ensure_ascii=False)

