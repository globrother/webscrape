from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
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
        handler_input.response_builder.speak("Skill iniciada. Vamos começar com as telas.")
        return handler_input.response_builder.response

# Intenção para o IntentRequest
class IntentRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        bg_image_url = "https://lh5.googleusercontent.com/d/1QZIOOt7ziy5avs2FklbSFoJxhUFpXFYf"

        apl_document = {
            "type": "APL",
            "version": "1.4",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Sequence",
                        "scrollDirection": "horizontal",
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

        handler_input.response_builder.speak("Texto da Primeira Tela")
        handler_input.response_builder.add_directive({
            'type': 'Alexa.Presentation.APL.RenderDocument',
            'token': 'screen_token',
            'document': apl_document
        })

        return handler_input.response_builder.response

# Adicionar os handlers ao Skill Builder
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(IntentRequestHandler())

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
