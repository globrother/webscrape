from flask import Flask, request, jsonify
import json
import ask_sdk_core as ask_sdk
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_element():
    # Definindo um header User-Agent
    url = 'https://statusinvest.com.br/fundos-imobiliarios/xpml11'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    # Verificando o status da resposta
    if response.status_code == 200:
        # Criando um objeto BeautifulSoup a partir do conteúdo HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrando a tag <div> com a classe "container pb-7"
        container_divs = soup.find_all('div', class_='container pb-7')
        
        # Tags que você deseja capturar
        tags = ['value']  # Pode adicionar mais tags se necessário
        
        # Iterando sobre cada <div> encontrado
        for div in container_divs:
            for tag in tags:
                elements = div.find_all(class_=tag)
                # Garantindo que há pelo menos 5 elementos na lista
                if len(elements) > 4:
                    xpml11_0 = elements[0].text
                    dyxpml11_3 = elements[3].text
                    pvpxpml11_6 = elements[6].text
                    divpcxmpl11_16 = elements[15].text
                    # valores_xpml11 = {{elements[0].text}, {elements[3].text},
                    #    {elements[6].text}, {elements[16].text}}
                    break
                for element in elements:
                    print(xpml11_0)
                    print(dyxpml11_3)
                    print(pvpxpml11_6)
                    print(divpcxmpl11_16)
    else:
        print(f"Erro ao acessar o site: Status Code {response.status_code}")

    return xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16

@app.route('/webscrape', methods=['POST'])
def alexa():
    data = request.get_json()
    xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16 = get_element()

    marcadores = f"• Valor atual da cota: {xpml11_0}\n• Dividend Yield (12): {dyxpml11_3}\n• P/VP: {pvpxpml11_6}\n• Último rendimento: {divpcxmpl11_16}"

    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": f"\n{marcadores}"
            },
            "card": {
                "type": "Simple",
                "title": "Obtendo de Brasil Indicadores",
                "content": f"\n{marcadores}"
            },
            "shouldEndSession": True
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
