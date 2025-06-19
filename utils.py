import logging

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
