## Coleta_Dados
Projeto Criação de Web Scraping - Python

# Robôs Python para Coleta e Tratamento de Dados

Este repositório contém scripts em Python desenvolvidos para realizar automação de coleta, extração e tratamento de dados relacionados a compras públicas e outros processos administrativos. Os robôs têm como objetivo simplificar a manipulação de informações, geração de relatórios e armazenamento de dados estruturados.

## Principais Scripts

# 1. portalDeComprasPublicas.py

- Realiza requisições à API do Portal de Compras Públicas para extrair informações sobre processos de licitação.

- Gera arquivos JSON contendo detalhes de itens, resultados, propostas, lances e empresas participantes.

- Os dados são organizados em diretórios com base na data atual.

# 2. publinexoAta.py

- Extrai conteúdo HTML de atas públicas no site Publinexo.

- Converte o HTML em um arquivo PDF e salva a versão original em formato HTML.

- Facilita o acesso e o arquivamento de documentos relacionados a atas públicas.

# 3. publinexoJSON.py

- Processa arquivos HTML gerados pelo publinexoAta.py.

- Extrai informações relevantes, como itens, propostas, empresas, lances e resultados.

- Gera arquivos JSON contendo os dados estruturados para análise posterior.

# 4. bncCompras.py

- Coleta informações de licitações no site BNC Compras.

- Extrai dados de itens, lances, empresas participantes e resultados.

- Armazena os dados em JSON organizados por data e processo licitatório.

# 5. comprasAmazonas.py

- Acessa o portal de compras do Amazonas para coletar informações de licitações.

- Extrai detalhes sobre produtos, lances e empresas concorrentes.

- Gera arquivos JSON contendo os dados organizados para análise posterior.

# 6. transparenciaVitoriaES.py

- Obtém dados da API do portal de transparência de Vitória/ES.

- Coleta informações sobre lotes, itens, participantes e vencedores.

- Gera arquivos JSON contendo os dados estruturados para relatórios e análises.

## Estrutura de Saída

Os robôs salvam os dados processados em diretórios organizados da seguinte forma:

- AtaJSON/: Armazena arquivos JSON com informações detalhadas.

- AtaPDF/: Contém arquivos PDF gerados a partir do conteúdo HTML.

- AtaHTML/: Contém os arquivos HTML baixados e processados.

# Dependências

Antes de executar os scripts, instale as dependências necessárias:

>>>> pip install -r requirements.txt


