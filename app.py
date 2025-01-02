from flask import Flask, request, jsonify
import json
import requests
from bs4 import BeautifulSoup
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective)
import logging
#from threading import Timer
#from xpml11_response import alexa_xpml11
#from xpml11 import get_element

# from xpml11 import get_element
# from xpml11_response import get_element

from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective)
from ask_sdk_model.ui import SimpleCard
import logging

from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective)
from ask_sdk_model.ui import SimpleCard
import logging

app = Flask(__name__)
sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.info("LaunchRequestHandler can_handle invoked")
        return handler_input.request_envelope.request.object_type == "LaunchRequest"

    def handle(self, handler_input):
        logger.info("LaunchRequestHandler handle invoked")
        speech_text = "Bem-vindo! Aqui estão os cartões."
        
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
                                "source": "https://lh5.googleusercontent.com/d/1QZIOOt7ziy5avs2FklbSFoJxhUFpXFYf",
                                "width": "100vw",
                                "height": "100vh"
                            },
                            {
                                "type": "Text",
                                "id": "textComponent",
                                "text": "Primeiro cartão",
                                "fontSize": "50dp",
                                "color": "#FFFFFF",
                                "textAlign": "center",
                                "textAlignVertical": "center"
                            }
                        ]
                    }
                ]
            }
        }
        
        apl_command = [
            {
                "type": "SpeakItem",
                "componentId": "textComponent",
                "highlightMode": "line"
            },
            {
                "type": "SetValue",
                "componentId": "textComponent",
                "property": "text",
                "value": "Segundo cartão"
            },
            {
                "type": "SpeakItem",
                "componentId": "textComponent",
                "highlightMode": "line"
            }
        ]

        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="uniqueToken",
                document=apl_document
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="uniqueToken",
                commands=apl_command
            )
        ).speak(speech_text).set_card(SimpleCard("Cartões", speech_text)).set_should_end_session(False)
        
        return handler_input.response_builder.response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type == "IntentRequest"

    def handle(self, handler_input):
        speech_text = "Desculpe, não entendi sua solicitação. Você pode tentar novamente?"
        
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        
        return handler_input.response_builder.response

class ErrorHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speech_text = "Desculpe, ocorreu um erro ao processar sua solicitação."
        
        handler_input.response_builder.speak(speech_text).set_should_end_session(True)
        
        return handler_input.response_builder.response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_exception_handler(ErrorHandler())

@app.route("/webscrape", methods=['POST'])
def webscrape():
    logger.info("Received request at /webscrape endpoint")
    request_body = request.json
    response = sb.lambda_handler()(request_body, None)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
