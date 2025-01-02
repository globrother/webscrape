from flask import Flask, request, jsonify
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
import json

app = Flask(__name__)

@app.route("/webscrape", methods=["POST"])
def handle_request():
    request_data = request.get_json()
    
    # Verifica o tipo de solicitação da Alexa
    if request_data["request"]["type"] == "LaunchRequest":
        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Olá, Bem-vindo ao Echo Show!"
                },
                "directives": [
                    {
                        "type": "Alexa.Presentation.APL.RenderDocument",
                        "token": "welcomeToken",
                        "document": {
                            "type": "APL",
                            "version": "1.4",
                            "mainTemplate": {
                                "items": [
                                    {
                                        "type": "Container",
                                        "items": [
                                            {
                                                "type": "Image",
                                                "source": "https://corhexa.com/png/1280x800/f57837",
                                                "width": "100vw",
                                                "height": "100vh"
                                            },
                                            {
                                                "type": "Text",
                                                "text": "Olá, Bem-vindo ao Echo Show!",
                                                "fontSize": "40dp",
                                                "color": "white",
                                                "position": "absolute",
                                                "top": "50vh",
                                                "left": "0vw",
                                                "transform": "translate(-50%, -50%)"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                ],
                "shouldEndSession": True
            }
        }
        return jsonify(response)
    return jsonify({})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
