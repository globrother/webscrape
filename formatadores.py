# formatadores.py

import locale

def formatar_reais(valor):
    """
    Formata um número como moeda brasileira (R$).
    Aceita float, int ou string numérica.
    """
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Linux/macOS
        # Para Windows, use: locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

        if isinstance(valor, (int, float)):
            valor_float = float(valor)
        else:
            valor_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_float = float(valor_str)

        return locale.currency(valor_float, grouping=True)
    except (ValueError, TypeError, locale.Error):
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