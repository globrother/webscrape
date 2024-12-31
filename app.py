from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
from threading import Timer
from xpml11_response import send_follow_up_response, alexa_xpml11
from xpml11_response import alexa_xpml11
from xpml11 import get_element

# from xpml11 import get_element
# from xpml11_response import get_element

app = Flask(__name__)

@app.route('/webscrape', methods=['POST'])
def alexa():
        #data = request.get_json()
        #Timer(5, send_follow_up_response).start() # 5 segundos de intervalo
        #response_knri = alexa_knri11(get_element, request, requests, BeautifulSoup)
        #response_xpml = alexa_xpml11(get_element, request, requests, BeautifulSoup)
        #response_mxrf = alexa_mxrf11(get_element, request, requests, BeautifulSoup)

    def delayed_response():
        # Faz a chamada para a função de resposta atrasada
        with app.app_context():
            response = send_follow_up_response()
            print(response.get_json()) # Apenas para visualizar a resposta, pode ser removido

    # Inicializa o temporizador para chamar a função após um atraso
    Timer(5, delayed_response).start()  # 5 segundos de intervalo
    return alexa_xpml11(get_element, request, requests, BeautifulSoup)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    