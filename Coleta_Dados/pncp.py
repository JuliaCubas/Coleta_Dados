import os
import requests
import json
import uuid
from datetime import date

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

diretorio = f'AtaJSON/{ano}/{nome_mes}/'
os.makedirs(diretorio, exist_ok=True)

prodnum = '1234567'
sequencial= '917'
cnpj_orgao = '00394429000100'
ano_sequencial_pncp = '2024'
id = '12345'

url = f'https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj_orgao}/compras/{ano_sequencial_pncp}/{sequencial}/itens/?pagina=1&tamanhoPagina=10000'

response = requests.get(url)

if response.status_code == 200:
    data = response.json() 
    
    produtos = []
    propostas = []

    for itens in data:
        item_numero = itens.get('numeroItem', None)
        descricao = itens.get('descricao', None)
        unidade = itens.get('unidadeMedida', None)
        quantidade = itens.get('quantidade', None)
        situacao = itens.get('situacaoCompraItemNome', None)
        tem_resultado = itens.get('temResultado', False)
        
        me_epp = None
        cnpj_empresa = None
        
        if tem_resultado:
            url_lances = f'https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj_orgao}/compras/{ano_sequencial_pncp}/{sequencial}/itens/{item_numero}/resultados?pagina=1&tamanhoPagina=10000'
            response_lances = requests.get(url_lances)

            vencedor = None
            valor_unitario_vencedor = None
            valor_total_vencedor = None

            if response_lances.status_code == 200:
                data_lances = response_lances.json()

                if data_lances:
                    lance_vencedor = min(data_lances, key=lambda x: x.get('valorTotalHomologado', float('inf')))
                    vencedor = lance_vencedor.get('nomeRazaoSocialFornecedor', None)
                    valor_unitario_vencedor = lance_vencedor.get('valorUnitarioHomologado', None)
                    valor_total_vencedor = lance_vencedor.get('valorTotalHomologado', None)

                for lances in data_lances:
                    empresa = lances.get('nomeRazaoSocialFornecedor', None)
                    cnpj_empresa = lances.get('niFornecedor', None)
                    quantidade_lance = lances.get('quantidadeHomologada', None)
                    numero_item = lances.get('numeroItem', None)
                    valor_unitario = lances.get('valorUnitarioHomologado', None)
                    valor_total = lances.get('valorTotalHomologado', None)
                    beneficio = lances.get('aplicacaoBeneficioMeEpp')
                    me_epp = 'S' if beneficio in ['true'] else 'N'

                    propostas.append({
                        'prodnum': prodnum,
                        'item': numero_item,
                        'empresa': empresa,
                        'CNPJ': cnpj_empresa,
                        'colocacao': 1,
                        'descricao': descricao,
                        'quantidade': quantidade_lance,
                        'valor_unitario': valor_unitario,
                        'valor_total': valor_total,
                    })
            else:
                print(f"Erro ao acessar a API lances. Status code: {response_lances.status_code} - PRODNUM: {prodnum} - {url_lances}")

        produtos.append({
            'prodnum': prodnum,
            'item': item_numero,
            'codigo': sequencial,
            'descricao': descricao,
            'unidade': unidade,
            'quantidade': quantidade,
            'me_epp': me_epp,
            'situacao': situacao,
            'vencedor': vencedor if tem_resultado else None,
            'CNPJ': cnpj_empresa if tem_resultado else None,
            'valor_unitario': valor_unitario_vencedor if tem_resultado else None,
            'valor_total': valor_total_vencedor if tem_resultado else None,
        })

    idUuid = uuid.uuid4()
    
    nomeArquivoItens = f'itens_{idUuid}_{ano_sequencial_pncp}_{sequencial}_{cnpj_orgao}.json'
    nomeArquivoResultados = f'resultados_{idUuid}_{ano_sequencial_pncp}_{sequencial}_{cnpj_orgao}.json'
    
    with open(f'{diretorio}{nomeArquivoItens}', 'w', encoding='utf-8') as json_file:
        json.dump({'itens': produtos}, json_file, indent=4, ensure_ascii=False)    

    with open(f'{diretorio}{nomeArquivoResultados}', 'w', encoding='utf-8') as json_file:
        json.dump({'resultados': propostas}, json_file, indent=4, ensure_ascii=False)
        