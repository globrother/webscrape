from time import time
import requests
import logging
import os

API_URL = "https://graficoapi.duckdns.org:5000/chart"

CHART_API_KEY = os.getenv("CHART_API_KEY")

if CHART_API_KEY is None:
    raise ValueError("Erro: CHART_API_KEY não está definida como variável de ambiente!")

def requisitando_chart(ticker):
    start = time()
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CHART_API_KEY
    }
    data = {"ticker": ticker}

    response = requests.post(API_URL, json=data, headers=headers)

    logging.info(f"🔄 Processamento finalizado em {time() - start:.2f}s")

    if response.status_code == 200:
        return response.json().get("url", "")  # Retorna a url pronta - resposta da API 
    else:
        return {"error": f"Erro {response.status_code}: {response.text}"}
    

# 🔹 Exemplo de chamada
#resultado = requisitando_chart("BBAS3")
#print(resultado)
