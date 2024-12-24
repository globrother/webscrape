from flask import Flask, request, jsonify
import json
import ask_sdk_core as ask_sdk
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_resultado():
    response = requests.get(
        'https://brasilindicadores.com.br/cdi/').content
    soup = BeautifulSoup(response, 'html.parser')
    #print(soup.text)
    
    # Encontrar o <div> com a classe específica
    myelement = soup.find('div', class_="card-body-texto")
    print(myelement.text)
    resultado = myelement.text if myelement else 'Não foi possível obter a hora'
    return resultado

@app.route('/webscrape', methods=['POST'])
def alexa():
    data = request.get_json()
    resultado = get_resultado()
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": f"Olá! O valor do CDI é {resultado}."
            },
            "card": {
                "type": "Simple",
                "title": "Hora Atual de Brasília",
                "content": f"O valor do CDI é {resultado}."
            },
            "shouldEndSession": True
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
