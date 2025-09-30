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

from formatadores import formatar_reais


# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
from log_utils import log_debug, log_info, log_warning, log_error, log_telegram, adicionar_na_fila
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
    caminho = os.path.abspath("/home/ubuntu/webscrape/finance.db")
    return sqlite3.connect(caminho)
#def conectar_sqlite():
    #return sqlite3.connect("finance.db")

def gravar_historico(sigla, valor, tabela="historico", var_fii_telegram=None):
    log_debug("Agora no método gravar_historico")
    conn = conectar_sqlite()
    cursor = conn.cursor()

    data_atual = datetime.datetime.now(brt_tz).strftime("%d/%m/%Y")
    tempo_atual = datetime.datetime.now(brt_tz).strftime("%H:%M")
    log_debug(f"Tentando gravar na tabela: {tabela}, ativo: {sigla}, valor: {valor}")
    # Verifica se o valor já existe
    cursor.execute(f"""
        SELECT valor FROM {tabela}
        WHERE ativo = ?
        ORDER BY DATE(substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)) DESC,
                TIME(tempo) DESC
        LIMIT 1
    """, (sigla,))
    #cursor.execute("SELECT valor FROM historico WHERE ativo = ? ORDER BY data DESC, tempo DESC LIMIT 1", (sufixo,))
    resultado = cursor.fetchone()
    if resultado and resultado[0] == valor:
        log_warning("Valor igual ao último registrado. Abortando gravar.")
        conn.close()
        return

    # Envia alerta Telegram
    fii_safe = html.escape(sigla.upper())
    cota_safe = html.escape(f"{valor}")
    log_info(f"cota_safe antes: {cota_safe}")
    cota_safe = formatar_reais(cota_safe)
    log_info(f"cota_safe depois: {cota_safe}")
    mensagem = (
        f"🔸<b> {fii_safe}:</b> ​<b>{cota_safe}</b>\n"
        f"{var_fii_telegram}\n"
        f"O Ativo 🔸<b> {fii_safe} </b> chegou a 💵 ​<b>{cota_safe}</b>\n"
        f"--------------------------------------------------------"
    )
    log_telegram(mensagem)
    nivel = "WARNING"
    adicionar_na_fila(mensagem, nivel, chat_id=os.getenv("TELEGRAM_ALERT_ID"))

    # Insere novo registro
    cursor.execute("INSERT INTO historico (data, tempo, valor, ativo) VALUES (?, ?, ?, ?)",
                   (data_atual, tempo_atual, valor, sigla))
    conn.commit()
    conn.close()
    log_info(f"Histórico gravado com sucesso na tabela {tabela}.")
    
def ler_historico(sufixo):
    log_debug("Agora no método ler_historico")
    try:
        conn = conectar_sqlite()
        cursor = conn.cursor()
        
        log_info(f"Sufixo recebido: {sufixo}")
        if sufixo.startswith("alert:"):
            ativo = sufixo.split("alert:")[1].lower()
            log_debug(f"Consultando alertas para: {ativo}")
            cursor.execute("""
                SELECT data, tempo, valor
                FROM alertas
                WHERE ativo = ?
                ORDER BY DATE(substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)) DESC,
                         TIME(tempo) DESC
            """, (ativo,))

        else:
            ativo = sufixo.lower()
            log_debug(f"Consultando histórico para: {ativo}")
            cursor.execute("""
                SELECT data, tempo, valor
                FROM historico
                WHERE ativo = ?
                ORDER BY DATE(substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)) DESC,
                         TIME(tempo) DESC
            """, (ativo,))

        historico = [{"data": row[0], "tempo": row[1], "valor": row[2]} for row in cursor.fetchall()]
        
        conn.close()
        return historico

    except Exception as e:
        log_error(f"Erro ao ler histórico: {e}")
        return []

def gerar_texto_historico(historico, aux):
    log_debug("Agora no método gerar_texto_historico")
    #log_debug(f"VALOR DE AUX >> {aux} ⚠ ⚠ ⚠")

    if not historico:
        log_info("Histórico está vazio")
        return "• 00/00/0000\u2003R$ 0,00"
    
    if aux == "alert":
        #log_debug("🧪 Flag de alerta detectado")
        
        # Limita aos 10 primeiros registros
        historico = historico[:10]

        # Formata cada linha com data e valor
        linhas = [
            f'• {registro["data"][:-4] + registro["data"][-2:]}\u2003{formatar_reais(registro["valor"])}'
            for registro in historico
        ]

        log_info(f"Histórico de alerta gerado com {len(linhas)} registros")
        log_debug(f"🧪 Linhas antes: {linhas}")

        if len(linhas) > 1:
            if len(linhas) >= 4:
                linhas = [f'{linhas[0]}\u2003{linhas[1]}<br>{linhas[2]}\u2003{linhas[3]}']
            elif len(linhas) == 3:
                linhas = [f'{linhas[0]}\u2003{linhas[1]}<br>{linhas[2]}']
            else:
                linhas = [f'{linhas[0]}\u2003{linhas[1]}']
        else:
            log_info("Um registro encontrado")
            linhas = [linhas[0]]

        log_debug(f"🧪 Histórico de alerta gerado: {linhas}")
        return "<br>".join(linhas)
    else:
        linhas = [
            f'{registro["data"][:-5]} {registro["tempo"]}\u2003{formatar_reais(registro["valor"])}'
            for registro in historico
        ]

        log_debug("Histórico de ativo gerado")
        log_info("✅🖥️ Mostrando Tela")
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
        if ativos_raw:
            _ativos_cache = (state_fund_mapping, ativos)
            _ativos_cache_time = agora
            log_debug(f"Total de ativos carregados do banco: {len(ativos_raw)}")
            log_debug(f"state_fund_mapping gerado: {len(state_fund_mapping)}")
        else:
            log_warning("Nenhum ativo encontrado — cache não será atualizado.")
        return _ativos_cache

    except Exception as e:
        log_error(f"❌ Erro ao carregar ativos do SQLite: {e}")
        return ({}, [])

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
