import logging
import requests
from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
sb = SkillBuilder()

# Endpoint da API
ENDPOINT = "https://alexawebscrape.onrender.com/webscrape"

# Handlers da skill Alexa
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("In LaunchRequestHandler")

        try:
            response = requests.get(f"{ENDPOINT}/launch")
            response.raise_for_status()
            logger.info(f"HTTP Response: {response.text}")
            data = response.json()
            logger.info(f"Data: {data}")
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            data = {}

        apl_document = data.get("document", {})
        datasource = data.get("datasources", {})

        handler_input.response_builder.speak("Bem-vindo à skill de atualizações de fundos imobiliários!")
        if apl_document and datasource:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(token="mainToken", document=apl_document, datasources=datasource)
            )
        else:
            handler_input.response_builder.speak("Desculpe, algo deu errado ao tentar obter os dados.")

        return handler_input.response_builder.response

class IntentRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = handler_input.request_envelope.request.intent.name
        logger.info(f"In IntentRequestHandler with intent: {intent_name}")

        try:
            response = requests.get(f"{ENDPOINT}/intent?name={intent_name}")
            response.raise_for_status()
            logger.info(f"HTTP Response: {response.text}")
            data = response.json()
            logger.info(f"Data: {data}")
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            data = {}

        speech_text = data.get("speech_text", "Desculpe, eu não entendo essa solicitação.")
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)

        return handler_input.response_builder.response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(IntentRequestHandler())

lambda_handler = sb.lambda_handler()

# Definindo a rota e a função para lidar com a requisição
@app.route("/webscrape", methods=["POST"])
def handle_request():
    return jsonify({
        "document": {
            "type": "APL",
            "version": "2024.3",
            "import": [
                {
                    "name": "alexa-layouts",
                    "version": "1.7.0"
                }
            ],
            "mainTemplate": {
                "parameters": ["payload"],
                "items": [
                    {
                        "type": "AlexaPaginatedList",
                        "id": "paginatedList",
                        "headerTitle": "${payload.imageListData.title}",
                        "headerBackButton": True,
                        "headerAttributionImage": "${payload.imageListData.logoUrl}",
                        "backgroundBlur": False,
                        "backgroundColorOverlay": False,
                        "backgroundScale": "best-fill",
                        "backgroundAlign": "bottom",
                        "theme": "dark",
                        "listItems": "${payload.imageListData.listItems}"
                    }
                ]
            }
        },
        "datasources": {
            "imageListData": {
                "type": "object",
                "objectId": "paginatedListSample",
                "title": "ATUALIZAÇÕES FUNDOS IMOBILIÁRIOS - FIIs",
                "listItems": [
                    {
                        "primaryText": "Fundos Imobiliários",
                        "secondaryText": "5 itens",
                        "imageSource": "https://lh5.googleusercontent.com/d/1QZIOOt7ziy5avs2FklbSFoJxhUFpXFYf"
                    },
                    {
                        "primaryText": "Fundo XML11",
                        "secondaryText": "5 items",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark2.png"
                    },
                    {
                        "primaryText": "Fundo MXRF11",
                        "secondaryText": "5 items",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark3.png"
                    },
                    {
                        "primaryText": "Fundo KNRI11",
                        "secondaryText": "5 items",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark4.png"
                    },
                    {
                        "primaryText": "Fundo XPLG11",
                        "secondaryText": "5 items",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark5.png"
                    }
                ],
                "logoUrl": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/logo/logo-modern-botanical-white.png"
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
