# formatadores.py

def formatar_reais(valor):
    """
    Formata um número como moeda brasileira (R$).
    Aceita float, int ou string numérica.
    """
    try:
        valor_float = float(str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip())
        return f'R$ {valor_float:,.2f}'.replace('.', ',')
    except (ValueError, TypeError):
        return 'R$ 0,00'