from flask import Flask, request, jsonify
import json
import requests
from bs4 import BeautifulSoup
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
from threading import Timer
from xpml11_response import alexa_xpml11
from xpml11 import get_element

# from xpml11 import get_element
# from xpml11_response import get_element

app = Flask(__name__)

@app.route("/webscrape", methods=["POST"])
def handle_request():
    
    return alexa_xpml11(get_element, request, requests, BeautifulSoup)

if __name__ == '__main__':
    app.run(debug=True, port=5000)