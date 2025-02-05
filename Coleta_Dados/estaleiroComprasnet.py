from seleniumwire.utils import decode as sw_decode
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import date
import requests
import random
import time
import json
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

def coleta_dados(url, pesquisa):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

    dados = None

    with uc.Chrome(options=chrome_options, driver_executable_path="chromedriver.exe") as driver:
        driver.get(url)
        time.sleep(random.uniform(10, 15))
        driver.maximize_window()
        time.sleep(random.uniform(1, 5))

        buttons = driver.find_elements(By.XPATH, './/app-cabecalho-item//button[starts-with(@class, "p-element br-button ng-tns-c")]')
        if buttons:
            button = buttons[0]
            driver.execute_script("arguments[0].scrollIntoView();", button)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(random.uniform(1, 5))

            for request in driver.requests:
                if request.response and pesquisa in request.url:
                    dados_decoded = sw_decode(
                        request.response.body, 
                        request.response.headers.get('Content-Encoding', 'identity')
                    ).decode("utf8")
                    dados = json.loads(dados_decoded)
                    time.sleep(random.uniform(1, 5))
                    break

    driver.quit()

    return dados

arguments = [
    ('1566024','09011305900252024'),
]

for codigo, idCompra in arguments:

    url = f'https://dadosabertos.compras.gov.br/modulo-contratacoes/2.1_consultarItensContratacoes_PNCP_14133_Id?idCompra={idCompra}'

    response = requests.get(url)

    itens = []
    proposta = []
    resultado = []
    empresa = []

    if response.status_code == 200:
        itensJson = response.json()
        totalItens = itensJson.get('totalRegistros', 0)
        print(f"Total de Itens: {totalItens}")

        for item_num in range(1, totalItens + 1):

            urlBase = f'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras/acompanhamento-compra/item/{item_num}?compra={idCompra}'
            pesquisaProposta = "propostas?captcha="
            dadosPropostas = coleta_dados(urlBase, pesquisaProposta)

            if dadosPropostas:
                numeroItemProposta = dadosPropostas.get('numero')
                propostasItens = dadosPropostas.get('propostasItem', [])
                for propostaItem in propostasItens:
                    quantidadeOfertada = propostaItem.get('quantidadeOfertada', None)
                    descricaoProposta = dadosPropostas.get('descricao', None)
                    marcaFabricante = propostaItem.get('marcaFabricante', None)
                    modeloVersao = propostaItem.get('modeloVersao', None)
                    colocacao = propostaItem.get('classificacao', None)

                    valores = propostaItem.get('valores', {})
                    valoresPropostas = valores.get('valorPropostaInicial', {}).get('valorCalculado', {})
                    valorUnitarioProposta = valoresPropostas.get('valorUnitario', None)
                    valorGlobalProposta = valoresPropostas.get('valorTotal', None)

                    valoresResultados = valores.get('valorPropostaInicialOuLances', {}).get('valorCalculado', {})
                    valorUnitarioResultado = valoresResultados.get('valorUnitario', None)
                    valorGlobalResultado = valoresResultados.get('valorTotal', None)

                    participantes = propostaItem.get('participante', {})
                    cnpj = participantes.get('identificacao', None)
                    razaoSocial = participantes.get('nome', None)
                    declaranteMeEpp = propostaItem.get('declaracaoMeEpp', False)
                    MeOuEpp = 'S' if declaranteMeEpp else 'N'

                    estruturaPropostas = {
                        'codigo': codigo,
                        'item': numeroItemProposta,
                        'empresa': razaoSocial,
                        'CNPJ': cnpj,
                        'me_epp': MeOuEpp,
                        'quantidade': quantidadeOfertada,
                        'valor_unitario': valorUnitarioProposta,
                        'valor_total': valorGlobalProposta,
                        'descricao': descricaoProposta,
                        'marca': marcaFabricante,
                        'fabricante': marcaFabricante,
                        'modelo': modeloVersao
                    }
                    proposta.append(estruturaPropostas)

                    estruturaResultados = {
                        'codigo':  codigo,
                        'item': numeroItemProposta,
                        'empresa': razaoSocial,
                        'CNPJ': cnpj,
                        'colocacao': colocacao,
                        'descricao': descricaoProposta,
                        'marca': marcaFabricante,
                        'fabricante': marcaFabricante,
                        'modelo': modeloVersao,
                        'quantidade': quantidadeOfertada,
                        'valor_unitario': valorUnitarioResultado,
                        'valor_total': valorGlobalResultado,

                    }
                    resultado.append(estruturaResultados)

                    estruturaEmpresas = {
                        'CNPJ': cnpj,
                        'empresa': razaoSocial,
                        'me_epp': MeOuEpp,
                    }
                    empresa.append(estruturaEmpresas)

            pesquisaItens = "detalhamento?captcha="
            dadosItens = coleta_dados(urlBase, pesquisaItens)

            if dadosItens:
                numeroItem = dadosItens.get('numero')
                descricaoDetalhada = dadosItens.get('descricaoDetalhada', None)
                descricao = dadosItens.get('descricao', None)
                descricaoCompleta = f"{descricao} - {descricaoDetalhada}"
                unidadeFornecimento = dadosItens.get('unidadeFornecimento', None)
                quantidade = dadosItens.get('quantidadeSolicitada', None)
                codigoSituacao = dadosItens.get('situacao', None)
                situacaoDicionario = {
                    '1': 'HOMOLOGADO' ,
                    '2': 'CANCELADO',
                    '3': 'ANULADO',
                    '4': 'REVOGADO',
                    '5': 'SUSPENSO',
                    '6': 'DESERTO',
                    '7': 'FRACASSADO_NA_ANALISE',
                    '8': 'FRACASSADO_NO_JULGAMENTO',
                    '9': 'FRACASSADO_NA_DISPUTA'
                }
                situacaoItem = situacaoDicionario.get(codigoSituacao)
                meeppResultado = dadosItens.get('participacaoExclusivaMeEppOuEquiparadas', None)
                meepp = 'S' if meeppResultado in ['true'] else 'N'

                estruturaItens = {
                    ' codigo':  codigo,
                    'item': numeroItem,
                    'codigo': idCompra,
                    'descricao': descricaoCompleta,
                    'unidade': unidadeFornecimento,
                    'quantidade': quantidade,
                    'me_epp': meepp,
                    'situacao': situacaoItem,
                    'vencedor': None,
                    'CNPJ': None,
                    'valor_unitario': None,
                    'valor_total': None,
                }

                for res in resultado:
                    if (
                        str(res['colocacao']) == '1' and
                        str(res['item']) == str(numeroItem) and
                        str(res[' codigo']) == str( codigo)
                    ):

                        estruturaItens['vencedor'] = res['empresa']
                        estruturaItens['CNPJ'] = res['CNPJ']
                        estruturaItens['valor_unitario'] = res['valor_unitario']
                        estruturaItens['valor_total'] = res['valor_total']
                        break

                itens.append(estruturaItens)

            else:
                print(f"Nenhum dado encontrado para item {item_num}.")

        idUuid = uuid.uuid4()
        nomeArquivosItem = f'/itens_{idUuid}_{idCompra}_{ codigo}.json'
        nomeArquivosResultado = f'/resultados_{idUuid}_{idCompra}_{ codigo}.json'
        nomeArquivosProposta = f'/propostas_{idUuid}_{idCompra}_{ codigo}.json'
        nomeArquivosEmpresa = f'/empresas_{idUuid}_{idCompra}_{ codigo}.json'   

        with open(f"{diretorio}{nomeArquivosProposta}", "w", encoding="utf-8") as f:
            json.dump({"propostas": proposta}, f, indent=4, ensure_ascii=False)
        with open(f"{diretorio}{nomeArquivosEmpresa}", "w", encoding="utf-8") as f:
            json.dump({"empresas": empresa}, f, indent=4, ensure_ascii=False)
        with open(f"{diretorio}{nomeArquivosResultado}", "w", encoding="utf-8") as f:
            json.dump({"resultados": resultado}, f, indent=4, ensure_ascii=False)
        with open(f"{diretorio}{nomeArquivosItem}", "w", encoding="utf-8") as f:
            json.dump({"itens": itens}, f, indent=4, ensure_ascii=False)

