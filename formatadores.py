# formatadores.py
    
def formatar_reais(valor):
    """
    Formata um número como moeda brasileira (R$).
    Aceita float, int ou string numérica.
    """
    try:
        if isinstance(valor, (int, float)):
            valor_float = float(valor)
        else:
            valor_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_float = float(valor_str)
        return f'R$ {valor_float:,.2f}'.replace('.', ',')
    except (ValueError, TypeError):
        return 'R$ 0,00'