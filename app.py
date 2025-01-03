import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("In LaunchRequestHandler")

        # O conteúdo APL do documento fornecido
        apl_document = {
            "type": "APL",
            "version": "2024.3",
            "import": [
                {
                    "name": "alexa-layouts",
                    "version": "1.7.0"
                }
            ],
            "mainTemplate": {
                "parameters": ["payload"],
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
            }
        }

        datasource = {
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
        }

        handler_input.response_builder.speak("Bem-vindo à skill de atualizações de fundos imobiliários!")
        handler_input.response_builder.add_directive(RenderDocumentDirective(token="mainToken", document=apl_document, datasources=datasource))
        
        return handler_input.response_builder.response

sb.add_request_handler(LaunchRequestHandler())

lambda_handler = sb.lambda_handler()
