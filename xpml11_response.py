"""
===== ::: CONSTRUINDO RESPOSTA PARA ALEXA ::: ========================================
"""
from flask import jsonify
#import time
#from xpml11 import get_element

def alexa_xpml11(json, get_element, request, requests, BeautifulSoup):
    try:
        #data = request.get_json()
        request_data = request.get_json()

        # Adiciona instrução de depuração para imprimir o conteúdo da solicitação
        # print("Request Data:", json.dumps(request_data, indent=2))

        xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16 = get_element(requests, BeautifulSoup)
        
        voz_xpml11 = (
            f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>"
            f"• Dividend Yield: {dyxpml11_3}%\n<break time='500ms'/>"
            f"• PVP: {pvpxpml11_6}\n<break time='500ms'/>"
            f"• Último rendimento: R$ {divpcxmpl11_16}<break time='1s'/>"
        )
        
        card_xpml11 = (
            f"• Valor atual da cota: R$ {xpml11_0}<br>"
            f"• Dividend Yield: {dyxpml11_3}%<br>"
            f"• P/VP: {pvpxpml11_6}<br>"
            f"• Último rendimento: R$ {divpcxmpl11_16}"
        )

        voz_teste1 = (
            f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>"
        )

        card_teste1 = (
            f"• Valor atual da cota: R$ {xpml11_0}<br>"
        )

        # Verifica o tipo de solicitação da Alexa
        if request_data["request"]["type"] in ["LaunchRequest", "IntentRequest"]:
            response = {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "SSML",
                        "ssml": f"<speak> Atualizações do Fundo XPML onze \n{voz_xpml11}</speak>"
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
                                                                    "text": f"Atualizações do Fundo XPML11:<br><br>{card_xpml11}",
                                                                    "style": "textStyleDisplay4",
                                                                    "textAlign": "left",
                                                                    "speech": "${payload.longTextTemplateData.properties.plantInfoSpeech}",
                                                                    "id": "financeContent-xpml"
                                                                },
                                                                {
                                                                    "type": "Text",
                                                                    "text": f"{card_teste1}",
                                                                    "style": "textStyleDisplay4",
                                                                    "textAlign": "left",
                                                                    "id": "financeContent-teste1",
                                                                    "display": "none"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                "commands": [
                                    {
                                        "type": "Sequential",
                                        "commands": [
                                            {
                                                "type": "SpeakItem",
                                                "componentId": "financeContent-xpml",
                                                "highlightMode": "line",
                                                "align": "center"
                                            },
                                            {
                                                "type": "SetValue",
                                                "componentId": "financeContent-teste1",
                                                "property": "display",
                                                "value": "normal"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
            return jsonify(response)
        return jsonify("Ocorreu um erro com a solicitação.")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        
        """
        response = {
            "version": "1.0",
            "sessionAttributes":{
                 "follow_up": True },
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": f"<speak> Atualizações do Fundo XPML onze \n{voz_xpml11}</speak>"
                },
                "card": {
                    "type": "Simple",
                    "title": "Obtendo de Status Invest",
                    "content": f"Atualizações do Fundo XPML11:\n\n{card_xpml11}"
                },
                "shouldEndSession": False # Mantem a sessão aberta para a próxima atualização
            }
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_follow_up_response():
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Aqui está a próxima atualização."
            },
            "card": {
                "type": "Simple",
                "title": "Mais Informações do Fundo XPML11",
                "content": "Informações adicionais aqui."
            },
            "shouldEndSession": True  # Fecha a sessão após a resposta
        }
    }
    return response

    
def send_follow_up_response():
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Aqui está a próxima atualização."
            },
            "card": {
                "type": "Simple",
                "title": "Mais Informações do Fundo XPML11",
                "content": "Informações adicionais aqui."
            },
            "shouldEndSession": True  # Fecha a sessão após a resposta
        }
    }
    return jsonify(response)
"""