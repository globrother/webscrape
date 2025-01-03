from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractRequestInterceptor
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
import logging

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sb = SkillBuilder()

# Intenção para o LaunchRequest
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.debug("LaunchRequestHandler chamado")
        handler_input.response_builder.speak("Skill iniciada. Vamos começar com as telas.")
        return handler_input.response_builder.response

# Intenção para o TestIntent
class TestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TestIntent")(handler_input)

    def handle(self, handler_input):
        logger.debug("TestIntentHandler chamado")
        bg_image_url = "https://lh5.googleusercontent.com/d/1QZIOOt7ziy5avs2FklbSFoJxhUFpXFYf"

        apl_document = {
            "type": "APL",
            "version": "1.4",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Container",
                        "items": [
                            {
                                "type": "Image",
                                "source": bg_image_url,
                                "width": "100%",
                                "height": "100%"
                            },
                            {
                                "type": "Text",
                                "text": "Texto da Primeira Tela",
                                "style": "textStylePrimary1",
                                "id": "texto_da_primeira_tela"
                            }
                        ]
                    }
                ]
            }
        }

        handler_input.response_builder.speak("Texto da Primeira Tela").add_directive(
            RenderDocumentDirective(
                token="screen_token",
                document=apl_document
            )
        )

        return handler_input.response_builder.response

# Logs adicionais para capturar detalhes específicos
class LoggingRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.debug(f"Interceptando pedido: {handler_input.request_envelope.request}")

# Adicionar os handlers ao Skill Builder
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TestIntentHandler())  # Adicionar o handler explícito para TestIntent
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
