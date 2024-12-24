import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def handle_alexa_request(request_data):
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

    return response

@app.route('/alexa', methods=['POST'])
def alexa_skill():
    try:
        request_data = request.json
        print(f"Received request data: {request_data}")
        response = handle_alexa_request(request_data)
        
        endpoint = "https://alexawebscrape.onrender.com/"
        headers = {
            "Content-Type": "application/json"
        }

        post_response = requests.post(endpoint, json=response, headers=headers)
        print(f"Response from endpoint: {post_response.json()}")
        return jsonify(post_response.json())
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
