# import locale
import json
import logging
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import (
    is_request_type, get_supported_interfaces, is_intent_name)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SendEventCommand)
from typing import Dict, Any
from xpml11 import get_xpml
from knri11 import get_knri

app = Flask(__name__)

# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')


def _load_apl_document(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # print(f"Content of {file_path}: {content}")
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    
card_xpml11, variac_xpml11, hist_text_xpml  = get_xpml(requests, BeautifulSoup) # ,_ significa que a variável variac_xpml11 não será utilizada
#_, variac_xpml11 = get_xpml(requests, BeautifulSoup) # _, significa que a variável card_xpml11 não será utilizada 
card_knri11, variac_knri11, hist_text_knri = get_knri(requests, BeautifulSoup)
#_, variac_knri11 = get_knri(requests, BeautifulSoup) # _, significa que a variável card_knri11 não será utilizada

# def aux_json(card_xpml11, card_knri11):
doc_apl_xpml = "apl_xpml.json"
apl_document_xpml = _load_apl_document(doc_apl_xpml)
doc_apl_knri = "apl_knri.json"
apl_document_knri = _load_apl_document(doc_apl_knri)
apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['text'] = card_xpml11
apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_xpml11
apl_document_xpml['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_xpml
apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][0]['text'] = card_knri11
apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][0]['headerSubtitle'] = variac_knri11
apl_document_knri['mainTemplate']['items'][0]['items'][1]['items'][1]['items'][1]['items'][1]['text'] = hist_text_knri


voz_xpml11 = card_xpml11.replace('<br>', '\n<break time="500ms"/>')

voz_knri11 = card_knri11.replace(
    '<br>', '\n<break time="500ms"/>').replace('KNRI11', 'K N R I onze')

class LaunchRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # logging.debug(f"Handling LaunchRequest with card_xpml11: {self.card_xpml11}")
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="textDisplayToken1",
                document=apl_document_xpml
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="textDisplayToken1",
                commands=[
                    SendEventCommand(
                        arguments=["showSecondScreen"], delay=0)
                ]
            )

        ).speak(f"Aqui está as atualizações dos fundos:<break time='1s'/>\n{voz_xpml11}")

        return handler_input.response_builder.response


class ShowSecondScreenHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input) and \
            handler_input.request_envelope.request.arguments == [
                "showSecondScreen"]

    def handle(self, handler_input):
        # _, apl_document_knri = aux_json(self.card_xpml11, self.card_knri11)
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="textDisplayToken2",
                document=apl_document_knri
            )
        ).speak(f"<break time='1s'/>\n{voz_knri11}")
        return handler_input.response_builder.response


class CatchAllRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return True
    """Aqui eu peço o encerramento da skill caso nenhum handler seja capaz de lidar com a solicitação.
    dessa forma ao tocar sobre o botão de voltar, a skill será encerrada, pois não implementei nenhum
    método para essa solicitação."""

    def handle(self, handler_input):
        # return handler_input.response_builder.speak("Desculpe, não consegui entender a solicitação.").response
        return handler_input.response_builder.speak("Encerrando a skill. Até a próxima!").set_should_end_session(True).response


@app.route('/webscrape', methods=['POST'])
def webhook():
    data = request.get_json()

    # Defina card_xpml11 aqui dentro do contexto da aplicação Flask
    card_xpml11 = get_xpml(requests, BeautifulSoup)
    card_knri11 = get_knri(requests, BeautifulSoup)

    # Inicialize o SkillBuilder
    sb = SkillBuilder()

    # Inicialize os handlers com card_xpml11
    launch_request_handler = LaunchRequestHandler()
    show_second_screen_handler = ShowSecondScreenHandler()
    catch_all_request_handler = CatchAllRequestHandler()
    # go_back_handler = GoBackHandler()

    # Adicione os handlers ao SkillBuilder
    sb.add_request_handler(launch_request_handler)
    sb.add_request_handler(show_second_screen_handler)
    sb.add_request_handler(catch_all_request_handler)
    # sb.add_request_handler(go_back_handler)

    # Gere a resposta
    response = sb.lambda_handler()(data, None)
    return jsonify(response)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG) # Habilita debug logging
    app.run(debug=True, port=5000)
