from time import time
import requests
from chart_server import gerar_grafico
import os

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
import logging
from log_utils import log_debug, log_info, log_warning, log_error
# =====================================================================

# ====================:: CONFIGURAÇÕES TOKENS ::=======================
SECRET_TOKEN = os.getenv("API_KEY")
# =====================================================================

# 🔹 Domínio público HTTPS
BASE_URL = "https://graficoapi.duckdns.org/static"

headers = {
        "Content-Type": "application/json",
        "x-api-key": SECRET_TOKEN
    }

def requisitando_chart(ticker):
    start = time()
    log_debug("Agora em requisitando_chart")
    try:
        caminho_imagem = gerar_grafico(ticker)
        log_info(f"Caminho da Imagem:{caminho_imagem}")
        
        if not caminho_imagem or not os.path.exists(caminho_imagem):
            raise FileNotFoundError("Gráfico não foi gerado ou não existe.")
        
        # 🔹 Extrai o nome do arquivo
        nome_arquivo = os.path.basename(caminho_imagem)
        
        # 🔹 Monta a URL pública
        url_publica = f"{BASE_URL}/{nome_arquivo}"
        
        # 🔐 Verifica se a URL está acessível com a chave
        headers = {"x-api-key": SECRET_TOKEN}
        response = requests.get(url_publica, headers=headers)

        if response.status_code != 200:
            raise ConnectionError(f"Falha ao acessar o gráfico: {response.status_code}")
        
        log_info(f"⏱️​​ Processado em ⏳ {time() - start:.2f}s ⏳")
        return url_publica  # Retorna o caminho local do arquivo gerado
    except Exception as e:
        log_error(f"Erro ao gerar gráfico: {e}")
        return None
    
# 🔹 Exemplo de chamada
# resultado = requisitando_chart("BBAS3")
# print(resultado)