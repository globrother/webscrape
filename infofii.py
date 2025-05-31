# =====::: FUNÇÃO UNICA PARA WEBSCRAPING DOS FIIs :::===== #

"""
===== ::: OBTENDO DADOS WEB DO FII XPML11 ::: ========================================
"""
import requests
from bs4 import BeautifulSoup
import grava_historico
import app
import os
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

import logging

# Usar o logger para registrar mensagens
logger = logging.getLogger(__name__)
logger.info('Função iniciada')


def get_dadosfii(fii):
    # Determina o tipo de ativo pelo sufixo
    if fii.endswith("11"):
        aux_url = "fundos-imobiliarios"
        tipo_ativo = "fii"
    elif fii[-1] in ["3", "4", "5", "6", "7", "8"]:
        aux_url = "acoes"
        tipo_ativo = "acao"
    else:
        # Caso queira tratar outros tipos, adicione aqui
        aux_url = "acoes"  # padrão
        tipo_ativo = "acao"

    try:
        # fii = "xpml11" # apagar depois
        url = "https://statusinvest.com.br/" + aux_url + "/" + fii
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Referer': 'https://statusinvest.com.br/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        # logging.info("gobis Status Veja")
        proxies = {
            'http': 'http://89.117.22.218:8080',
            # Certifique-se de usar um proxy que suporte HTTPS
            'https': 'http://183.234.215.11:8443',
        }

        response = requests.get(url, headers=headers)
        logger.info(f"\n Status Code: {response.status_code}\n")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            if tipo_ativo == "fii":
                container_divs = soup.find_all('div', class_='container pb-7')
                tags = ['v-align-middle', 'value']
                # logging.info("Veja antes do for")
                cota_fii = var_fii = dy_fii = pvp_fii = divpc_fii = None

                for div in container_divs:
                    # Encontra todos os elementos que têm as classes 'v-align-middle' ou 'value'
                    """
                    função de critério que está sendo passada para find_all.
                    Esta função anônima (lambda) verifica se a tag atual (tag)
                    possui a classe v-align-middle ou value em seu atributo class.
                    """
                    # elements = div.find_all(lambda tag: 'v-align-middle' in tag.get('class', []) or 'value' in tag.get('class', [])) #sem o uso de tags
                    # com o uso do dicionário tags.
                    elements = div.find_all(lambda tag: any(
                        t in tag.get('class', []) for t in tags))
                    if len(elements) > 4:
                        cota_fii = elements[0].text  # Valor atual da cota
                        # Variação da cota dia anterior
                        var_fii = elements[1].text
                        dy_fii = elements[4].text  # Dividend Yield
                        pvp_fii = elements[26].text  # P/VP
                        divpc_fii = str(
                            # Dividendo por cota
                            round((float((elements[39].text).replace(',', '.'))), 2)).replace('.', ',')
                        # logging.info("Veja dentro do for")
                        break
                # Verificação defensiva
                if not all([cota_fii, var_fii, dy_fii, pvp_fii, divpc_fii]):
                    raise ValueError(
                        "Não foi possível extrair todos os dados necessários para o ativo.")

        elif tipo_ativo == "acao":
            container_divs = soup.find_all('div', class_='container')
            tags = ['v-align-middle', 'value d-block lh-4 fs-4 fw-700']

            logging.info(f"Veja Conteiner Divs:{container_divs}")

            cota_fii = var_fii = dy_fii = pvp_fii = divpc_fii = None

            for div in container_divs:
                # Encontra todos os elementos que têm as classes 'v-align-middle' ou 'value'
                """
                função de critério que está sendo passada para find_all.
                Esta função anônima (lambda) verifica se a tag atual (tag)
                possui a classe v-align-middle ou value em seu atributo class.
                """
                # com o uso do dicionário tags.
                elements = div.find_all(lambda tag: any(
                    t in tag.get('class', []) for t in tags))

                logging.info(f"Veja Elementos:{elements}")

                if len(elements) > 4:
                    cota_fii = elements[0].text  # Valor atual da cota
                    # Variação da cota dia anterior
                    var_fii = "1,27"  # elements[1].text
                    dy_fii = elements[10].text  # Dividend Yield
                    pvp_fii = elements[13].text  # P/VP
                    divpc_fii = str(
                        # Dividendo por cota
                        round((float((elements[76].text).replace(',', '.'))), 2)).replace('.', ',')
                    # logging.info("Veja dentro do for")
                    break
            # Verificação defensiva
            if not all([cota_fii, var_fii, dy_fii, pvp_fii, divpc_fii]):
                raise ValueError(
                    "Não foi possível extrair todos os dados necessários para o ativo.")
        else:
            raise ConnectionError(
                f"Erro ao acessar o site: Status Code {response.status_code}")

        arrow_fii = ""
        aux_fii = ""
        var_fii = "1,27"  # apagar depois %%%%%%%%%%%%%%%
        if var_fii[0] == "-":
            arrow_fii = "&#x2B07;"
            aux_fii = "queda"
        else:
            arrow_fii = "&#x2B06;"
            aux_fii = "alta"

        variac_fii = (
            f"Houve {aux_fii} de <b>{var_fii}  {arrow_fii}</b> na cota do FII {fii.upper()} (hoje X ontem).")
        # variac_xpml11_aux = (f"<b>VAR {varxpml11}  {arrow_xpml}</b>")

        # logging.info(f"Veja o valor de Variac_xpml:> {variac_xpml11}")
        card_fii = (
            f"Atualizações do Fundo {fii.upper()}:<br><br>"
            f"• Houve {aux_fii} de {var_fii} na cota<br>"
            f"• Valor atual da cota: R$ {cota_fii}<br>"
            f"• Dividend Yield: {dy_fii}%<br>"
            f"• P/VP: {pvp_fii}<br>"
            f"• Último rendimento: R$ {divpc_fii}."
        )
        # logging.info(f"\n Veja o valor de Card:> {card_xpml11}\n")

        # Com caminho absoluto, parece não ser necessário: os.path.join(os.path.dirname(__file__)
        # nome_do_arquivo = os.path.join(os.path.dirname(__file__), 'historico_xpml.json') # com caminho absoluto
        # grava_historico.gravar_historico(nome_do_arquivo, f"R$ {xpml11_0}")
        # meu_historico = grava_historico.ler_historico("historico_xpml.json")
        # hist_text_xpml = grava_historico.gerar_texto_historico(meu_historico)
        # logging.info("começar a chamar função de gravar Veja")
        sufixo = app.remover_sufixo_numerico(fii)
        valor = f"R$ {cota_fii}"
        aux = "fund"
        grava_historico.gravar_historico(sufixo, valor)
        historico = grava_historico.ler_historico(sufixo)
        hist_text_fii = grava_historico.gerar_texto_historico(historico, aux)

        # print(f"Texto para Histórico: {hist_text_xpml}")

        # logging.info(f"\nVeja os valores:> {hist_text_xpml}\n")
        return cota_fii, card_fii, variac_fii, hist_text_fii

    except Exception as e:
        logging.info(f"\n Ocorreu um erro em {fii}: {e}\n")
        return {"error": str(e)}, 500


# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
