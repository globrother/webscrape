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
            f"• P/VP: {pvpxpml11_6}\n<break time='500ms'/>"
            f"• Último rendimento: R$ {divpcxmpl11_16}<break time='1s'/>"
        )
        
        card_xpml11 = (
            f"• Valor atual da cota: R$ {xpml11_0}<br>"
            f"• Dividend Yield: {dyxpml11_3}%<br>"
            f"• P/VP: {pvpxpml11_6}<br>"
            f"• Último rendimento: R$ {divpcxmpl11_16}"
        )
        
        # Verifica o tipo de solicitação da Alexa
        if request_data["request"]["type"] in ["LaunchRequest", "IntentRequest"]:
            response = {
                "version": "1.0",
                "response": {
                   # "outputSpeech": {
                   #     "type": "SSML",
                   #     "ssml": f"<speak> Atualizações do Fundo XPML onze \n{voz_xpml11}</speak>"
                   # },
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
                                },
                                "datasources": {
                                    "imageListData": {
                                        "type": "object",
                                        "objectId": "paginatedListSample",
                                        "title": "ATUALIÇÕES FUNDOS IMOBILIÁRIOS - FIIs",
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
                                },
                                "sources": {}
                            }
                        }
                    ]
                }
            }
            return jsonify(response)
        return jsonify("Ocorreu um erro com a solicitação.")
    except Exception as e:
        return jsonify({"error": str(e)}), 500