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
    data = request.get_json()
    session = data.get('session', {})
    attributes = session.get('attributes', {})
        #data = request.get_json()
        #Timer(5, send_follow_up_response).start() # 5 segundos de intervalo
        #response_knri = alexa_knri11(get_element, request, requests, BeautifulSoup)
        #response_xpml = alexa_xpml11(get_element, request, requests, BeautifulSoup)
        #response_mxrf = alexa_mxrf11(get_element, request, requests, BeautifulSoup)

    if attributes.get('follow_up', False):
        # Se a sessão tiver o atributo de seguir, chama a função de resposta atrasada
        response = send_follow_up_response()
        with app.app_context():
            return response

    def delayed_response():
        # Redefinir a função de resposta atrasada dentro do contexto da aplicação
        with app.app_context():
            # Altere aqui para o cliente de teste chamando a mesma rota novamente
            test_client = app.test_client()
            test_client.post('/webscrape', json={"session": {"attributes": {"follow_up": True}}})
            #response = test_client.post('/webscrape', json={"session": {"attributes": {"follow_up": True}}})

    # Inicializa o temporizador para chamar a função após um atraso
    Timer(2, delayed_response).start()  # 5 segundos de intervalo
    print("teste de teste")
    return alexa_xpml11(get_element, request, requests, BeautifulSoup)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    