from datetime import datetime
import requests
import json
import re

url = "https://www.peintegrado.pe.gov.br/Portal/WebService/Servicos.asmx/PesquisarProcessos"

headers = {
    "Content-Type": "application/json"
}

processos = []
pagina_atual = 1

while True:
    payload = {
        "dtoProcesso": {
            "nAnoFinalizacao": 0,
            "tmpTipoMuralProcesso": 0,
            "nCdModulo": 0,
            "tmpTipoMuralVisao": 998,
            "nCdSituacao": 0,
            "tDtInicial": "2024-07-01T03:00:00.000Z",
            "tDtFinal": "2024-12-31T03:00:00.000Z",
            "nCdTipoProcesso": 0,
            "nCdEmpresa": 0,
            "sNrProcesso": "",
            "nCdProcesso": 0,
            "sDsObjeto": "",
            "sOrdenarPor": "NCDPROCESSO",
            "sOrdenarPorDirecao": "DESC",
            "dtoPaginacao": {"nPaginaDe": pagina_atual, "nPaginaAte": 50},
            "dtoIdioma": {},
            "SituacaoLicitacao": "Encerradas"
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()

        licitacoes = data.get('d', [])
        if not licitacoes:
            break
        for licitacao in licitacoes:

            Processo = licitacao.get('nCdProcesso')
            Modulo = licitacao.get('nCdModulo')
            idApuracao = licitacao.get('nIdTipoApuracao')
            Situacao = licitacao.get('nCdSituacao')
            Orgao = licitacao.get('sNmEmpresa')
            Modalidade = licitacao.get('sNmModalidade')

            tratamentoEdital = licitacao.get('sNrEdital')
            match_edital = re.search(r'AC[-\.].*?\..*?\.0*(\d*)\.', tratamentoEdital)
            Edital = match_edital.group(1) if match_edital else None

            dataInicio = licitacao.get('tDtInicial')
            timestamp = int(dataInicio.strip('/Date()/')) / 1000
            dataFormatada = datetime.fromtimestamp(timestamp)
            data = dataFormatada.strftime('%d/%m/%Y %H:%M:%S')

            urlDetalhes = "https://www.peintegrado.pe.gov.br/Portal/WebService/Servicos.asmx/PesquisarProcessoDetalhes"

            payloadDetalhes = {
                "dtoProcesso": {
                    "nCdProcesso": Processo,
                    "nCdModulo": Modulo,
                    "nCdSituacao": Situacao,
                    "sNrProcesso":0,
                    "tmpTipoMuralProcesso":0,
                    "dtoIdioma":{}
                }
            }

            responseDetalhes = requests.post(url, json=payload, headers=headers)

            dataDetalhes = response.json()

            detalhesLicitacoes = dataDetalhes.get('d', [])
            for detalheLicitacao in detalhesLicitacoes:
                Empresa = detalheLicitacao.get('nCdEmpresa')

            estruturaProcessos = {
                "CodProcesso": tratamentoEdital,
                "Processo": Processo,
                "Modulo": Modulo,
                "Apuracao": idApuracao,
                "Situacao": Situacao,
                "Orgao": Empresa,
                "Modalidade": Modalidade,
                "Edital": Edital,
                "Data": data
            }
            processos.append(estruturaProcessos)

        pagina_atual += 1

    with open(f"Licitacoes.json", "w", encoding="utf-8") as f:
        json.dump({"Licitacoes": processos}, f, indent=4, ensure_ascii=False)

    print(f"Coleta finalizada! {len(processos)} processos extraídos.")