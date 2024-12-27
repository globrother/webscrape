from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

app = Flask(__name__)

def get_element():
    url = 'https://statusinvest.com.br/fundos-imobiliarios/xpml11'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        container_divs = soup.find_all('div', class_='container pb-7')
        tags = ['value']
        
        xpml11_0 = dyxpml11_3 = pvpxpml11_6 = divpcxmpl11_16 = None
        
        for div in container_divs:
            for tag in tags:
                elements = div.find_all(class_=tag)
                if len(elements) > 4:
                    xpml11_0 = elements[0].text
                    dyxpml11_3 = elements[3].text
                    pvpxpml11_6 = elements[6].text
                    divpcxmpl11_16 = elements[15].text
                    break
        
        if not all([xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16]):
            raise ValueError("Unable to scrape all required elements.")
    else:
        raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")

    return xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16

APL_DOCUMENT_TOKEN = "documentToken"

@app.route('/webscrape', methods=['POST'])
def alexa():
    try:
        data = request.get_json()
        xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16 = get_element()

        marcadores_voz = f"• Valor atual da cota: R$ {xpml11_0}\n<break time='500ms'/>" \
                         f"• Dividend Yield: {dyxpml11_3}%\n<break time='500ms'/>" \
                         f"• P/VP: {pvpxpml11_6}\n<break time='500ms'/>" \
                         f"• Último rendimento: R$ {divpcxmpl11_16}<break time='500ms'/>"
        
        marcadores_card = f"• Valor atual da cota: R$ {xpml11_0}\n" \
                          f"• Dividend Yield: {dyxpml11_3}%\n" \
                          f"• P/VP: {pvpxpml11_6}\n" \
                          f"• Último rendimento: R$ {divpcxmpl11_16}"

        apl_document = {
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
                                "backgroundImageSource": "https://www.hashtagtreinamentos.com/wp-content/uploads/2022/02/Capa-Para-Dashboard-no-Power-BI-3.png",
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
                                                "text": marcadores_voz,
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

        datasources = {
            "longTextTemplateData": {
                "type": "object",
                "objectId": "longTextSample",
                "properties": {
                    "backgroundImage": {
                        "contentDescription": None,
                        "smallSourceUrl": None,
                        "largeSourceUrl": None,
                        "sources": [
                            {
                                "url": "https://www.hashtagtreinamentos.com/wp-content/uploads/2022/02/Capa-Para-Dashboard-no-Power-BI-3.png",
                                "size": "large"
                            }
                        ]
                    },
                    "title": "Atualizações Fundos Imobiliários - FIIs",
                    "textContent": {
                        "primaryText": {
                            "type": "PlainText",
                            "text": marcadores_card
                        }
                    },
                    "logoUrl": "https://d2o906d8ln7ui1.cloudfront.net/images/templates_v3/logo/logo-modern-botanical-white.png",
                    "plantSpeechSSML": f"<speak>{marcadores_voz}</speak>"
                },
                "transformers": [
                    {
                        "inputPath": "plantSpeechSSML",
                        "transformer": "ssmlToSpeech",
                        "outputName": "plantInfoSpeech"
                    }
                ]
            }
        }

        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": f"<speak>Atualizações do Fundo XPML onze \n{marcadores_voz}</speak>"
                },
                "card": {
                    "type": "Simple",
                    "title": "Obtendo de Status Invest",
                    "content": f"Atualizações do Fundo XPML11:\n{marcadores_card}"
                },
                "shouldEndSession": True
            },
            "directives": [
                {
                    "type": "Alexa.Presentation.APL.RenderDocument",
                    "token": APL_DOCUMENT_TOKEN,
                    "document": apl_document,
                    "datasources": datasources
                }
            ]
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
