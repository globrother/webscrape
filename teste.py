import plotly.express as px
import os

import plotly.io as pio
#pio.defaults.default_format = "png"
#pio.defaults.default_width = 600
#pio.defaults.default_height = 400


nome = "teste.png"
try:
    fig = px.line(x=[1, 2, 3], y=[10, 20, 30])
    #print("chamando fig.write_image")
    fig.write_image(nome,  width=800, height=450, scale=1)
    if not os.path.exists(nome):
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