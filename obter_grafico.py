import requests
import os

API_URL = "http://204.216.158.137:8000/screenshot"
CHART_API_KEY = os.getenv("CHART_API_KEY")

def requisitando_chart(ticker):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": CHART_API_KEY
    }
    data = {"ticker": ticker}

    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()  # Retorna a resposta da API
    else:
        return {"error": f"Erro {response.status_code}: {response.text}"}

# 🔹 Exemplo de chamada
#resultado = requisitando_chart("BBAS3")
#print(resultado)
