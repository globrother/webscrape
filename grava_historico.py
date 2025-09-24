# grava_historico.py

import datetime
import pytz
import os
import http.client
import json
import requests
import sqlite3
import time
import html

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
from log_utils import log_debug, log_info, log_warning, log_error, log_telegram
# =====================================================================

# Usar o logger para registrar mensagens
#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
#log_info('--> Preparando para gerenciar o hitórico ...')

# Configurar a conexão com o Back4App
#APPLICATION_ID = os.getenv("APPLICATION_ID")
#REST_API_KEY = os.getenv("REST_API_KEY")

# Define o fuso horário para horário de Brasília
brt_tz = pytz.timezone("America/Sao_Paulo")

#criando conexão com o banco SQLite
def conectar_sqlite():
    return sqlite3.connect("finance.db")

"""# Função para criar uma nova classe dinamicamente
def create_dynamic_class(class_name):
    return class_name"""

"""
def obter_nome_classe(sufixo):
    # Função para gerar o nome da classe
    if len(sufixo) > 6:
        return sufixo
    else:
        return f"historico_{sufixo}"
"""

"""def testar_conexao():
    try:
        connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
        connection.connect()
        connection.request('GET', '/', '', {
            "X-Parse-Application-Id": APPLICATION_ID,
            "X-Parse-REST-API-Key": REST_API_KEY
        })
        response = connection.getresponse()
        if response.status == 200:
            log_info("Conexão bem-sucedida (servidor Back4App).")
            connection.close()
            return True
        else:
            log_error(f"Falha ao conectar (servidor Back4App). Status: {response.status}\n")
            connection.close()
            return False
    except Exception as e:
        log_error(f"\nErro ao conectar com o servidor Back4App: {e}\n")
        return False"""

def gravar_historico(sufixo, valor, var_fii_telegram=None):
    log_debug("Agora no método gravar_historico")
    conn = conectar_sqlite()
    cursor = conn.cursor()

    data_atual = datetime.datetime.now(brt_tz).strftime("%d/%m/%Y")
    tempo_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")

    # Verifica se o valor já existe
    cursor.execute("SELECT valor FROM historico WHERE ativo = ? ORDER BY data DESC, tempo DESC LIMIT 1", (sufixo,))
    resultado = cursor.fetchone()
    if resultado and resultado[0] == valor:
        log_warning("Valor igual ao último registrado. Abortando gravar.")
        conn.close()
        return

    # Envia alerta Telegram
    fii_safe = html.escape(sufixo.upper())
    cota_safe = html.escape(f"{valor}")
    mensagem = (
        f"<b>Gobs-Finance</b>: {var_fii_telegram}\n"
        f"O Ativo 🔸<b> {fii_safe} </b> chegou a 💵 ​<b>{cota_safe}</b>"
    )
    log_telegram(mensagem)

    # Insere novo registro
    cursor.execute("INSERT INTO historico (data, tempo, valor, ativo) VALUES (?, ?, ?, ?)",
                   (data_atual, tempo_atual, valor, sufixo))
    conn.commit()
    conn.close()
    log_info("Histórico gravado com sucesso.")


"""
def gravar_historico(sufixo, valor, var_fii_telegram=None):
    log_debug("Agora no método gravar_historico")
    #log_info("--> Iniciando Gravar Histórico")
    
    if not testar_conexao():
        log_error("Erro ao conectar com o servidor Back4App.")
        return
    
    nome_classe = obter_nome_classe(sufixo)
    
    log_info(f"Função gravar iniciada para: {nome_classe}")
    
    data_atual = datetime.datetime.now(brt_tz).strftime("%d/%m/%Y")
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
    #log_info(f"Resultado mais recente: {resultado}")

    if resultado['results'] and resultado['results'][0]['valor'] == valor:
        #log_info(f"Valor zero da tabela: {resultado['results'][0]['valor']}")
        log_warning("Valor igual ao último registrado. Abortando gravar.")
        connection.close()
        return
    else: # Garante que o alerta seja enviado ao telegram apenas se o valor for diferente
        fii_safe = html.escape(sufixo.upper())
        cota_safe = html.escape(f"{valor}")  # R$ 21,72
        mensagem = (
            f"<b>Gobs-Finance</b>: {var_fii_telegram}\n"
            f"O Ativo 🔸<b> {fii_safe} </b> chegou a 💵 ​<b>{cota_safe}</b>"
        )
        log_telegram(mensagem)

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
        log_info("Histórico gravado com sucesso.")
        connection.close()
    else:
        log_error(f"Erro ao gravar histórico: {response.reason}")

    # Verificar o limite de registros e remover os mais antigos se necessário
    if len(sufixo) > 6:
        limite_registros = 5
    else:
        limite_registros = 500
    
    connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
    connection.connect()
    connection.request('GET', f'/classes/{nome_classe}?count=1&limit=0', '', {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    })
    #log_debug(f"Verificando Contagem de registros em: {nome_classe}")
    response = connection.getresponse()
    log_debug(f"Response status: {response.status}")  # Adiciona log do status da resposta
    data = response.read()
    total_registros = json.loads(data).get('count', 0)
    log_debug(f"Histórico Gravado. Total de registros:{total_registros}")
    
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
"""

def ler_historico(sufixo):
    log_debug("Agora no método ler_historico")
    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT data, tempo, valor FROM historico WHERE ativo = ? ORDER BY data DESC, tempo DESC", (sufixo,))
        historico = [{"data": row[0], "tempo": row[1], "valor": row[2]} for row in cursor.fetchall()]
        conn.close()
        return historico
    except Exception as e:
        log_error(f"Erro ao ler histórico: {e}")
        return []

"""
def ler_historico(sufixo):
    log_debug("Agora no método ler_historico")

    try:
        #log_info("--> Iniciando Ler Histórico")
        
        if not testar_conexao():
            log_error("Erro ao conectar com o servidor Back4App.")
            return
        
        nome_classe = obter_nome_classe(sufixo)
        log_debug(f"Iniciando Leitura de: {nome_classe}")
        
        # Conexão ao servidor Back4App
        connection = http.client.HTTPSConnection('parseapi.back4app.com', 443)
        connection.connect()
        log_debug(f"Conectando ao servidor para ler: {nome_classe}")

        # Requisição GET para recuperar objetos da classe ordenados por createdAt
        connection.request('GET', f'/classes/{nome_classe}?order=-createdAt', '', {
            "X-Parse-Application-Id": APPLICATION_ID,
            "X-Parse-REST-API-Key": REST_API_KEY
        })
        resultados = json.loads(connection.getresponse().read())
        historico = [{"data": resultado['data'],"tempo": resultado.get('tempo', ':'),"valor": resultado['valor']} for resultado in resultados['results']]
        connection.close()
        #historico = [{'data': '24/01/2025','tempo': '14:15','valor': 'R$ 9,16'}]
        #log_info(f"valor de hitórico: {historico}")
        return historico
    except Exception as e:
        log_error(f"Erro ao ler histórico: {e}")
        return []  # Retorna uma lista vazia em caso de erro
"""
 
def gerar_texto_historico(historico, aux):
    log_debug("Agora no método gerar_texto_historico")
    #log_info("--> Iniciando Gerar Histórico")
    
    # Verificar se o histórico está vazio
    if not historico:
        log_info("Histórico está vazio")
        return "• 00/00/0000\u2003R$ 0,00"
    
    #log_info("Iniciando condição")
    
    if aux == "alert":
        # Usar a nova coluna "tempo"
        linhas = [f'• {registro["data"][:-4] + registro["data"][-2:]}\u2003{registro["valor"]}' for registro in historico]
        #log_info(f"\n Linhas antes: {linhas}\n")
        if len(linhas) > 1:
            if len(linhas) >= 4:
                linhas = [f'{linhas[0]}\u2003{linhas[1]}<br>{linhas[2]}\u2003{linhas[3]}']
            elif len(linhas) == 3:
                linhas = [f'{linhas[0]}\u2003{linhas[1]}<br>{linhas[2]}']
            else:
                linhas = [f'{linhas[0]}\u2003{linhas[1]}']
            #log_info(f"Hist alerta gerado: {linhas}")
        else:
            log_info("Um registro encontrado")
            linhas = [linhas[0]]
        #if len(linhas) > 1:
            #linhas = [f'{linhas[0]}\u2003{linhas[1]}<br>{linhas[2]}\u2003{linhas[3]}']
        #log_info(f"Histórico de alerta gerado: {linhas}")
        return "<br>".join(linhas)
    else:
        log_info(f'{historico[0]["valor"]}')
        linhas = [f'{registro["data"][:-5]} {registro["tempo"]}\u2003{registro["valor"]}' for registro in historico]
        #linhas = [f'{registro["data"][:-5]} {registro["tempo"]}\u2003R$ {float(registro["valor"]):,.2f}'.replace('.', ',') for registro in historico]
        
        #meio = len(linhas) // 2  # Divide ao meio para colunas no APL
        log_debug("Histórico de ativo gerado")
        log_info("✅🖥️ Mostrando Tela")
        #return "<br>".join(linhas)
        return linhas

#::--> CARREGAR LISTA DE ATIVOS - USA CACHE EM ATÉ 10 MINUTOS <--::
# Variáveis globais para cache
_ativos_cache = None
_ativos_cache_time = 0
_CACHE_TTL = 60 * 10  # 10 minutos


def carregar_ativos():
    log_debug("Agora no método carregar_ativos")
    global _ativos_cache, _ativos_cache_time
    agora = time.time()

    # Se o cache existe e não expirou, retorna do cache
    if _ativos_cache and (agora - _ativos_cache_time) < _CACHE_TTL:
        return _ativos_cache

    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT state_id, status, codigo, nome, favorite, apelido FROM ativos")
        ativos_raw = cursor.fetchall()
        conn.close()

        # Converte para lista de dicionários
        ativos = [
            {
                "state_id": row[0],
                "status": row[1],
                "codigo": row[2],
                "nome": row[3],
                "favorite": row[4],
                "apelido": row[5]
            }
            for row in ativos_raw
        ]

        # Cria o mapeamento por state_id
        state_fund_mapping = {f["state_id"]: f for f in ativos if f["status"]}

        # Atualiza o cache
        _ativos_cache = (state_fund_mapping, ativos)
        _ativos_cache_time = agora
        return _ativos_cache

    except Exception as e:
        log_error(f"❌ Erro ao carregar ativos do SQLite: {e}")
        return ({}, [])

"""
def carregar_ativos():
    log_debug("Agora no método carregar_ativos")
    global _ativos_cache, _ativos_cache_time
    agora = time.time()
    # Se o cache existe e não expirou, retorna do cache
    if _ativos_cache and (agora - _ativos_cache_time) < _CACHE_TTL:
        return _ativos_cache

    # Senão, busca do Back4App
    url = "https://parseapi.back4app.com/classes/map_ativo?limit=1000"
    #print("APPLICATION_ID:", APPLICATION_ID)
    #print("REST_API_KEY:", REST_API_KEY)
    headers = {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            log_error(f"❌ Erro ao decodificar JSON: {e}")
            data = {"results": []}
    else:
        log_error(f"❌ Requisição falhou. Status code: {response.status_code}")
        data = {"results": []}

    #log_info(f"DEBUG resposta Back4App:{data}") 
    ativos = data['results']
    #state_fund_mapping = {f['state_id']: f['codigo'] for f in ativos if f['status']}
    state_fund_mapping = {f['state_id']: f for f in ativos if f.get('status', True)}
    # Atualiza o cache
    _ativos_cache = (state_fund_mapping, ativos)
    _ativos_cache_time = agora
    return _ativos_cache

# Exemplo de uso:
#state_fund_mapping, lista_ativos = carregar_ativos()
"""

#::--> ADICIONAR ATIVO AO BANCO DE DADOS <--::
def adicionar_ativo(ativo_dict):
    log_debug("Agora no método adicionar_ativo")

    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()

        # Extrai os campos esperados do dicionário
        state_id = ativo_dict.get("state_id")
        status = ativo_dict.get("status", 1)
        codigo = ativo_dict.get("codigo")
        nome = ativo_dict.get("nome", "")
        favorite = ativo_dict.get("favorite", 0)
        apelido = ativo_dict.get("apelido", "")

        # Verifica se o ativo já existe
        cursor.execute("SELECT COUNT(*) FROM ativos WHERE state_id = ?", (state_id,))
        existe = cursor.fetchone()[0]

        if existe:
            log_warning(f"⚠️ Ativo com state_id {state_id} já existe. Abortando inserção.")
            conn.close()
            return False

        # Insere novo ativo
        cursor.execute("""
            INSERT INTO ativos (state_id, status, codigo, nome, favorite, apelido)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (state_id, status, codigo, nome, favorite, apelido))

        conn.commit()
        conn.close()
        log_info(f"✅ Ativo cadastrado com sucesso: {ativo_dict}")
        return True

    except Exception as e:
        log_error(f"❌ Erro ao cadastrar ativo no SQLite: {e}")
        return False

"""
def adicionar_ativo(ativo_dict):
    log_debug("Agora no método adicionar_ativo")
    url = "https://parseapi.back4app.com/classes/map_ativo"
    headers = {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(ativo_dict))
    log_debug(f"resposta de adicionar_ativo: {response.status_code}")
    if response.status_code in (200, 201):
        log_info(f"Arquivo gravado: {ativo_dict}\n")
        return response.json()
    else:
        log_error(f"❌ Erro ao cadastrar ativo: {response.text}")
        return False
"""
#::--> EXCLUIR ATIVO AO BANCO DE DADOS <--::
def excluir_ativo(state_id):
    log_debug(f"🗑️ Agora no método excluir_ativo: {state_id}")

    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()

        # Verifica se o ativo existe
        cursor.execute("SELECT COUNT(*) FROM ativos WHERE state_id = ?", (state_id,))
        existe = cursor.fetchone()[0]

        if not existe:
            log_warning(f"⚠️ Ativo com state_id {state_id} não encontrado. Nada foi excluído.")
            conn.close()
            return False

        # Exclui o ativo
        cursor.execute("DELETE FROM ativos WHERE state_id = ?", (state_id,))
        conn.commit()
        conn.close()

        log_info(f"✅ Ativo excluído com sucesso: {state_id}")
        return True

    except Exception as e:
        log_error(f"❌ Erro ao excluir ativo no SQLite: {e}")
        return False


"""
def excluir_ativo(object_id):
    log_debug(f"🗑️ Agora no método excluir_ativo: {object_id}")
    url = f"https://parseapi.back4app.com/classes/map_ativo/{object_id}"
    headers = {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        log_info(f"✅ Ativo excluído com sucesso: {object_id}")
        return True
    else:
        log_error(f"❌ Erro ao excluir ativo: {response.text}")
        return False"""

# ::--> ATUALIZAR STATUS DO ATIVO <--::
def atualizar_status_ativo(state_id, status: bool):
    log_debug(f"Atualizando status do ativo {state_id} para {status}")

    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()

        # Verifica se o ativo existe
        cursor.execute("SELECT COUNT(*) FROM ativos WHERE state_id = ?", (state_id,))
        existe = cursor.fetchone()[0]

        if not existe:
            log_warning(f"⚠️ Ativo com state_id {state_id} não encontrado. Nada foi atualizado.")
            conn.close()
            return False

        # Atualiza o status
        cursor.execute("UPDATE ativos SET status = ? WHERE state_id = ?", (int(status), state_id))
        conn.commit()
        conn.close()

        log_info(f"✔️ Status atualizado com sucesso para {status}")
        return True

    except Exception as e:
        log_error(f"❌ Erro ao atualizar status no SQLite: {e}")
        return False


"""
def atualizar_status_ativo(object_id, status: bool):
    log_debug(f"Atualizando status do ativo {object_id} para {status}")
    url = f"https://parseapi.back4app.com/classes/map_ativo/{object_id}"
    headers = {
        "X-Parse-Application-Id": APPLICATION_ID,
        "X-Parse-REST-API-Key": REST_API_KEY,
        "Content-Type": "application/json"
    }
    body = {"status": status}
    response = requests.put(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        log_info(f"✔️ Status atualizado com sucesso para {status}")
        return True
    else:
        log_error(f"❌ Erro ao atualizar status: {response.text}")
        return False
"""

# ::--> ATUALIZAR FAVORITE DO ATIVO <--::
def atualizar_favorito(state_id, favorito_bool):
    try:
        log_debug(f"Atualizando favorito do ativo {state_id} para {favorito_bool}")
        conn = conectar_sqlite()
        cursor = conn.cursor()

        # Verifica se o ativo existe
        cursor.execute("SELECT COUNT(*) FROM ativos WHERE state_id = ?", (state_id,))
        existe = cursor.fetchone()[0]

        if not existe:
            log_warning(f"⚠️ Ativo com state_id {state_id} não encontrado. Nada foi atualizado.")
            conn.close()
            return False

        # Atualiza o campo favorite
        cursor.execute("UPDATE ativos SET favorite = ? WHERE state_id = ?", (int(favorito_bool), state_id))
        conn.commit()
        conn.close()

        log_info(f"✔️ Favorito atualizado com sucesso para {favorito_bool}")
        return True

    except Exception as e:
        log_error(f"❌ Erro ao atualizar favorito no SQLite: {e}")
        return False

"""
def atualizar_favorito(object_id, favorito_bool):
    try:
        log_debug(f"Atualizando status do ativo {object_id} para {favorito_bool}")
        url = f"https://parseapi.back4app.com/classes/map_ativo/{object_id}"
        log_warning(f"Id do OBJETO:{object_id}:{favorito_bool}")
        headers = {
            "X-Parse-Application-Id": APPLICATION_ID,
            "X-Parse-REST-API-Key": REST_API_KEY,
            "Content-Type": "application/json"
        }
        body = {"favorite": favorito_bool}
        response = requests.put(url, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            log_debug(f"Resposta bruta do servidor: {response.text[:300]}")
            log_info(f"✔️ Status do favorito atualizado com sucesso para {favorito_bool}")
            return True
        else:
            log_error(f"❌ Erro ao atualizar status do favorito: {response.text}")
            return False
    except Exception as e:
        log_error(f"Erro ao atualizar favorito: {e}")
        return False
"""
