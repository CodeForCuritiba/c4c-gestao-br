#!/usr/bin/env python3

# biblioteca utilizada paga buscar a página html
import requests

# expressão regular para algumas buscas
import re

# uso do colletions para a utilizacao da variável defaultdict
from collections import defaultdict

# BeautifulSoup para tratamento html
from bs4 import BeautifulSoup

# O bloco abaixo seta os valores para inserção na url que realiza a busca dos dados
# Tipos de licitações disponíveis para pesquisa no site da prefeitura
tipo = {'Concorrência': 1, 'Convite': 2, 'Pregão Eletrônico': 3, 'Pregão Presencial': 4, 'Leilão': 5, 'Tomada de Preços': 6, 'Chamamento Público': 7}
ano = int()
# o valor de cidade abaixo deve ser identico ao da url do site, como por exemplo em www.marmeleiro.pr.gov.br o valor de cidade é 'marmeleiro'
cidade = ('marmeleiro', )
pg_numero = int(1)

# variáveis para a montagem da url
ano = 2017
index = 0
protocolo = 'http://'
url_licitacao_base = '{0}www.{1}.pr.gov.br/sitio/licitacoes/'.format(protocolo, cidade[index])
dicionario_paginas = defaultdict(list)
dicionario_paginas_final = {}
#dicionario_paginas_beautiful = {}
#lista_de_arquivos = []

# Expressões regulares para busca de cadeias de caracteres relevantes
regra_procura_arquivos = re.compile(r'(?<=a href="licitacoes\/)(.*)(?=" target=")')
#regex_trunk_arquivo = re.compile(r'([^"]+)')
regex_recupera_paginas = re.compile(r'>([0-9]+\s?)<')

#teste = []


# Para cada chave e valor no dicionário de tipos de licitações disponíveis no site de busca, executar ...
for chave, valor in tipo.items():
    numero_paginas = []
    url = '{0}www.{1}.pr.gov.br/sitio/licitacoes-de-marmeleiro.php?rdTipo={2}&txtBusca=&slAno={3}&pg={4}&btPesquisar=+Pesquisar+'.format(protocolo, cidade[index], valor, ano, pg_numero)

    # realiza pesquisa no site da prefeitura, retorna dados apenas da página 1, se houver, os dados contidos aqui serão utilizados também para verificar a existencia de mais páginas.
    # se duas ou mais páginas forem encontradas, a ação 'requests.get()' deve ser realizada individualmente para cada página extra.
    dicionario_paginas[chave].append(requests.get(url))
    #dicionario_paginas_temp.update({chave: BeautifulSoup(dicionario_paginas[chave][0].content, 'html.parser')})
    # retorna uma lista contendo as numerações das páginas no formato 'str'
    #numero_paginas = regex_recupera_paginas.findall(str(dicionario_paginas_temp[chave].find("div", {"id": "paginacao"})))
    numero_paginas = regex_recupera_paginas.findall(str(BeautifulSoup(dicionario_paginas[chave][0].content, 'html.parser').find("div", {"id": "paginacao"}))) 
    # se número de páginas for maior que zero, executar ações abaixo.
    if len(numero_paginas) > 0:
        ''' Executar bloco somente se pesquisa retornar pelo menos uma página '''

        # percorre a lista contendo a numeração das páginas existentes para limpar cada número - strip() - e transforma-los em inteiros 'int'
        for i in range(len(numero_paginas)):
            numero_paginas[i] = int(numero_paginas[i].strip())

        contador_paginas = 1
        # executa ações para cada página retornada na pesquisa realizada acima
        while True:
            # se a página a ser percorrida for a primeira página, retirar dados da variável 'dicionario_paginas_temp[chave]' senão, deverá realizar a ação 'requests.get(url)' individualmente para cada página extra.
            if contador_paginas == 1:
                pass
            elif contador_paginas > 1:
                if contador_paginas < len(numero_paginas):
                    url = '{0}www.{1}.pr.gov.br/sitio/licitacoes-de-marmeleiro.php?rdTipo={2}&txtBusca=&slAno={3}&pg={4}&btPesquisar=+Pesquisar+'.format(protocolo, cidade[index], valor, ano, contador_paginas)
                    dicionario_paginas[chave].append(requests.get(url))
                elif contador_paginas == len(numero_paginas):
                    url = '{0}www.{1}.pr.gov.br/sitio/licitacoes-de-marmeleiro.php?rdTipo={2}&txtBusca=&slAno={3}&pg={4}&btPesquisar=+Pesquisar+'.format(protocolo, cidade[index], valor, ano, contador_paginas)
                    dicionario_paginas[chave].append(requests.get(url))
                    proxima_pagina = regex_recupera_paginas.findall(str(BeautifulSoup(dicionario_paginas[chave][contador_paginas -1].content, 'html.parser').find("div", {"id": "paginacao"}))) 
                    for i in range(len(proxima_pagina)):
                        proxima_pagina[i] = int(proxima_pagina[i].strip())
                    if len(proxima_pagina) > 0:
                        numero_paginas.extend(proxima_pagina)
            if contador_paginas == len(numero_paginas):
                break
            else:
                contador_paginas += 1

# tipo = variável que contém os valores chave - key - do dicionário,
# tem o nome de tipo pois refere-se ao tipo de licitação que se pode buscar no site da prefeitura
# veja a lista declarada no início do arquivo e que está reproduzida no comentário abaixo:
# tipo = {'Concorrência': 1, 'Convite': 2, 'Pregão Eletrônico': 3, 'Pregão Presencial': 4, 'Leilão': 5, 'Tomada de Preços': 6, 'Chamamento Público': 7}
contador_tipo = int(1)
for cada_tipo in dicionario_paginas:
    # dicinario_paginas é uma variável do tipo dicionário onde cada_tipo (variável de iteracao recebe o valor de cada chave por rodada)
    contador_pagina = int(1)
    for pagina in dicionario_paginas[cada_tipo]:
        # dentro da variável do tipo dicionário dicionario_paginas, os valores para cada chave é uma lista, logo, aqui fazemos interacao com cada elemento da lista
        # e abaixo atraves da biblioteca BeautifulSoup estraímos o htmnl da página retornada por requests.get(url)
        html_beautifulsoup = BeautifulSoup(pagina.content, 'html.parser')

        arquivos = ''
        arquivos = str(html_beautifulsoup.findAll('a', {'title': 'Clique aqui para ver este arquivo.'}))
        arquivos = arquivos.split('</a>')
        arquivos.pop()

        contador_arquivo = int(1)
        for arquivo_sujo in arquivos:
            arquivo_limpo = regra_procura_arquivos.search(arquivo_sujo).group()
            print(tipo[cada_tipo], '-', cada_tipo, '\t\tPagina:', contador_pagina, '| Arquivo nome:', arquivo_limpo)
            print(url_licitacao_base + arquivo_limpo)

        contador_pagina += 1
    contador_tipo += 1
