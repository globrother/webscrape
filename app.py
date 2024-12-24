from flask import Flask, request, jsonify
import json
import ask_sdk_core as ask_sdk

app = Flask(__name__)

@app.route('/webscrape', methods=['POST'])
def alexa():
    data = request.get_json()
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Olá! Esta é uma resposta de teste da sua skill Alexa."
            },
            "card": {
                "type": "Simple",
                "title": "Teste de Skill Alexa",
                "content": "Esta é uma resposta de teste da sua skill Alexa."
            },
            "shouldEndSession": True
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
