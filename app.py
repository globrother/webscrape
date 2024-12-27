from flask import Flask, request, jsonify
import ask_sdk_core as ask_sdk
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_element():
    url = 'https://statusinvest.com.br/fundos-imobiliarios/xpml11'
    # Definindo um header User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    # Verificando o status da resposta
    if response.status_code == 200:
        # Criando um objeto BeautifulSoup a partir do conteúdo HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # Encontrando a tag <div> com a classe "container pb-7"
        container_divs = soup.find_all('div', class_='container pb-7')
        # Tags que você deseja capturar
        tags = ['value'] # Pode adicionar mais tags se necessário
        
        xpml11_0 = dyxpml11_3 = pvpxpml11_6 = divpcxmpl11_16 = None
        
        # Iterando sobre cada <div> encontrado
        for div in container_divs:
            for tag in tags:
                elements = div.find_all(class_=tag)
                # Garantindo que há pelo menos 5 elementos na lista
                if len(elements) > 4:
                    xpml11_0 = elements[0].text
                    dyxpml11_3 = elements[3].text
                    pvpxpml11_6 = elements[6].text
                    divpcxmpl11_16 = elements[15].text
                    break
        # Tratamento de Erros: Verifica se todos os elementos foram encontrados
        if not all([xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16]):
            raise ValueError("Unable to scrape all required elements.")
    else:
        raise ConnectionError(f"Erro ao acessar o site: Status Code {response.status_code}")

    return xpml11_0, dyxpml11_3, pvpxpml11_6, divpcxmpl11_16

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

        # Documento APL para a imagem de fundo
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
                                                "text": marcadores_card,
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
                    "token": "welcomeDocument",
                    "document": apl_document
                }
            ]
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
