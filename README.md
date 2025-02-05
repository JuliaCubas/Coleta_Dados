## Coleta_Dados
Projeto Criação de Web Scraping - Python

# Robôs Python para Coleta e Tratamento de Dados

Este repositório contém scripts em Python desenvolvidos para realizar automação de coleta, extração e tratamento de dados relacionados a compras públicas e outros processos administrativos. Os robôs têm como objetivo simplificar a manipulação de informações, geração de relatórios e armazenamento de dados estruturados.

## Principais Scripts


1. portalDeComprasPublicas.py

- Realiza requisições à API do Portal de Compras Públicas para extrair informações sobre processos de licitação.
- Gera arquivos JSON contendo detalhes de itens, resultados, propostas, lances e empresas participantes.
- Os dados são organizados em diretórios com base na data atual.
  

2. publinexoAta.py

- Extrai conteúdo HTML de atas públicas no site Publinexo.
- Converte o HTML em um arquivo PDF e salva a versão original em formato HTML.
- Facilita o acesso e o arquivamento de documentos relacionados a atas públicas.
  

3. publinexoJSON.py

- Processa arquivos HTML gerados pelo publinexoAta.py.
- Extrai informações relevantes, como itens, propostas, empresas, lances e resultados.
- Gera arquivos JSON contendo os dados estruturados para análise posterior.
  

4. bncCompras.py

- Coleta informações de licitações no site BNC Compras.
- Extrai dados de itens, lances, empresas participantes e resultados.
- Armazena os dados em JSON organizados por data e processo licitatório.
  

5. comprasAmazonas.py

- Acessa o portal de compras do Amazonas para coletar informações de licitações.
- Extrai detalhes sobre produtos, lances e empresas concorrentes.
- Gera arquivos JSON contendo os dados organizados para análise posterior.
  

6. transparenciaVitoriaES.py

- Obtém dados da API do portal de transparência de Vitória/ES.
- Coleta informações sobre lotes, itens, participantes e vencedores.
- Gera arquivos JSON contendo os dados estruturados para relatórios e análises.

7.compraEletronicaJundiai.py

- Coleta informações de licitações do portal de compras eletrônicas de Jundiaí/SP.
- Extrai detalhes de itens, propostas, empresas participantes e resultados.
- Gera arquivos JSON contendo dados estruturados para análise posterior.
  
8.estaleiroComprasnet.py

- Automatiza a coleta de dados do portal Comprasnet usando Selenium.
- Extrai informações sobre itens, propostas, resultados e empresas participantes.
- Realiza a decodificação de pacotes de rede para obter dados detalhados de licitações.
- Armazena os dados em arquivos JSON organizados por mês e ano para facilitar o acesso.
  
9.pncp.py

- Acessa a API do Portal Nacional de Contratações Públicas (PNCP).
- Coleta informações sobre itens de compras, propostas e resultados homologados.
- Identifica empresas vencedoras, valores homologados e benefícios aplicados (ME/EPP).
- Gera arquivos JSON contendo os dados estruturados para relatórios e análises.

10.peIntegradoBusca.py

- Coleta informações de licitações do portal PE Integrado de Pernambuco.
- Realiza consultas à API do portal para buscar processos de licitação encerrados.
- Extrai dados como número do processo, órgão responsável, modalidade, edital e datas.
- Obtém detalhes adicionais de cada licitação, incluindo informações sobre as empresas participantes.
- Gera um arquivo JSON consolidado com todas as licitações extraídas para facilitar a análise posterior.

11.comprasnetRelacaoItens.py

- Coleta informações de itens de licitações no portal Comprasnet antigo.
- Acessa detalhes de editais de licitação usando parâmetros como UASG e número do edital.
- Extrai informações sobre itens de material, incluindo número do produto, descrição, quantidade e unidade de fornecimento.
- Identifica o tratamento diferenciado para ME/EPP, aplicabilidade de decretos e margens de preferência.
- Gera um arquivo JSON contendo os dados dos itens para facilitar consultas e análises futuras.

12.bllCompras.py

- Coleta informações de licitações no site BLL Compras.
- Extrai dados de itens, lances, empresas participantes e resultados.
- Armazena os dados em JSON organizados por data e processo licitatório.

## Estrutura de Saída

Os robôs salvam os dados processados em diretórios organizados da seguinte forma:

- AtaJSON/: Armazena arquivos JSON com informações detalhadas.

- AtaPDF/: Contém arquivos PDF gerados a partir do conteúdo HTML.

- AtaHTML/: Contém os arquivos HTML baixados e processados.
  

# Dependências

Antes de executar os scripts, instale as dependências necessárias:

> pip install -r requirements.txt


