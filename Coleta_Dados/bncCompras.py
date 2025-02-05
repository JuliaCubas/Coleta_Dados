
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import uuid
import random
import os
import requests
from datetime import date
import json
import re
from bs4 import BeautifulSoup
import time

def formatar_lote_item(lote, item):
    return f"{lote:04}{item}"
def formatar_lote(lote):
    return f"{lote:05}"

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

while True:

    codigo = 123456
    link = "https://bnccompras.com/Process/ProcessView?param1=%5Bgkz%5DnkIugOFkFpcNNvxye4f376M6a%2FPCzi%2F1oph%2FWVfQVWJyd3es_8DsZTWX4YSTBozNtGohXFeAp_rBCSu9eX%2FBZtOVGfjUzNKc76DfDNSUgFg%3D"

    url = f'{link}'

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    try:
        with uc.Chrome(options=chrome_options, driver_executable_path="chromedriver.exe") as driver:
            driver.get(url)
            time.sleep(random.uniform(3,5))
            driver.maximize_window()

        driver.execute_script("ExecuteCaptcha('processView').then(function (token) { console.log('Token:'+token); });")

        time.sleep(5)

        for entry in driver.get_log('browser'):
            if 'Token:' in entry['message']:
                mensagemToken = entry['message']

        botao_lotes = driver.find_element(By.XPATH, "//button[contains(text(), 'Lotes')]")
        botao_lotes.click()

        time.sleep(5)
    except:

        driver.quit()
        time.sleep(5)

        with uc.Chrome(options=chrome_options, driver_executable_path="chromedriver.exe") as driver:
            driver.get(url)
            time.sleep(random.uniform(3,5))
            driver.maximize_window()

        driver.execute_script("ExecuteCaptcha('processView').then(function (token) { console.log('Token:'+token); });")

        time.sleep(5)

        for entry in driver.get_log('browser'):
            if 'Token:' in entry['message']:
                mensagemToken = entry['message']

        botao_lotes = driver.find_element(By.XPATH, "//button[contains(text(), 'Lotes')]")
        botao_lotes.click()

        time.sleep(5) 

    pagina2 = driver.page_source
    html_Inicial = re.sub(r'\s+', ' ', pagina2)

    all_empresas, all_resultados, all_itens, all_lances = [], [], [], []

    regexBatchItemsInfo = r"GetBatchItemsInfo\(\'(.*?)\'\)"
    itensInfo = re.findall(regexBatchItemsInfo, pagina2)
    for iteminfo in itensInfo:
        iteminfo = iteminfo.replace("'", '')
        partsInfo = iteminfo.split(',')

        if len(partsInfo) < 3:
            print(f"Formato inesperado em iteminfo: {iteminfo}")
            continue

        param1 = partsInfo[0]
        param2 = partsInfo[2].replace(' ', '') 

        url2 = f'https://bnccompras.com/Process/ProcessBatchItems?param1={param1}&param2={param2}'

        headers = {            
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://bnccompras.com",
            "Referer": url,
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

        print(url2)

        response = requests.post(url2, headers=headers)
        resultadoItem = json.loads(response.text)
        PageItem = resultadoItem['html']

        html_Item = re.sub(r'\s+', ' ', PageItem)

        numero_lote_match = re.search(r'Nº.*?value=\"(\d+)\"', html_Item)
        numero_lote = numero_lote_match.group(1).strip() if numero_lote_match else None

        num_lote = formatar_lote(numero_lote)

        fase_lote_match = re.search(r'FASE:.*?value=\"(.*?)\"', html_Item)
        fase_lote = fase_lote_match.group(1).strip() if fase_lote_match else None

        tipo_lote_match = re.search(r'TIPO DE LOTE.*?value=\"(.*?)\"', html_Item)
        tipo_lote = tipo_lote_match.group(1).strip() if tipo_lote_match else None

        me_epp_match = re.search(r'EXCLUSIVO\sME/EPP.*?value=\"(.*?)\"', html_Item)
        me_epp_declarado = me_epp_match.group(1).strip() if me_epp_match else None
        me_epp = 'S' if me_epp_declarado in ['SIM'] else 'N'

        valor_vencedor_match = re.search(r'>MELHOR\sOFERTA.*?value=\"(.*?)\"', html_Item)
        valor_vencedor = valor_vencedor_match.group(1).strip() if valor_vencedor_match else None
        valor = float(str(valor_vencedor).replace(' ', '').replace('.', '').replace(',', '.'))

        quantidade_lote_match = re.search(r'QUANTIDADE.*?value=\"(\d+)\"', html_Item)
        quantidade_lote_tratado = quantidade_lote_match.group(1).strip() if quantidade_lote_match else None
        quantidade_lote = float(str(quantidade_lote_tratado).replace(' ', '').replace('.', '').replace(',', '.'))

        valor_ref_match = re.search(r'VALOR REF..*?value=\"(.*?)\"', html_Item)
        valor_ref_tratado = valor_ref_match.group(1).strip() if valor_ref_match else 0
        valor_ref = float(str(valor_ref_tratado).replace(' ', '').replace('.', '').replace(',', '.'))

        vencedor_match = re.search(r'DETENTOR\sDA\sMELHOR\sOFERTA.*?value=\"(.*?)\"', html_Item)
        vencedor = vencedor_match.group(1).strip() if vencedor_match else None

        itens = []
        resultados = []

        bloco_itens = re.findall(r'table\stable-striped.*', html_Item)
        for bloco_item in bloco_itens:
            itens_encontrado = re.findall(r'</tr>\s<tr>(.*?)<td><input', bloco_item)

            for item_encontrado in itens_encontrado:
                soup = BeautifulSoup(item_encontrado, 'html.parser')
                row = soup.find_all('td')

                numero_item = row[0].text.strip()
                descricao = row[1].text.strip()
                unidade_fornecimento = row[2].text.strip()
                quantidade = row[3].text.strip()
                quantidade_limpeza = float(str(quantidade).replace(' ', '').replace('.', '').replace(',', '.'))

                valor_estimado_match = row[4].text.strip()
                valor_estimado = float(str(valor_estimado_match).replace(' ', '').replace('.', '').replace(',', '.'))

                numero_lote_item = formatar_lote_item(numero_lote, numero_item)

                if tipo_lote == 'GLOBAL' and valor_ref == 0:
                    valor_unitario = valor
                    valor_global = valor_unitario * quantidade_limpeza
                elif tipo_lote == 'GLOBAL' and valor_ref != 0:
                    multiplicacao = valor_estimado * quantidade_limpeza
                    divisao = multiplicacao / valor_ref
                    valor_unitario = divisao * valor
                    valor_global = valor_unitario / quantidade_limpeza
                else:
                    valor_unitario = valor
                    valor_global = valor_unitario * quantidade_limpeza

                    
                itens.append({
                    'codigo': codigo,
                    'item': numero_lote_item,
                    'descricao': descricao,
                    'unidade': unidade_fornecimento,
                    'quantidade': quantidade,
                    'me_epp': me_epp,
                    'situacao': fase_lote,
                    'vencedor': vencedor,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_global,
                }) 

                resultados.append({
                    'codigo': codigo, 
                    'item': numero_lote_item, 
                    'empresa': vencedor,
                    'colocacao': 1,
                    'descricao': descricao, 
                    'quantidade': quantidade_limpeza,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_global,
                })


        regexBidHistory = re.findall(r"BidHistory',\s*\['(.*?)'\]", html_Item)

        url3 = f"https://bnccompras.com/Batch/BidHistory?param1={regexBidHistory[0]}"

        responseLance = requests.get(url3, headers=headers)
        resultadoLance = json.loads(responseLance.text)
        PageLance = resultadoLance['html']

        html_lance = re.sub(r'\s+', ' ', PageLance)

        lances = []
        lista_classificados = []
        empresas = []

        bloco_lances_classificado = re.search(r'Lances\se\sClassificação(.*?)</table>\s</div></div>', html_lance)
        if bloco_lances_classificado:
            bloco_lances_encontrado = bloco_lances_classificado.group(0)

            blocos_lances = re.findall(r'</tr>\s<tr>(.*?)type=\"checkbox\"\s\/>', bloco_lances_encontrado)
            for bloco_lance in blocos_lances:
                soup_lance = BeautifulSoup(bloco_lance, 'html.parser')
                row1 = soup_lance.find_all('td')

                data_hora = row1[0].text.strip()
                participante = row1[1].text.strip()
                valor = row1[2].text.strip()
                valor_limpeza = float(str(valor).replace(' ', '').replace('.', '').replace(',', '.'))  

                mapa_lances = {
                    "codigo": codigo,
                    "participante": participante,
                    "item": num_lote,
                    "valor": valor_limpeza,
                    "data": data_hora,
                }
                lances.append(mapa_lances)

            empresa_unica = set()
            bloco_classificacao = re.findall(r'>Classificação(.*?)<\/table>', bloco_lances_encontrado)
            if bloco_classificacao:  
                blocos_classificados = re.findall(r'(<td>.*?)</tr>', bloco_classificacao[0])
                for bloco_classificado in blocos_classificados:
                    soup_classificao = BeautifulSoup(bloco_classificado, 'html.parser')
                    row2 = soup_classificao.find_all('td')

                    razao_social_classificado = row2[0].text.strip()
                    participante_classificado = row2[1].text.strip()
                    valor_classificado = row2[2].text.strip()
                    valor_classificado_limpeza = float(str(valor_classificado).replace(' ', '').replace('.', '').replace(',', '.'))  

                    mapa_classificados = {
                        'participante': participante_classificado,
                        'razao_social': razao_social_classificado,
                        'valor': valor_classificado_limpeza
                    }
                    lista_classificados.append(mapa_classificados)
                        
                    if razao_social_classificado not in empresa_unica:
                        empresas.append({
                            'empresa': razao_social_classificado,
                        })
                        empresa_unica.add(razao_social_classificado)


            for lance in lances:
                for classificado in lista_classificados:
                    if classificado['participante'] == lance['participante']:
                        lance['empresa'] = classificado['razao_social']
                        break
            
        for lance in lances:
            del lance['participante']

        all_empresas.extend(empresas)
        all_lances.extend(lances)
        all_resultados.extend(resultados)
        all_itens.extend(itens)

    empresas_unicas = {empresa['empresa']: empresa for empresa in all_empresas}.values()
    idUuid = uuid.uuid4()

    nomeArquivosItem = f'/itens_{idUuid}_{codigo}.json'
    nomeArquivosResultado = f'/resultados_{idUuid}_{codigo}.json'
    nomeArquivosProposta = f'/propostas_{idUuid}_{codigo}.json'
    nomeArquivosEmpresa = f'/empresas_{idUuid}_{codigo}.json'
    nomeArquivosLance = f'/lances_{idUuid}_{codigo}.json'

    with open(f'{diretorio}{nomeArquivosItem}', "w", encoding="utf-8") as f:
        json.dump({'itens': all_itens}, f, indent=4, ensure_ascii=False)

    with open(f'{diretorio}{nomeArquivosLance}', "w", encoding="utf-8") as f:
        json.dump({'lances': all_lances}, f, indent=4, ensure_ascii=False)

    with open(f'{diretorio}{nomeArquivosEmpresa}', "w", encoding="utf-8") as f:
        json.dump({'empresas': list(empresas_unicas)}, f, indent=4, ensure_ascii=False)

    with open(f'{diretorio}/{nomeArquivosResultado}', "w", encoding="utf-8") as f:
        json.dump({'resultados': all_resultados}, f, indent=4, ensure_ascii=False)
