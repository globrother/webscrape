from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/alexa', methods=['POST'])
def alexa_skill():
    data = request.json
    response_text = "Olá, esta é uma resposta simples em português."

    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response_text
            },
            "shouldEndSession": True
        }
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
