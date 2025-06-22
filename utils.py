import logging
import time
import json
import re # Regex para trabalhar com expressões regulares
import grava_historico
import obter_grafico
from infofii import get_dadosfii

# VARIÁVEIS: 

# Mapeamento de Estados e Fundos
state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()
logging.info(f"\n O Mapa é: {state_asset_mapping}")

# Limpa o nome passado pelo usuário. EX: recebe "X P. mL11" e transforma em "xpml"
def limpar_asset_name(raw):
    if not raw:
        return None
    raw = str(raw).lower()
    raw = re.sub(r'\s|\.', '', raw)     # Remove espaços e pontos
    raw = re.sub(r'\d+$', '', raw)      # Remove números no final
    return raw

# Carrega documentos APL da pasta principal
def _load_apl_document(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # print(f"Content of {file_path}: {content}")
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Faz a comparação do valor da cota com o valor para o alerta de preço.
def comparador(historico, cota_atual, voz_fundo):
    # Verificar se o histórico é válido e contém pelo menos um registro
    if historico and isinstance(historico, list) and len(historico) >= 1:
        alert_value = historico[0].get("valor", "").replace("R$ ", "")
        logging.info(f"Valor do Alerta: {alert_value}")
        logging.info(f"Valor Atual da Cota: {cota_atual}")

        # Verificar se o valor do alerta é válido
        if alert_value:
            try:
                alert_value_float = float(alert_value.replace(',', '.'))
                cota_atual_float = float(cota_atual.replace(',', '.'))
                #logging.info(f"Valor de alert_value_float: {alert_value_float}")
                #logging.info(f"Valor de cota_atual_float: {cota_atual_float} \n")

                # Comparar os valores e adicionar aviso de fala se necessário
                if cota_atual_float <= alert_value_float:
                    voz_fundo += f"\n<break time='900ms'/>Aviso!<break time='500ms'/> Alerta de preço da cota atingido em ({cota_atual})!<break time='500ms'/> Repito, Alerta de preço atingido."
            except ValueError as e:
                logging.error(f"Erro ao converter valores para float: {e}")
    else:
        logging.info("\n Histórico está vazio ou não é uma lista válida \n")

    return voz_fundo

# ===============::::: SESSÃO WEBSCRAPE :::::===============
def web_scrape(fundo):
    # extrai os caracteres numéricos de fundo
    fundo_fii = limpar_asset_name(fundo)
    doc_apl = "apl_fii.json"  # f"apl_{fundo_fii}.json"
    # Carregar APL padrão de exibiçaõ dos fundos
    apl_document = _load_apl_document(doc_apl)
    # Adiciona a geração do texto do histórico de alertas
    sufixo = f"alert_value_{fundo_fii}"
    historico = grava_historico.ler_historico(sufixo)
    aux = "alert"
    hist_alert = grava_historico.gerar_texto_historico(historico, aux)
    # logging.info(f"\n Recuperando hist_alert_xpml da sessão: {hist_alert} \n")

    fii = fundo
    #logging.info(f"valor de fii: {fii}")
    
    # 🔹 Obtendo Url do Gráfico
    url_grafico = obter_grafico.requisitando_chart(fii)
    timestamp = int(time.time() // 3600)  # 🔹 Atualiza a cada hora
    url_grafico = f"{url_grafico}&v={timestamp}" if "?" in url_grafico else f"{url_grafico}?v={timestamp}" # verifica se já tem ? e atribui
    #logging.info(f"URL do Gráfico: {url_grafico}")

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
        (key for key, value in state_asset_mapping.items() if value == fundo), None)

    if fundo_index is not None:
        logging.info(f"Índice do fundo '{fundo}': {fundo_index}")
    else:
        logging.error(f"Fundo '{fundo}' não encontrado no mapeamento de estados.")
        # Define um índice padrão (primeiro fundo) ou tome outra ação apropriada
        fundo_index = 1
        logging.info(f"Usando índice padrão: {fundo_index}")

    # Seleciona a imagem de fundo correspondente ao índice
    background_image = background_images[(
        fundo_index - 1) % len(background_images)]
    # logger.info(f"O link da imagem de fundo é: {background_image}")

    # ,_ significa que a variável variac_xpml11 não será utilizada
    cota_fii, card_fii, variac_fii, hist_text_fii, logo_url_atv = get_dadosfii(fii)

    voz = card_fii.replace('<br>', '\n<break time="500ms"/>')

    cota_atual = cota_fii
    voz_fundo = voz
    voz = comparador(historico, cota_atual, voz_fundo)

    # DIVIDE O HISTÓRICO EM DUAS COLUNAS
    #logging.info(f"hist_text_FII é: {hist_text_fii}")
    meio = len(hist_text_fii) // 2  # Divide a lista ao meio
    hist_text_ativo_col1 = hist_text_fii[:meio]  # Primeira metade da lista
    hist_text_ativo_col2 = hist_text_fii[meio:]   # Segunda metade da lista
    #logging.info(f"COl2 é: {hist_text_ativo_col2}")

    dados_info = {
        "card_ativo": card_fii,
        "variac_ativo": variac_fii,
        "hist_text_ativo_col1": hist_text_ativo_col1,
        "hist_text_ativo_col2": hist_text_ativo_col2,
        "hist_alert": hist_alert,
        "background_image": background_image,
        "logo_url_atv": logo_url_atv,
        "url_grafico": url_grafico
    }

    return dados_info, card_fii, variac_fii, hist_text_fii, apl_document, voz

# Remove números ou sufixos da sigla de um fundo
def remover_sufixo_numerico(sigla):
    import re
    return re.sub(r'\d+$', '', sigla.strip().lower())

# Retorna uma lista padronizada de fundos permitidos
def obter_fundos_validos(state_fund_mapping):
    return [remover_sufixo_numerico(v).lower() for v in state_fund_mapping.values()]

# Verifica se uma sigla (sem sufixo numérico) é válida com base no mapeamento
def fundo_valido(sigla, state_fund_mapping):
    sigla = remover_sufixo_numerico(sigla)
    return any(remover_sufixo_numerico(v).lower() == sigla for v in state_fund_mapping.values())

# Retorna o nome completo e state_id de um fundo com base na sigla
def buscar_fundo_por_sigla(sigla, state_fund_mapping):
    sigla = remover_sufixo_numerico(sigla)
    for state_id, nome in state_fund_mapping.items():
        if remover_sufixo_numerico(nome).lower() == sigla:
            return nome, state_id
    return None, None

# Verifica se os slots existem com segurança
def extrair_valor_slot(slots, nome_slot):
    slot = slots.get(nome_slot)
    return slot.value if slot and slot.value else None

# Log para debug avançado (opcional)
def log_detalhado_session(slots, session_attr):
    logging.info(f"Slots: {slots}")
    logging.info(f"Atributos de Sessão: {session_attr}")
