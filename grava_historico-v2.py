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
logger.info('Função Gravar iniciada')

# Configurar a conexão com o Back4App
APPLICATION_ID = ""
REST_API_KEY = ""

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

# Função para criar uma nova classe dinamicamente
def create_dynamic_class(class_name):
    return class_name

def obter_nome_classe(sufixo):
    # Exemplo de função para gerar o nome da classe
    return f"historico_{sufixo}"

def testar_conexao():
    try:
        connection = http.client.HTTPSConnection('parseapi.back4app.com', 443) #timeout=20
        connection.connect()
        connection.request('GET', '/', '', {
            "X-Parse-Application-Id": APPLICATION_ID,
            "X-Parse-REST-API-Key": REST_API_KEY
        })
        response = connection.getresponse()
        if response.status == 200:
            logger.info("Conexão bem-sucedida com o servidor Back4App.")
            return True
        else:
            logger.error(f"Falha ao conectar com o servidor Back4App: {response.status}")
            return False
    except Exception as e:
        logger.error(f"Erro ao conectar com o servidor Back4App: {e}")
        return False

def gravar_historico(sufixo, valor, limite_registros=250):
    if not testar_conexao():
        logger.error("Erro ao conectar com o servidor Back4App.")
        return
    
    nome_classe = obter_nome_classe(sufixo)
    
    logger.info(f"Função Gravar iniciada: {nome_classe}")
    
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    data_hora_atual = f"{data_atual}\u2003{hora_atual}"
    print(hora_atual)
    novo_registro = {
        "data": data_hora_atual,
        "valor": valor  # Valor já formatado como string
    }

    # Conexão ao servidor Back4App
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
    connection.connect()
    
    connection.request('GET', f'/classes/{nome_classe}?count=1&limit=0', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    contagem = connection.getresponse()
    logger.info(f"\nNúmero TOTAL de registros teste: {contagem}\n")
    logger.info(f"Response status: {contagem.status}")
    data = contagem.read()
    logger.info(f"valor de data AQUI: {data}")
    
    # Verificar o limite de registros e remover os mais antigos se necessário
    for tentativa in range(3):
        try:
            logger.info(f"Iniciando verificação de limite de registros para: {nome_classe}")
            connection.request('GET', f'/classes/{nome_classe}?count=1&limit=0', '', {
                "X-Parse-Application-Id": APPLICATION_ID,
                "X-Parse-REST-API-Key": REST_API_KEY
            })
            logger.info(f"PASSOU AQUI COUNT=1: {nome_classe}")
            time.sleep(1)
            
            contagem = connection.getresponse()
            logger.info("Obteve resposta do servidor.")
            logger.info(f"Response object: {contagem}")  # Adiciona log do objeto response
            logger.info(f"Response status: {contagem.status}")  # Adiciona log do status da resposta
            
            # Verifica se a resposta contém dados antes de lê-los
            if contagem:
                data = contagem.read()
                logger.info(f"Dados da resposta: {data}")
                total_registros = json.loads(data).get('count', 0)
                logger.info(f"\nNúmero TOTAL de registros: {total_registros}\n")
                
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
                break
            else:
                logger.error("Erro: A resposta da requisição GET está vazia.")
        except Exception as e:
            logger.error(f"Tentativa {tentativa + 1} falhou: {e}")
            time.sleep(2)  # Espera de 2 segundos antes de tentar novamente
    
    # Requisição GET para recuperar o registro mais recente
    connection.request('GET', f'/classes/{nome_classe}?order=-createdAt&limit=1', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    resultado = json.loads(connection.getresponse().read())
    logger.info(f"Resultado mais recente: {resultado}")

    if resultado['results'] and resultado['results'][0]['valor'] == valor:
        logger.info(f"Valor na tabela: {valor}")
        logger.info(f"Valor zero da tabela: {resultado['results'][0]['valor']}")
        print("O valor é igual ao último registrado. Não será gravado novamente.")
        return

    # Adiciona o novo registro no Parse
    connection.request('POST', f'/classes/{nome_classe}', json.dumps(novo_registro), {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY,
        "Content-Type": "application/json"
    })
    response = connection.getresponse()
    if response.status == 201:
        print("\nHistórico gravado com sucesso.\n")
    else:
        print(f"Erro ao gravar histórico: {response.reason}")

def ler_historico(sufixo):
    if not testar_conexao():
        logger.error("Erro ao conectar com o servidor Back4App.")
        return
    
    nome_classe = obter_nome_classe(sufixo)
    logger.info(f"DENTRO DA FUNÇÃO ler_historico: {nome_classe}")
    
    # Conexão ao servidor Back4App
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443, timeout=20)
    connection.connect()
    logger.info(f"CONECTANDO VERIFICAR: {nome_classe}")

    # Requisição GET para recuperar objetos da classe ordenados por createdAt
    connection.request('GET', f'/classes/{nome_classe}?order=-createdAt', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    resultados = json.loads(connection.getresponse().read())
    historico = [{"data": resultado['data'], "valor": resultado['valor']} for resultado in resultados['results']]
    return historico

def gerar_texto_historico(historico):
    linhas = [f'{registro["data"]}:\u2003{registro["valor"]}' for registro in historico]
    return "<br>".join(linhas)
