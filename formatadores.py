# formatadores.py

def formatar_reais(valor):
    """
    Formata um número como moeda brasileira (R$).
    Aceita float, int ou string numérica com ponto ou vírgula.
    """
    try:
        if isinstance(valor, (int, float)):
            valor_float = float(valor)
        else:
            # Remove R$ e espaços
            valor_str = str(valor).replace('R$', '').replace(' ', '').strip()

            # Se tiver vírgula e não tiver ponto, assume que vírgula é decimal
            if ',' in valor_str and '.' not in valor_str:
                valor_str = valor_str.replace(',', '.')

            # Se tiver ponto e vírgula, assume que ponto é milhar e vírgula é decimal
            elif ',' in valor_str and '.' in valor_str:
                valor_str = valor_str.replace('.', '').replace(',', '.')

            valor_float = float(valor_str)

        # Formata com separador de milhar brasileiro
        reais = f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {reais}"
    except (ValueError, TypeError):
        return 'R$ 0,00'
    
"""    
def formatar_reais(valor):
    
    try:
        if isinstance(valor, (int, float)):
            valor_float = float(valor)
        else:
            valor_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_float = float(valor_str)
        return f'R$ {valor_float:,.2f}'.replace('.', ',')
    except (ValueError, TypeError):
        return 'R$ 0,00'"""