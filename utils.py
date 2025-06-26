# utils

from ask_sdk_model.dialog.dynamic_entities_directive import DynamicEntitiesDirective
import logging
import time
import json
import re # Regex para trabalhar com expressões regulares
import grava_historico


# VARIÁVEIS: 

# Mapeamento de Estados e Fundos
state_asset_mapping, lista_ativos = grava_historico.carregar_ativos()
logging.info(f"\n O Mapa é: {state_asset_mapping}")

# Dicionário para letras em extenso (português)
letras_extenso = {
    "a": "a",
    "b": "bê",
    "c": "cê",
    "d": "dê",
    "e": "é",
    "f": "éfe",
    "g": "gê",
    "h": "agá",
    "i": "i",
    "j": "jóta",
    "k": "cá",
    "l": "éle",
    "m": "ême",
    "n": "êne",
    "o": "ó",
    "p": "pê",
    "q": "quê",
    "r": "érre",
    "s": "ésse",
    "t": "tê",
    "u": "u",
    "v": "vê",
    "w": "dáblio",
    "x": "xis",
    "y": "ípsilon",
    "z": "zê"
}

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

def gerar_sinonimos(fundo):
    # normaliza tudo em minúsculas
    base = fundo.strip().lower()
    letras = list(base)
    # 1) Sigla contínua
    contigua = base
    # 2) Sigla separada por espaço: "k n c r"
    separado = " ".join(letras)
    # 3) Sigla com pontos: "k.n.c.r"
    pontuada = ". ".join(letras)
    # 4) Sigla com pontos em maiúsculas: "K.N.C.R"
    pontuada_upper = pontuada.upper()
    # 5) Sigla com pontos em minusculas: 'k. n. c. r.'
    pontuada_literal = ". ".join(letras) + "."
    # 6) Letras por extenso: "kê ene cê erre"
    extenso = " ".join([letras_extenso.get(l, l) for l in letras])
    # Monta um set pra evitar duplicatas e retorna como lista
    return list({contigua, separado, pontuada, pontuada_upper, pontuada_literal, extenso})

def get_dynamic_entities_directive():
    fundos = [limpar_asset_name(v) for v in state_asset_mapping.values()]
    entities = [
        {
            "id": fundo,
            "name": {"value": fundo},
            "synonyms": gerar_sinonimos(fundo)
        } for fundo in fundos
    ]
    return DynamicEntitiesDirective(
        update_behavior="REPLACE",
        types=[
            {
                "name": "FUNDO_TYPES_xxxx",
                "values": entities
            }
        ]
    )

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
