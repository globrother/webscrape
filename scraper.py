# scraper.py

from utils import state_asset_mapping
from utils import _load_apl_document, limpar_asset_name, comparador
from infofii import get_dadosfii
import grava_historico
import obter_grafico
import time

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
from log_utils import log_debug, log_info, log_warning, log_error
# =====================================================================
log_info("Agora em web_scrape()")
# ===============::::: SESSÃO WEBSCRAPE :::::===============
def web_scrape(fundo):
    log_info("Agora em web_scrape()")
    start = time.time()
    timeout = False
    # extrai os caracteres numéricos de fundo
    fundo_fii = limpar_asset_name(fundo)
    doc_apl = "apl_fii.json"  # f"apl_{fundo_fii}.json"
    # Carregar APL padrão de exibiçaõ dos fundos
    apl_document = _load_apl_document(doc_apl)
    log_debug(f"Tentando carregar APL: {doc_apl}")
    #log_debug(f"Resultado do apl_document: {apl_document}")

    
    # Adiciona a geração do texto do histórico de alertas
    sufixo = f"alert:{fundo_fii}" #f"alert_value_{fundo_fii}"
    historico = grava_historico.ler_historico(sufixo)
    aux = "alert"
    hist_alert = grava_historico.gerar_texto_historico(historico, aux)
    # log_info(f"\n Recuperando hist_alert_xpml da sessão: {hist_alert} \n")

    fii = fundo
    #log_info(f"valor de fii: {fii}")
    
    # 🔹 Obtendo Url do Gráfico
    url_grafico = obter_grafico.requisitando_chart(fii)
    #timestamp = int(time.time() // 3600)  # 🔹 Atualiza a cada hora
    
    if url_grafico is None:
        raise ValueError("url_grafico está None. Verifique a origem dos dados.")
    #log_info(f"URL do Gráfico: {url_grafico}")
    
    limite_timeout = 3.5
    
    if time.time() - start > limite_timeout:
        timeout = True
        # Retorne dados parciais ou vazios
        return {}, None, None, None, None, None, timeout

    # Lista de links de imagens de planos de fundo
    background_images = [
        "https://lh5.googleusercontent.com/d/1-A_3cMBv-0E1o4RAzMjf8j31q2IKj3e5",
        "https://lh5.googleusercontent.com/d/1-9P8D-AJCsH6-S2ZSmSURlT8aGDGcgV4",
        "https://lh5.googleusercontent.com/d/1-Eeo6Kr7MQQ1MTAtFnrYynkaqaDrU_LW",
        "https://lh5.googleusercontent.com/d/1-8MRaljDqQKt6IlhTtlcKcEsFKO6psqF",
        "https://lh5.googleusercontent.com/d/1-Eeo6Kr7MQQ1MTAtFnrYynkaqaDrU_LW",
        "https://lh5.googleusercontent.com/d/1-CUhhgJDaGaTMJL6Ss0hdFENPb07F1FU"
    ]

    # Determina o índice do fundo atual com base no ID do estado
    fundo_index = next(
        (key for key, value in state_asset_mapping.items() if value.get("codigo", "") == fundo), None)

    if fundo_index is not None:
        log_debug(f"Índice do fundo '{fundo}': {fundo_index}")
    else:
        log_error(f"Fundo '{fundo}' não encontrado no mapeamento de estados.")
        # Define um índice padrão (primeiro fundo) ou tome outra ação apropriada
        fundo_index = 1
        log_info(f"Usando índice padrão: {fundo_index}")

    # Seleciona a imagem de fundo correspondente ao índice
    background_image = background_images[(
        fundo_index - 1) % len(background_images)]
    #log_warning(f"O link da imagem de fundo é: {background_image}")

    # ,_ significa que a variável variac_xpml11 não será utilizada
    cota_fii, card_fii, variac_fii, hist_text_fii, logo_url_atv = get_dadosfii(fii)
    
    #log_info(f"DADOS: {cota_fii, card_fii, variac_fii, hist_text_fii, logo_url_atv}")

    voz = card_fii.replace('<br>', '\n<break time="500ms"/>')

    cota_atual = cota_fii
    voz_fundo = voz
    voz = comparador(historico, cota_atual, voz_fundo, fii)

    # DIVIDE O HISTÓRICO EM DUAS COLUNAS
    #log_info(f"hist_text_FII é: {hist_text_fii}")
    meio = len(hist_text_fii) // 2  # Divide a lista ao meio
    hist_text_ativo_col1 = hist_text_fii[:meio]  # Primeira metade da lista
    hist_text_ativo_col2 = hist_text_fii[meio:]  # Segunda metade da lista
    #log_info(f"COl2 é: {hist_text_ativo_col2}")

    dados_info = {
        "card_ativo": card_fii or "Nenhuma informação disponível.",
        "variac_ativo": variac_fii or "Sem variação.",
        "hist_text_ativo_col1": hist_text_ativo_col1 or [],
        "hist_text_ativo_col2": hist_text_ativo_col2 or [],
        "hist_alert": hist_alert or "Sem alertas.",
        "background_image": background_image or "",
        "logo_url_atv": logo_url_atv or "",
        "url_grafico": url_grafico or ""
    }

    return dados_info, card_fii, variac_fii, hist_text_fii, apl_document, voz, timeout