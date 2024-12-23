from flask import Flask, jsonify, request
# ... (resto das importações)

app = Flask(__name__)
# ... (resto do código)

@app.route("/", methods=['POST']) # Apenas POST
def alexa_endpoint():
    # ... (código para processar a requisição da Alexa)

if __name__ == '__main__':
    app.run(debug=True, port=8080)