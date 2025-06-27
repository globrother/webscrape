# =====::: FUNÇÃO UNICA PARA WEBSCRAPING DOS FIIs :::===== #

"""
===== ::: OBTENDO DADOS WEB DO FII XPML11 ::: ========================================
"""
import requests
from bs4 import BeautifulSoup
from utils import limpar_asset_name
from time import time
import grava_historico
import app
import json
import os
# import locale
# Configurar a localidade para o formato de número correto
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

#import logging
# Usar o logger para registrar mensagens
#logger = logging.getLogger(__name__)
#log_info('Função iniciada')

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
import logging
from log_utils import log_debug, log_info, log_warning, log_error

# =====================================================================

def get_dadosfii(fii):
    start = time()
    log_debug("Agora no método get_dadosfii")

    # Determina o tipo de ativo pelo sufixo
    if fii.endswith("11"):
        aux_url = "fundos-imobiliarios"
        tipo_ativo = "fii"
        tipo_ativo_str = "do Fundo"
    elif fii[-1] in ["3", "4", "5", "6", "7", "8"]:
        aux_url = "acoes"
        tipo_ativo = "acao"
        tipo_ativo_str = "da Ação"
    else:
        # Caso queira tratar outros tipos, adicione aqui
        aux_url = "acoes"  # padrão
        tipo_ativo = "acao"
        tipo_ativo_str = "da Ação"

    log_info(f"TIPO DE ATIVO:> {tipo_ativo}")

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
        # log_info("gobis Status Veja")
        proxies = {
            'http': 'http://89.117.22.218:8080',
            # Certifique-se de usar um proxy que suporte HTTPS
            'https': 'http://183.234.215.11:8443',
        }

        response = requests.get(url, headers=headers)
        log_info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            log_info(f"TIPO DE ATIVO 1:> {tipo_ativo}")

            if tipo_ativo == "fii":
                container_divs = soup.find_all('div', class_='container pb-7')
                tags = ['v-align-middle', 'value']
                # log_info("Veja antes do for")
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
                        break

                # Logo do Ativo (URL extraído automaticamente do site status invest)
                script_image_fii = soup.find_all(
                    'script', type='application/ld+json')

                if len(script_image_fii) > 2:
                    data = json.loads(script_image_fii[2].string)
                    # Acesse o campo da logo
                    logo_url = data.get('image', {}).get('url')
                    log_info(f"LOGO DO ATIVO: {logo_url}")

                # Verificação defensiva
                if not all([cota_fii, var_fii, dy_fii, pvp_fii, divpc_fii, logo_url]):
                    raise ValueError(
                        "Não foi possível extrair todos os dados necessários para o ativo.")

                log_info(f"\nTIPO DE ATIVO:> {tipo_ativo}\n")

            elif tipo_ativo == "acao":
                containers = soup.find_all('div', class_='container')
                container = containers[5]
                if not container:
                    log_info(f"Quantidade de containers encontrados: {len(container)}")
                    raise ValueError("Container principal NÃO encontrado para ação.")
                else:
                    log_info(f"HTML do container encontrado")

                # Valor atual
                valor_atual_tag = container.find(
                    'div', {'title': 'Valor atual do ativo'})
                cota_fii = valor_atual_tag.find(
                    'strong', class_='value').text.strip() if valor_atual_tag else None
                log_info(f"VALOR COTA:{cota_fii}")

                # Variação do dia
                variacao_tag = container.find(
                    'span', {'title': 'Variação do valor do ativo com base no dia anterior'})
                var_fii = variacao_tag.find(
                    'b').text.strip() if variacao_tag else None

                # Dividend Yield
                dy_tag = container.find(
                    'div', {'title': 'Dividend Yield com base nos últimos 12 meses'})
                dy_fii = dy_tag.find(
                    'strong', class_='value').text.strip() if dy_tag else None

                # P/VP
                pvp_tag = container.find('div', {
                                         'title': 'Facilita a análise e comparação da relação do preço de negociação de um ativo com seu VPA.'})
                pvp_fii = pvp_tag.find(
                    'strong', class_='value d-block lh-4 fs-4 fw-700').text.strip() if pvp_tag else None

                # Último rendimento (Proventos últimos 12 meses
                container_divpc = soup.find(
                    'div', class_='container pb-7 pt-7')
                divpc_tag = container_divpc.find(
                    'div', {'title': 'Soma total dos proventos provisionados'})
                divpc_fii = divpc_tag.find(
                    'strong', class_='value').text.strip() if divpc_tag else None
                log_info(f"VALOR DIV POR COTA:{divpc_fii}")
                divpc_fii = str(
                    round((float((divpc_fii).replace(',', '.'))), 2)).replace('.', ',')

                # Logo do Ativo (URL extraído automaticamente do site status invest)
                script_image = soup.find_all(
                    'script', type='application/ld+json')

                if len(script_image) > 2:
                    data = json.loads(script_image[2].string)
                    # Acessa o campo da logo
                    logo_url = data.get('image', {}).get('url')
                    log_info(f"LOGO DO ATIVO: {logo_url}")

                # Verificação defensiva
                if not all([cota_fii, var_fii, dy_fii, pvp_fii, divpc_fii, logo_url]):
                    raise ValueError(
                        "Não foi possível extrair todos os dados necessários para o ativo.")
        else:
            raise ConnectionError(
                f"Erro ao acessar o site: Status Code {response.status_code}")

        log_info(f"🔄 Processamento finalizado em {time() - start:.2f}s")

        arrow_fii = ""
        aux_fii = ""
        # var_fii = "1,27"  # apagar depois %%%%%%%%%%%%%%%
        if var_fii[0] == "-":
            arrow_fii = "&#x2B07;"
            aux_fii = "queda"
        else:
            arrow_fii = "&#x2B06;"
            aux_fii = "alta"

        variac_fii = (
            f"Houve {aux_fii} de <b>{var_fii}  {arrow_fii}</b> na cota do FII {fii.upper()} (hoje X ontem).")
        # variac_xpml11_aux = (f"<b>VAR {varxpml11}  {arrow_xpml}</b>")

        # log_info(f"Veja o valor de Variac_xpml:> {variac_xpml11}")
        card_fii = (
            f"Atualizações {tipo_ativo_str} {fii.upper()}:<br><br>"
            f"• Houve {aux_fii} de {var_fii} na cota<br>"
            f"• Valor atual da cota: R$ {cota_fii}<br>"
            f"• Dividend Yield: {dy_fii}%<br>"
            f"• P/VP: {pvp_fii}<br>"
            f"• Último rendimento: R$ {divpc_fii}."
        )
        # log_info(f"\n Veja o valor de Card:> {card_xpml11}\n")

        # Com caminho absoluto, parece não ser necessário: os.path.join(os.path.dirname(__file__)
        # nome_do_arquivo = os.path.join(os.path.dirname(__file__), 'historico_xpml.json') # com caminho absoluto
        # grava_historico.gravar_historico(nome_do_arquivo, f"R$ {xpml11_0}")
        # meu_historico = grava_historico.ler_historico("historico_xpml.json")
        # hist_text_xpml = grava_historico.gerar_texto_historico(meu_historico)
        # log_info("começar a chamar função de gravar Veja")
        sufixo = limpar_asset_name(fii)
        valor = f"R$ {cota_fii}"
        aux = "fund"
        grava_historico.gravar_historico(sufixo, valor)
        historico = grava_historico.ler_historico(sufixo)
        hist_text_fii = grava_historico.gerar_texto_historico(historico, aux)
        """hist_text_fii = {"dados_update": {
            "hist_text_fii": grava_historico.gerar_texto_historico(historico, aux)
            }
        }"""

        # print(f"Texto para Histórico: {hist_text_xpml}")

        # log_info(f"\nVeja os valores:> {hist_text_xpml}\n")
        return cota_fii, card_fii, variac_fii, hist_text_fii, logo_url

    except Exception as e:
        log_error(f"Ocorreu um erro em {fii}: {e}")
        return {"error": str(e)}, 500

# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
