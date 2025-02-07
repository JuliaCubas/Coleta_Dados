from seleniumwire.utils import decode as sw_decode
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from seleniumwire import webdriver
from docx import Document
from datetime import date
from bs4 import BeautifulSoup
import requests
import pypandoc
import pathlib
import uuid
import random
import json
import time
import os
import re
import pathlib

def coletaRelatorio(Relatorios, palavra_chave):
    if not Relatorios:
        print("Nenhum relatório encontrado.")
        return None

    for Relatorio in Relatorios:
        NomeRelatorio = Relatorio.get('sDsTituloItem', 'Relatorio_Desconhecido').replace("/", "-")
        Link = Relatorio.get('sDsParametroCriptografado')

        if palavra_chave not in NomeRelatorio or not Link:
            continue

        print(f"Processando: {NomeRelatorio}")
        print(f"Link: {Link}")

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        try:
            driver.delete_all_cookies()
            driver.requests.clear()
            urlBase = f'https://www.peintegrado.pe.gov.br/{Link}'
            driver.get(urlBase)
            time.sleep(random.uniform(1, 3))

            exportPesquisa = 'Reserved.ReportViewerWebControl.axd?OpType=SessionKeepAlive'
            cookies = driver.get_cookies()
            session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            aiuser = session_cookies.get('ai_user')
            aisession = session_cookies.get('ai_session')
            asp_net = session_cookies.get('ASP.NET_SessionId')

            payloadDownload = None
            for request in driver.requests:
                if request.response and exportPesquisa in request.url:
                    payloadDownload = request.url
                    break
        except UnexpectedAlertPresentException:
            print("Erro: Alerta inesperado encontrado. Pulando relatório.")
            continue
        finally:
            driver.quit()

        if not payloadDownload:
            print(f"Não foi possível obter o link de download para {NomeRelatorio}.")
            continue

        IDControl_match = re.search(r'ControlID=(.*?)&', payloadDownload)
        IDControl = IDControl_match.group(1).strip() if IDControl_match else None

        urlAta = 'https://www.peintegrado.pe.gov.br/Reserved.ReportViewerWebControl.axd'

        headersAta = {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Referer": urlBase,
            "cookie": f'ASP.NET_SessionId={asp_net}; ai_user={aiuser}; ai_session={aisession}',
            "User-Agent": headers["User-Agent"],
        }

        payloadAta = {
            'Culture': 1046,
            'CultureOverrides': True,
            'UICulture': 1046,
            'UICultureOverrides': True,
            'ReportStack': 1,
            'ControlID': IDControl,
            'Mode': 'true',
            'OpType': 'Export',
            'FileName': 'AtaPublicaItemV2.pt-br',
            'ContentDisposition': 'OnlyHtmlInline',
            'Format': 'WORDOPENXML'
        }

        response = session.get(urlAta, params=payloadAta, headers=headersAta)

        return response
    
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

Arguments = [
    ('87654321','28654','18','1','6','3','3422.2025.AC-30.PE.0022.SAD.SEPDEC'),
    ('12345678','28575','18','1','24','153','3330.2024.CPL.CISAM.PE.0084.CISAM'),
]

for prodnum, Processo, Modulo, idApuracao, Situacao, Empresa, CodProcesso in Arguments:

    urlRelatorio = "https://www.peintegrado.pe.gov.br/Portal/WebService/Servicos.asmx/PesquisarProcessoDetalheRelatorio"
    urlDetalhesItens = "https://www.peintegrado.pe.gov.br/Portal/WebService/Servicos.asmx/PesquisarProcessoDetalheItemProduto"

    currentPath = pathlib.Path(__file__).parent.resolve()
    output_dir = os.path.abspath(f"{currentPath}/documentos")
    os.makedirs(output_dir, exist_ok=True)

    idUuid = uuid.uuid4()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    payloadRelatorio = {
        "dtoProcesso": {
            "nCdProcesso": Processo,
            "nCdModulo": Modulo,
            "nIdTipoApuracao": idApuracao,
            "nCdSituacao": Situacao,
            "nCdEmpresa": Empresa,
            "dtoIdioma": {}
        }
    }

    payloadDetalhesItens = {
        "dtoProcesso": {
            "nCdProcesso": Processo,
            "nCdModulo": Modulo,
            "sNrProcesso": CodProcesso,
            "nCdLote": 0,
            "nCdSituacao": Situacao,
            "dtoIdioma": {}
        }
    }

    itens = []
    lances = []
    resultados = []
    propostas = []
    empresas = []

    session = requests.Session()

    try:
        responseRelatorio = session.post(urlRelatorio, json=payloadRelatorio, headers=headers)
        responseDetalhesItens = session.post(urlDetalhesItens, json=payloadDetalhesItens, headers=headers)

        if responseRelatorio.status_code == 200 and responseDetalhesItens.status_code == 200:

            DataDetalhesItens = responseDetalhesItens.json()
            DetalhesItens = DataDetalhesItens.get('d', [])
            for DetalheItem in DetalhesItens:
                Quantidade = DetalheItem.get('dQtItem')
                valorVencedor = DetalheItem.get('dVlMelhorLanceMoedaVencedor')
                valorVencedorTotal = valorVencedor * Quantidade
                numeroItem = DetalheItem.get('nCdItemSequencial')
                descricaoItem = DetalheItem.get('sDsItem')
                unidadeFornecimento = DetalheItem.get('sSgUnidadeMedida')
                situacaoItem = DetalheItem.get('sStItem')

                itens.append({
                    'prodnum': prodnum,
                    'item': numeroItem,
                    'codigo': CodProcesso,
                    'descricao': descricaoItem,
                    'unidade': unidadeFornecimento,
                    'quantidade': Quantidade,
                    'me_epp': None,
                    'situacao': situacaoItem,
                    'vencedor': None,
                    'CNPJ': None,
                    'valor_unitario': valorVencedor,
                    'valor_total': valorVencedorTotal,
                    'lote': None
                })

            Data = responseRelatorio.json()
            Relatorios = Data.get('d', [])
            palavra_Ata = "Ata"

            responseAta =  coletaRelatorio(Relatorios, palavra_Ata)

            if responseAta.status_code == 200:
                docx_path = os.path.join(output_dir, f"Ata_{prodnum}.docx")
                with open(docx_path, 'wb') as file:
                    file.write(responseAta.content)
                html_path = os.path.join(output_dir, f"Ata_{prodnum}.html")
                #print (docx_path)

                try:
                    html_content = pypandoc.convert_file(docx_path, "html")
                    ataHtml = re.sub(r'\s+', ' ', html_content)

                    with open(html_path, 'w', encoding='utf-8') as handler:
                        handler.write(ataHtml)

                    htmlEmpresa_match = re.search(r'LICITANTES.*?E-mail.*?<\/tr>\s(.*?)tbody', ataHtml)

                    if htmlEmpresa_match:
                        htmlEmpresa = htmlEmpresa_match.group(1)
                        bloco_empresas = re.findall(r'<tr>(.*?)<\/tr>', htmlEmpresa)
                        for bloco_empresa in bloco_empresas:      
                            soupempresa = BeautifulSoup(bloco_empresa, 'html.parser')
                            try:
                                row1 = soupempresa.find_all('td')
                                
                                cnpj = row1[0].text.strip()
                                nomeempresa = row1[1].text.strip()
                                email = row1[2].text.strip()
                                meepp = row1[3].text.strip()
                                meepp_sigla = 'S' if meepp in ['Sim'] else 'N'

                                empresas.append({
                                        'CNPJ': cnpj,
                                        'empresa': nomeempresa,
                                        'me_epp': meepp_sigla,
                                        'contato': None,
                                        'fone': None,
                                        'email': email
                                })

                            except Exception as e:
                                print(f"Erro ao processar tabela de licitantes: {e}")
                    else:
                        print("Tabela de licitantes não encontrada no conteúdo HTML.")
                    
                    htmlLances_match = re.search(r'ETAPA\sDE\sLANCES.*?text.*?<\/tr>(.*?)QUADRO\sDE\sRESULTADOS', ataHtml)
                    
                    if htmlLances_match:

                        htmlLance = htmlLances_match.group(1)
                        bloco_lances = re.findall(r'(Item.*?)Valor total do lance.*?Situação</td> </tr>(.*?)</td> <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> </tr> <tr>', htmlLance, re.DOTALL)

                        if bloco_lances:
                            for bloco_lance in bloco_lances:
                                infoItem = bloco_lance[0]
                                numeroLance = re.findall(r'Item\s(\d+)\s-', infoItem)

                                infoLance = bloco_lance[1]
                                bloco_lances = re.findall(r'<tr>(.*?)<\/tr>', infoLance)
                                for bloco_lance in bloco_lances:
                                    souplance= BeautifulSoup(bloco_lance, 'html.parser')
                                    try:
                                        row2 = souplance.find_all('td')
                                        
                                        data = row2[0].text.strip()
                                        razaoSocial = row2[1].text.strip()
                                        valor = row2[4].text.strip()
                                        situacaolance = row2[6].text.strip()

                                        lances.append({
                                            "prodnum": prodnum,
                                            "item": numeroLance[0],
                                            "empresa": razaoSocial,
                                            "CNPJ": cnpj,
                                            "valor": valor,
                                            "data": data,
                                            "situacao": situacaolance
                                        })

                                    except Exception as e:
                                        print(f"Erro ao processar tabela de licitantes: {e}")

                except Exception as e:
                    print(f"Erro ao converter DOCX para HTML da Ata: {e}")
            else:
                print(f"Erro ao baixar relatório Ata: {responseAta.status_code}")
                continue

            palavra_homologacao = "homologação"
            responsehomologacao =  coletaRelatorio(Relatorios, palavra_homologacao)

            if responsehomologacao.status_code == 200:
                docx_homologacao = os.path.join(output_dir, f"Homologação_{prodnum}.docx")
                with open(docx_homologacao, 'wb') as file:
                    file.write(responsehomologacao.content)
                html_homologacao = os.path.join(output_dir, f"Homologação_{prodnum}.html")

                try:
                    html_Homologado = pypandoc.convert_file(docx_homologacao, "html")
                    homologacaoHtml = re.sub(r'\s+', ' ', html_Homologado)

                    htmlresultados_match = re.search(r'.*HOMOLOGO.*?<table(.*?)</tbody>', homologacaoHtml)

                    if htmlresultados_match:
                        htmlResultado = htmlresultados_match.group(1)

                        bloco_resultados = re.findall(r'<tr>(.*?)Índice\sde\seconomia\sreferência', htmlResultado, re.DOTALL)

                        if bloco_resultados:
                            for bloco_resultado in bloco_resultados:
                                numeroResultado_match = re.search(r'Item\s(\d+)\s-', bloco_resultado)
                                numeroResultado = numeroResultado_match.group(1).strip()

                                quantidade_match = re.search(r'Quantidade</td>.*?>(.*?)<', bloco_resultado)
                                quantidadefloat = quantidade_match.group(1).strip() if quantidade_match else 0
                                quantidadeResult = float(str(quantidadefloat).replace(' ', '').replace('.', '').replace(',', '.'))
                                
                                vencedor_match = re.search(r'.*>(.*?)\svencedora', bloco_resultado)
                                vencedor = vencedor_match.group(1).strip() if vencedor_match else None

                                descricaoResult_match = re.search(r'Item.*?-\s(.*?)\s\(Encerrado\)', bloco_resultado)
                                descricaoResult = descricaoResult_match.group(1).strip() if descricaoResult_match else None

                                unidadeMedida_match = re.search(r'Unidade de medida</td>.*?>(.*?)<', bloco_resultado)
                                unidadeMedida = unidadeMedida_match.group(1).strip() if unidadeMedida_match else None

                                valorUnitario_match = re.search(r'Valor\sfinal\sunitário.*?R\$\s(.*?)<', bloco_resultado)
                                valorUnitario_group = valorUnitario_match.group(1).strip() if valorUnitario_match else 0
                                valorUnitario = float(str(valorUnitario_group).replace(' ', '').replace('.', '').replace(',', '.'))

                                valorTotal_match = re.search(r'Valor\sfinal\stotal.*?R\$\s(.*?)<', bloco_resultado)
                                valorTotal_group = valorTotal_match.group(1).strip() if valorTotal_match else 0
                                valorTotal = float(str(valorTotal_group).replace(' ', '').replace('.', '').replace(',', '.'))   

                                resultados.append({
                                    'prodnum': prodnum, 
                                    'item': numeroResultado, 
                                    'empresa': vencedor,
                                    'CNPJ': None,
                                    'colocacao': 1,
                                    'descricao': descricaoResult, 
                                    'marca': None, 
                                    'fabricante': None,
                                    'modelo': None,
                                    'quantidade': quantidadeResult,
                                    'valor_unitario': valorUnitario,
                                    'valor_total': valorTotal,
                                    'EAN': None
                                })

                except Exception as e:
                    print(f"Erro ao converter DOCX para HTML da Homologação: {e}")
            else:
                print(f"Erro ao baixar relatório Homologação: {responsehomologacao.status_code}")
                continue

            palavra_propostas = "Propostas"
            responseproposta =  coletaRelatorio(Relatorios, palavra_propostas)

            if responseproposta.status_code == 200:
                docx_proposta = os.path.join(output_dir, f"Propostas_{prodnum}.docx")
                with open(docx_proposta, 'wb') as file:
                    file.write(responseproposta.content)
                html_proposta = os.path.join(output_dir, f"Propostas_{prodnum}.html")
                try:
                    html_Proposta = pypandoc.convert_file(docx_proposta, "html")
                    propostaHtml = re.sub(r'\s+', ' ', html_Proposta)

                    htmlpropostas_match = re.search(r'seguintes\spreços:.*?</colgroup>\s<tbody>(.*?)<\/tbody>', propostaHtml, re.DOTALL)
                    if htmlpropostas_match:

                        htmlproposta = htmlpropostas_match.group(1)
                        bloco_propostasdetalhadas = re.findall(r'(Item.*?)\s<tr>\s<td\sstyle=\"text-align: left;\"></td>', htmlproposta, re.DOTALL)
                        if bloco_propostasdetalhadas:
                            for bloco_propostadetalhada in bloco_propostasdetalhadas:
                                bloco_propostas = re.findall(r'<tr>\s(<td\sstyle=\"text-align: center;\">.*?)</td>\s</tr>', htmlproposta, re.DOTALL)
                                
                                numeroPropostas_match = re.search(r'Item\s-\s(\d+)', bloco_propostadetalhada)
                                numeroPropostas = numeroPropostas_match.group(1).strip()

                                descricaoPropostas_match = re.search(r'Item\s-\s\d+\s(.*?)<', bloco_propostadetalhada)
                                descricaoPropostas = descricaoPropostas_match.group(1).strip()
                                for bloco_proposta in bloco_propostas:
                                    soupproposta = BeautifulSoup(bloco_proposta, 'html.parser')
                                    
                                    row3 = soupproposta.find_all('td')
                                    
                                    empresaproposta = row3[1].text.strip()
                                    cnpjproposta_match = re.search(r'(.*?)\s-', empresaproposta)
                                    cnpjproposta = cnpjproposta_match.group(1).strip()

                                    empresaproposta_match = re.search(r'\s-\s(.*)', empresaproposta)
                                    empresaproposta = empresaproposta_match.group(1).strip()

                                    marca_modelo_fabri = row3[2].text.strip()
                                    partes = marca_modelo_fabri.split("/")

                                    marca = partes[0].strip()
                                    modelo = partes[1].strip()
                                    fabricante = partes[2].strip()

                                    quantidadeproposta_match = row3[3].text.strip()
                                    quantidadeproposta = float(str(quantidadeproposta_match).replace(' ', '').replace('.', '').replace(',', '.'))
                                    valoruniproposta_match = row3[7].text.strip()
                                    valoruniproposta = float(str(valoruniproposta_match).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.'))
                                    valortotproposta_match = row3[8].text.strip()
                                    valortotproposta = float(str(valortotproposta_match).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.'))

                                    propostas.append({
                                        'prodnum': prodnum,
                                        'item': numeroPropostas,
                                        'empresa': empresaproposta,
                                        'CNPJ': cnpjproposta,
                                        'me_epp': None,
                                        'quantidade': quantidadeproposta,
                                        'valor_unitario': valoruniproposta,
                                        'valor_total': valortotproposta,
                                        'descricao': descricaoPropostas,
                                        'marca': marca,
                                        'fabricante': modelo,
                                        'modelo': fabricante,
                                    })
                
                except Exception as e:
                    print(f"Erro ao converter DOCX para HTML da Propostas: {e}")
            else:
                print(f"Erro ao baixar relatório Propostas: {responseproposta.status_code}")
                continue


        for resultado in resultados:
            nome_empresa_resultado = resultado.get("empresa")
            for empresa in empresas:
                nome_empresa_json = empresa.get("empresa")
                if nome_empresa_resultado and nome_empresa_json and nome_empresa_resultado.lower() == nome_empresa_json.lower():
                    resultado["CNPJ"] = empresa["CNPJ"]
                    break 
            for proposta in propostas:
                if resultado["item"] == proposta["item"]:
                    resultado["marca"] = proposta.get("marca", None)
                    resultado["modelo"] = proposta.get("modelo", None)
                    resultado["fabricante"] = proposta.get("fabricante", None)
                    break 

        resultados_dict = {str(r["item"]): {"empresa": r["empresa"], "CNPJ": r["CNPJ"]} for r in resultados}
        empresas_dict = {e["empresa"].lower(): e["me_epp"] for e in empresas}

        for item in itens:
            item_id = str(item["item"])

            if item_id in resultados_dict:
                item["vencedor"] = resultados_dict[item_id]["empresa"]
                item["CNPJ"] = resultados_dict[item_id]["CNPJ"]

            if item.get("vencedor") and item["vencedor"].lower() in empresas_dict:
                item["me_epp"] = empresas_dict[item["vencedor"].lower()]

        for prop in propostas:
            if prop.get("empresa") and prop["empresa"].lower() in empresas_dict:
                prop["me_epp"] = empresas_dict[prop["empresa"].lower()]

        idUuid = uuid.uuid4()

        nomeArquivosItem = f'/itens_{idUuid}.json'
        nomeArquivosResultado = f'/resultados_{idUuid}.json'
        nomeArquivosProposta = f'/propostas_{idUuid}.json'
        nomeArquivosEmpresa = f'/empresas_{idUuid}.json'
        nomeArquivosLance = f'/lances_{idUuid}.json'

        with open(f'{diretorio}{nomeArquivosItem}', "w", encoding="utf-8") as f:
            json.dump({'itens': itens}, f, indent=4, ensure_ascii=False)

        with open(f'{diretorio}{nomeArquivosProposta}', "w", encoding="utf-8") as f:
            json.dump({'propostas': propostas}, f, indent=4, ensure_ascii=False)

        with open(f'{diretorio}{nomeArquivosLance}', "w", encoding="utf-8") as f:
            json.dump({'lances': lances}, f, indent=4, ensure_ascii=False)

        with open(f'{diretorio}{nomeArquivosEmpresa}', "w", encoding="utf-8") as f:
            json.dump({'empresas': empresas}, f, indent=4, ensure_ascii=False)

        with open(f'{diretorio}/{nomeArquivosResultado}', "w", encoding="utf-8") as f:
            json.dump({'resultados': resultados}, f, indent=4, ensure_ascii=False)

    finally:
        session.close()
        continue