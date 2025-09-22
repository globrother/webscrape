import plotly.express as px
import os

try:
    fig = px.line(x=[1, 2, 3], y=[10, 20, 30])
    print("chamando fig.write_image")
    fig.write_image("teste1.png")
    if not os.path.exists("teste.png"):
        raise FileNotFoundError("Gráfico não foi salvo. Verifique Kaleido ou permissões.")
    print("finalizando")
except FileNotFoundError as e:
    raise FileNotFoundError(f"Falha ao salvar gráfico: {e}")
except OSError as e:
    raise OSError(f"Erro de sistema ao salvar gráfico: {e}")
except ValueError as e:
    raise ValueError(f"Erro de configuração do Plotly/Kaleido: {e}")
except Exception as e:
    raise RuntimeError(f"Erro inesperado ao salvar gráfico: {e}")