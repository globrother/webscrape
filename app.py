import requests

def send_alexa_request():
    endpoint = "https://alexawebscrape.onrender.com/"
    response_text = "Olá, esta é uma resposta simples em português."

    response_data = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response_text
            },
            "shouldEndSession": True
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(endpoint, json=response_data, headers=headers)
    return response.json()

if __name__ == '__main__':
    result = send_alexa_request()
    print(result)
