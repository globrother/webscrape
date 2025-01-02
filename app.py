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
                    "type": "SSML",
                    "ssml": "<speak>Olá, Bem-vindo ao Echo Show!<break time='5s'/></speak>"
                },
                "directives": [
                    {
                        "type": "Alexa.Presentation.APL.RenderDocument",
                        "token": "welcomeToken",
                        "document": {
                            "type": "APL",
                            "version": "2024.3",
                            "license": "Copyright 2024 Amazon.com, Inc. or its affiliates. All Rights Reserved.\nSPDX-License-Identifier: LicenseRef-.amazon.com.-AmznSL-1.0\nLicensed under the Amazon Software License  http://aws.amazon.com/asl/",
                            "theme": "dark",
                            "import": [
                                {
                                    "name": "alexa-layouts",
                                    "version": "1.7.0"
                                }
                            ],
                            "mainTemplate": {
                                "parameters": [
                                    "payload"
                                ],
                                "items": [
                                    {
                                        "type": "Container",
                                        "height": "100vh",
                                        "items": [
                                            {
                                                "type": "AlexaBackground",
                                                "backgroundImageSource": "https://lh5.googleusercontent.com/d/1QZIOOt7ziy5avs2FklbSFoJxhUFpXFYf",
                                                "backgroundScale": "best-fill"
                                            },
                                            {
                                                "type": "Container",
                                                "height": "100vh",
                                                "width": "100vw",
                                                "items": [
                                                    {
                                                        "type": "AlexaHeader",
                                                        "headerTitle": "Atualizações Fundos Imobiliários - FIIs",
                                                        "headerAttributionImage": "${payload.longTextTemplateData.properties.logoUrl}"
                                                    },
                                                    {
                                                        "type": "ScrollView",
                                                        "paddingTop": "@spacingMedium",
                                                        "paddingBottom": "${@spacing3XLarge + @spacingXSmall}",
                                                        "paddingLeft": "@marginHorizontal",
                                                        "paddingRight": "@marginHorizontal",
                                                        "grow": 1,
                                                        "items": [
                                                            {
                                                                "type": "Text",
                                                                "text": "marcadores voz,",
                                                                "style": "textStyleDisplay4",
                                                                "textAlign": "left",
                                                                "speech": "${payload.longTextTemplateData.properties.plantInfoSpeech}",
                                                                "id": "financeContent"
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            "onMount": [
                                {
                                    "type": "SpeakItem",
                                    "componentId": "financeContent",
                                    "highlightMode": "line",
                                    "align": "center"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        return jsonify(response)
    return jsonify({})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
