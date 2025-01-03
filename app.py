from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractRequestInterceptor
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective, ExecuteCommandsDirective, AutoPageCommand
import logging

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sb = SkillBuilder()

# Intenção para o LaunchIntent
class LaunchIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LaunchIntent")(handler_input)

    def handle(self, handler_input):
        logger.debug("LaunchIntentHandler chamado")
        bg_image_url = "https://lh5.googleusercontent.com/d/1QZIOOt7ziy5avs2FklbSFoJxhUFpXFYf"

        apl_document = {
            "type": "APL",
            "version": "1.4",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Sequence",
                        "scrollDirection": "horizontal",
                        "id": "SequenceComponent",
                        "data": [
                            {"bgImage": bg_image_url, "text": "Texto da Primeira Tela"},
                            {"bgImage": bg_image_url, "text": "Texto da Segunda Tela"},
                            {"bgImage": bg_image_url, "text": "Texto da Terceira Tela"}
                        ],
                        "items": [
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "Image",
                                        "source": "${data.bgImage}",
                                        "width": "100%",
                                        "height": "100%"
                                    },
                                    {
                                        "type": "Text",
                                        "text": "${data.text}",
                                        "style": "textStylePrimary1"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        apl_datasources = {
            "imageListData": {
                "type": "object",
                "objectId": "paginatedListSample",
                "title": "ATUALIZAÇÕES FUNDOS IMOBILIÁRIOS - FIIs",
                "listItems": [
                    {
                        "primaryText": "Fundos Imobiliários",
                        "secondaryText": "5 itens",
                        "imageSource": bg_image_url
                    },
                    {
                        "primaryText": "Fundo XML11",
                        "secondaryText": "5 itens",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark2.png"
                    },
                    {
                        "primaryText": "Fundo MXRF11",
                        "secondaryText": "5 itens",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark3.png"
                    },
                    {
                        "primaryText": "Fundo KNRI11",
                        "secondaryText": "5 itens",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark4.png"
                    },
                    {
                        "primaryText": "Fundo XPLG11",
                        "secondaryText": "5 itens",
                        "imageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/paginatedlist/PaginatedList_Dark5.png"
                    }
                ],
                "logoUrl": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/logo/logo-modern-botanical-white.png"
            }
        }

        # Comando para mudar as telas automaticamente
        commands = [
            AutoPageCommand(
                component_id="SequenceComponent",
                duration=5000  # Troca a cada 5 segundos
            )
        ]

        handler_input.response_builder.speak("Texto da Primeira Tela").add_directive(
            RenderDocumentDirective(
                token="screen_token",
                document=apl_document,
                datasources=apl_datasources
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="screen_token",
                commands=commands
            )
        )

        return handler_input.response_builder.response

# Handler para SessionEndedRequest
class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.debug("SessionEndedRequestHandler chamado")
        return handler_input.response_builder.response

# Logs adicionais para capturar detalhes específicos
class LoggingRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.debug(f"Interceptando pedido: {handler_input.request_envelope.request}")

# Adicionar os handlers ao Skill Builder
sb.add_request_handler(LaunchIntentHandler())  # Adicionar o handler explícito para LaunchIntent
sb.add_request_handler(SessionEndedRequestHandler())  # Adicionar o handler para SessionEndedRequest
sb.add_global_request_interceptor(LoggingRequestInterceptor())  # Adicionar o interceptor de logging

@app.route('/webscrape', methods=['POST'])
def alexa_skill():
    logger.debug("Request JSON: %s", request.json)
    try:
        response = sb.lambda_handler()(request.json, None)
        logger.debug("Response: %s", response)
        return jsonify(response)
    except Exception as e:
        logger.error("Exception: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
