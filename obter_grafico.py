from time import time
from chart_server import gerar_grafico

# ====================:: CONFIGURAÇÃO DO LOGTAIL ::====================
import logging
from log_utils import log_debug, log_info, log_warning, log_error
# =====================================================================

def requisitando_chart(ticker):
    start = time()
    log_debug("Agora em requisitando_chart")
    try:
        caminho_imagem = gerar_grafico(ticker)
        log_info(f"⏱️​​ Processado em ⏳ {time() - start:.2f}s ⏳")
        return caminho_imagem  # Retorna o caminho local do arquivo gerado
    except Exception as e:
        log_error(f"Erro ao gerar gráfico: {e}")
        return None
    
# 🔹 Exemplo de chamada
# resultado = requisitando_chart("BBAS3")
# print(resultado)