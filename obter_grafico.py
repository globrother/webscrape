from dotenv import load_dotenv
from time import time
import requests
import os

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
import logging
from log_utils import log_debug, log_info, log_warning, log_error
# =====================================================================

API_URL = "https://graficoapi.duckdns.org:5000/chart"

CHART_API_KEY = os.getenv("CHART_API_KEY")

if CHART_API_KEY is None:
    raise ValueError("Erro: CHART_API_KEY não está definida como variável de ambiente!")

def requisitando_chart(ticker):
    start = time()
    log_debug("Agora em requisitando_chart")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CHART_API_KEY
    }
    data = {"ticker": ticker}

    try:
        response = requests.post(API_URL, json=data, headers=headers)

        log_info(f"⏱️​​ Processado em ⏳ {time() - start:.2f}s ⏳")

        if response.status_code == 200:
            return response.json().get("url", "")  # Retorna a url pronta - resposta da API 
        else:
            log_warning(f"Erro ao obter gráfico: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        log_error(f"Erro de conexão ao obter gráfico: {e}")
        return {"error": "Servidor de gráficos indisponível no momento."}
    

# 🔹 Exemplo de chamada
#resultado = requisitando_chart("BBAS3")
#print(resultado)
