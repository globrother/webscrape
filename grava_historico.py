import datetime
import pytz
import os
import http.client
import json
import logging
import time

# Usar o logger para registrar mensagens
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info(' Função Gravar Histórico Iniciada\n')

# Configurar a conexão com o Back4App
APPLICATION_ID = os.getenv("APPLICATION_ID")
REST_API_KEY = os.getenv("REST_API_KEY")

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

# Função para criar uma nova classe dinamicamente
def create_dynamic_class(class_name):
    return class_name

def obter_nome_classe(sufixo):
    # Função para gerar o nome da classe
    if len(sufixo) > 6:
        return sufixo
    else:
        return f"historico_{sufixo}"

def testar_conexao():
    try:
        connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
        connection.connect()
        connection.request('GET', '/', '', {
            "X-Parse-Application-Id": APPLICATION_ID,
            "X-Parse-REST-API-Key": REST_API_KEY
        })
        response = connection.getresponse()
        if response.status == 200:
            logger.info("\n Conexão bem-sucedida com o servidor Back4App.\n")
            connection.close()
            return True
        else:
            logger.error(f"\n Falha ao conectar com o servidor Back4App. Status: {response.status}\n")
            connection.close()
            return False
    except Exception as e:
        logger.error(f"\n Erro ao conectar com o servidor Back4App: {e}\n")
        return False

def gravar_historico(sufixo, valor):
    if not testar_conexao():
        print("\n Erro ao conectar com o servidor Back4App.")
        return
    
    nome_classe = obter_nome_classe(sufixo)
    
    logger.info(f"\n Função gravar iniciada em: {nome_classe}\n")
    
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    tempo_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    #data_tempo_atual = f"{data_atual}\u2003{tempo_atual}"
    #print(tempo_atual)
    novo_registro = {
        "data": data_atual,
        "tempo": tempo_atual,
        "valor": valor  # Valor já formatado como string
    }

    # Conexão ao servidor Back4App
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
    connection.connect()
    
    # Requisição GET para recuperar o registro mais recente
    connection.request('GET', f'/classes/{nome_classe}?order=-createdAt&limit=1', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    resultado = json.loads(connection.getresponse().read())
    #logger.info(f"Resultado mais recente: {resultado}")

    if resultado['results'] and resultado['results'][0]['valor'] == valor:
        #logger.info(f"Valor zero da tabela: {resultado['results'][0]['valor']}")
        print("\n O valor é igual ao último registrado. Não será gravado novamente.\n")
        connection.close()
        return

    # Adiciona o novo registro no Parse
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
    connection.connect()
    connection.request('POST', f'/classes/{nome_classe}', json.dumps(novo_registro), {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY,
        "Content-Type": "application/json"
    })
    response = connection.getresponse()
    if response.status == 201:
        print("\n Histórico gravado com sucesso.\n")
        connection.close()
    else:
        print(f"\n Erro ao gravar histórico: {response.reason}\n")

    # Verificar o limite de registros e remover os mais antigos se necessário
    if len(sufixo) > 6:
        limite_registros = 5
    else:
        limite_registros = 250
    
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
    connection.connect()
    connection.request('GET', f'/classes/{nome_classe}?count=1&limit=0', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    logger.info(f"\n Verificando Contagem de registros em: {nome_classe}\n")
    response = connection.getresponse()
    logger.info(f"\n Response status: {response.status}\n")  # Adiciona log do status da resposta
    data = response.read()
    #logger.info(f"Dados da resposta: {data}") 
    total_registros = json.loads(data).get('count', 0)
    logger.info(f"\n Histórico Gravado com total de registros igual a {total_registros}\n")
    
    if total_registros > limite_registros:
        connection.request('GET', f'/classes/{nome_classe}?order=-createdAt&skip={limite_registros}', '', {
            "X-Parse-Application-Id": APPLICATION_ID,
            "X-Parse-REST-API-Key": REST_API_KEY
        })
        registros_antigos = json.loads(connection.getresponse().read())['results']
        for registro in registros_antigos:
            connection.request('DELETE', f'/classes/{nome_classe}/{registro["objectId"]}', '', {
                "X-Parse-Application-Id": APPLICATION_ID,
                "X-Parse-REST-API-Key": REST_API_KEY
            })
            connection.getresponse()
            connection.close()

def ler_historico(sufixo):
    if not testar_conexao():
        print("\n Erro ao conectar com o servidor Back4App.\n")
        return
    
    nome_classe = obter_nome_classe(sufixo)
    logger.info(f"\n Iniciando Leitura de: {nome_classe}\n")
    
    # Conexão ao servidor Back4App
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
    connection.connect()
    logger.info(f"\n Conectando ao servidor para ler: {nome_classe}\n")

    # Requisição GET para recuperar objetos da classe ordenados por createdAt
    connection.request('GET', f'/classes/{nome_classe}?order=-createdAt', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    resultados = json.loads(connection.getresponse().read())
    historico = [{"data": resultado['data'],"tempo": resultado.get('tempo', ':'),"valor": resultado['valor']} for resultado in resultados['results']]
    connection.close()
    #historico = [{'data': '24/01/2025','tempo': '14:15','valor': 'R$ 9,16'}]
    #logger.info(f"valor de hitórico: {historico}")
    return historico
    
def gerar_texto_historico(historico, aux):
    logger.info("\n Iniciando Gerar Histórico\n")
    if aux == "alert":
        # Usar a nova coluna "tempo"
        linhas = [f'• {registro["tempo"]} {registro["tempo"]}\u2003{registro["valor"]}' for registro in historico]
        if len(linhas) > 1:
            linhas = [f'{linhas[0]}\u2003{linhas[1]}']
        logger.info("\n Histórico gerado \n")
        return "<br>".join(linhas)
    else:
        linhas = [f'{registro["data"]}\u2003{registro["tempo"]}\u2003{registro["valor"]}' for registro in historico]
        logger.info("\n Histórico gerado\n")
        return "<br>".join(linhas)