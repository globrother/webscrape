#from flask import Flask, request, send_from_directory, jsonify
#from flask_sslify import SSLify
#from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import requests
import time
#import json
import os

# sslify = SSLify(app)
OUTPUT_DIR = os.path.abspath(os.path.dirname(__file__))
# 🔹 Definições da API
API_KEY = "KY23IP0KJZYSOU3Y"  # Colocar em uma variável de ambiente
SYMBOL = "BBAS3"

CACHE_DIR = "./cache"
CACHE_TIME_LIMIT = 60 * 60  # 🔹 Tempo de cache: 1 hora

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

"""
def enviar_para_telegram(mensagem):
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ Telegram não configurado")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar para Telegram: {e}")
"""
print("Iniciando Rederização do Gráfico")
# 🔹 Função para verificar se o gráfico já existe no cache
def get_cached_image(ticker):
    filename = f"{CACHE_DIR}/grafico-{ticker}-15dias.png"
    
    if os.path.exists(filename):
        last_modified = os.path.getmtime(filename)
        if time.time() - last_modified < CACHE_TIME_LIMIT:
            return filename  # 🔹 Retorna imagem existente
    
    return None  # 🔹 Força geração de nova imagem se cache expirou


def gerar_grafico(ticker):
    print("Gerando Gráfico")
    ticker = (ticker.upper() + ".SA")
    output_filename = f"{CACHE_DIR}/grafico-{ticker}-100dias.png"
    # 🔹 Verifica se já há imagem recente no cache
    cached_image = get_cached_image(ticker)
    if cached_image:
        print(">> Usando imagem em cache.")
        return cached_image

    # 🔹 Obtendo dados do yfinance
    try:
        ativo = yf.Ticker(ticker)
        historico = ativo.history(period="100d")
        print(F"requisição finalizada de Yahoo Finance para {ticker}]: 100 dias.")
        if historico.empty:
            raise ValueError("Ticker não encontrado ou sem dados")
    except ValueError as e:
        raise ValueError(f"Ticker inválido ou sem dados: {e}")
    except ConnectionError as e:
        raise ConnectionError(f"Falha de rede ao consultar o Yahoo Finance: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro inesperado ao consultar o Yahoo Finance: {e}")
    
    # 🔹 Extraindo dados relevantes
    try:
        historico.reset_index(inplace=True)
        dados_extraidos = historico[["Date", "High", "Low", "Volume"]].copy()
        dados_extraidos.columns = ["data", "maximo", "minimo", "volume"]
    except KeyError as e:
        raise KeyError(f"Coluna esperada não encontrada: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao processar dados históricos: {e}")

    # 🔹 Criando DataFrame
    try:
        df = pd.DataFrame(dados_extraidos)
        df["data"] = df["data"].dt.tz_localize(None) # Removendo timezone se necessário
        df["data"] = pd.to_datetime(df["data"])  # Convertendo para formato datetime
        df = df.sort_values("data")  # Ordenando por data

        # 🔹 Filtrando os últimos **20 dias**
        hoje = datetime.today()
        limite = hoje - timedelta(days=20) # Ajuste para 20 dias
        df = df[~df["data"].dt.weekday.isin([5, 6])]
        df = df[df["maximo"] > 0]  # Exclui registros com preço zerado
        df = df[df["minimo"] > 0]  # Exclui registros com preço zerado
        df = df[df["volume"] > 0]  # Remove dias sem negociação
        df_crop = df[df["data"] >= limite].copy()  # Agora é uma cópia real

        df_crop["maximo"] = df_crop["maximo"].astype(float).round(2)  # Converte para garantir tipo numérico
        df_crop["minimo"] = df_crop["minimo"].astype(float).round(2)
        df_crop["intervalo"] = df_crop["maximo"] - df_crop["minimo"] # Calculando o intervalo entre máximo e mínimo

        # 🔹 Calculando variação do volume e atribuindo cores
        df_crop["variação_volume"] = df_crop["volume"].diff()
        df_crop["cor_volume"] = ["rgba(0, 255, 0, 0.4)" if v >= 0 else "rgba(255, 85, 0, 0.4)" for v in df_crop["variação_volume"]]

        #print(df_crop.head(25))  # Exibe os primeiros registros
        #print(df.info())  # Mostra informações sobre colunas e tipos

        # 🔹 Criando o gráfico
        fig = go.Figure()

        # 🔹 Barras de volume com cor dinâmica
        fig.add_trace(go.Bar(
            x=df_crop["data"],
            y=df_crop["volume"],
            name="Volume",
            marker=dict(color=df_crop["cor_volume"], line=dict(width=0)),  # Aplicando cores conforme a variação
            width=1000 * 60 * 60 * 24, # Largura das barras de volume em dias
            yaxis="y2",  # Agora usa o eixo principal
            text=df_crop["volume"].apply(lambda x: f"{x / 1_000_000:.2f}"), # Formata o volume como string sem casas decimais, com separador de milhar
            textposition="inside", # Coloca o texto DENTRO da barra
            textangle=-45, # Ângulo do texto (0 para horizontal)
            #textfont=dict(family="Ubuntu light", color="rgba(255, 255, 255, 1)", size=8), # Cor da fonte do volume (ajuste para contraste com a barra)
            insidetextfont=dict(family="Ubuntu light", size=8, color="white"),
            insidetextanchor="start", # Ancoragem do texto dentro da barra (centro)
            constraintext="inside" # Tenta manter o texto dentro da barra
        ))

        # 🔹 Barras flutuantes para preço
        fig.add_trace(go.Bar(
            x=df_crop["data"],
            y=df_crop["intervalo"],  
            base=df_crop["minimo"],  
            marker=dict(color="white", line=dict(width=0)),  # Barras de preços sem borda
            opacity=0.6,
            name="Mínimo e Máximo",
            width=1000 * 60 * 60 * 24 * 0.7, # Largura das barras de preços em dias
            yaxis="y"  # Agora usa o eixo secundário
            #textfont=dict(color="white", family="Ubuntu light"),  # Fonte branca para o texto
            #text=df_crop["maximo"],  
            #textposition="outside",
            #outsidetextfont=dict(size=20, color="white"),
            #text=[f"{x:.2f}" for x in df_crop["maximo"]],  # Força duas casas decimais
            #textangle=-90,
        ))

        # 🔹 Adicionamos legenda para os valores mínimos
        for i, row in df_crop.iterrows():
            # Adiciona anotação para o máximo
            fig.add_annotation(
                x=row["data"],
                y=row["maximo"],
                text=str(f"{row['maximo']:.2f}"),
                textangle=-90,
                showarrow=False,
                yshift=25,  # Ajusta para ficar acima
                font=dict(color="white", size=16),
                opacity=0.8
            )
            # Adiciona anotação para o mínimo
            fig.add_annotation(
                x=row["data"],
                y=row["minimo"],
                text=str(f"{row['minimo']:.2f}"),
                textangle=-90,
                showarrow=False,
                yshift=-25,  # Ajusta para ficar abaixo
                font=dict(color="white", size=16),
                opacity=0.8
            )
        
        # 🔹 Adicionando gráfico de linha para o preço mínimo
        fig.add_trace(go.Scatter(
            name="Útimos 100 dias ",
            x=df["data"],
            y=df["minimo"],
            mode="lines",
            line=dict(color="rgba(250, 165, 0, 0.8)", width=2, dash="solid", shape="spline"),
            yaxis="y3",
            xaxis="x2"
        ))

        minDfCrop = min(df_crop["minimo"])
        maxDfcrop = max(df_crop["maximo"])
        minDf = min(df["minimo"])
        maxDf = max(df["maximo"])
        maxDfvol = max(df_crop["volume"])
        #print("maxdfvol:", maxDfvol)

        # 🔹 Configuração do Layout
        fig.update_layout(
            #title="Cotação + Volume de Negociações",
            # 🔹 Configuração Eixo dos Preços >>>>>>>>>>>>>>
            yaxis=dict(
                #title="Preço",
                side="right",
                overlaying="y2",
                zeroline=False,
                range=[minDfCrop-minDfCrop*0.08, maxDfcrop+maxDfcrop*0.04],  # Ajusta o range para incluir margem
                gridcolor="rgba(255,255,255,0.1)",  # Cor das linhas do eixo Y dos preços
                tickformat=".1f",  # Formato dos ticks do eixo de preços
                gridwidth=1,  # 🔹 Mesma espessura das linhas do eixo de preços
                ticks="outside", tickcolor='rgba(0,0,0,0)', ticklen=5,
                tickfont=dict(color="rgba(255, 255, 255, 1)", size=14),  # Cor e tamanho da fonte do eixo de preços
                nticks=15
            ),
            
            # 🔹 Configuração Eixo de Volumes >>>>>>>>>>>>>>
            yaxis2=dict(
                #title="Volume",
                side="left",
                range=[0, maxDfvol*3.5],
                zeroline=False,
                showgrid=False,
                #dtick=((maxDfvol)/3.7),
                ticks="outside", tickcolor='rgba(0,0,0,0)', ticklen=5,
                tickfont=dict(color="rgba(255, 255, 255, 1)", size=14),
                nticks=15  
            ),
            
            yaxis3=dict(
                #title="Preço Mínimo",
                side="right",
                showgrid=False,
                #showline=False,  # Remove a linha
                #zeroline=False,  # Remove a linha
                overlaying="y",
                range=[minDf-minDf*0.25, maxDf+maxDf*0.10],
                tickformat=".1f",  # Formato dos ticks do eixo de preços
                #dtick=((minDfCrop)/18),
                ticks="outside", tickcolor='rgba(0,0,0,0)', ticklen=45,
                #tick0=(minDfCrop)-(minDfCrop)*0.05,  # Início dos ticks
                tickfont=dict(color="rgba(250, 145, 0, 1)", size=15),  # Cor e tamanho da fonte do eixo de preços mínimos
                nticks=20
            ),
            
            # 🔹 Configuração Eixo do Tempo >>>>>>>>>>>>>>
            xaxis=dict(
                #title="Data",
                tickangle=-45,
                dtick= 60 * 60 * 24 * 1000,  # Intervalo de 1 dia em milissegundos
                zeroline=False,
                #range=[min(df_crop["data"]), max(df_crop["data"])],
                tickfont=dict(color="rgba(255, 255, 255, 1)", size=14),
                tickformat="%b %d",  # Exibe apenas o mês e o dia
                rangebreaks=[dict(bounds=["sat", "mon"])] # Ignora fins de semana
            ),
            
            xaxis2=dict(
                #title="Data (Topo)",
                overlaying="x",
                side="top",
                tickangle=0,
                showgrid=False,
                zeroline=False,  # Remove a linha
                ticks="outside", tickcolor='rgba(0,0,0,0)', ticklen=10,
                tickformat="%b %d",  # Exibe apenas o mês e o dia
                tickfont=dict(color="rgba(255, 255, 255, 1)"),
            ),
            
            legend=dict(
                orientation="h",  # Legenda horizontal
                #entrywidth=150,  # Largura de cada entrada na legenda
                yanchor="bottom",
                font=dict(color="rgba(255, 255, 255, 1)"),
                y=1.12,  # Posição acima do gráfico
                xanchor="right",
                x=1
            ),
            
            # 🔹 Configurações gerais do Layout >>>>>>>>>>>>>>
            barmode="overlay",  
            showlegend=True,
            width=600,  # Largura do gráfico
            height=450,  # Altura do gráfico
            paper_bgcolor="rgba(0,0,0,0.4)",  # Fundo transparente
            plot_bgcolor="rgba(0,0,0,0)",    # Fundo transparente
            margin=dict(l=30, r=40, t=40, b=40),
            uniformtext=dict(minsize=14, mode="show")
        )
    except ValueError as e:
        raise ValueError(f"Erro nos dados do gráfico: {e}")
    except TypeError as e:
        raise TypeError(f"Tipo de dado incompatível para gráfico: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro inesperado ao gerar gráfico: {e}")
    
    # 🔹 Salvar o gráfico como PNG
    try:
        img_bytes = fig.to_image(format="png")
        with open(output_filename, "wb") as f:
            f.write(img_bytes)  # grava os bytes no arquivo
        if not os.path.exists(output_filename):
            raise FileNotFoundError("Gráfico não foi salvo. Verifique Kaleido ou permissões.")
        if not os.path.exists(output_filename):
            raise RuntimeError("Arquivo não foi gerado.")
        print("Gráfico Gerado com Sucesso")
        return output_filename 
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Falha ao salvar gráfico: {e}")
    except OSError as e:
        raise OSError(f"Erro de sistema ao salvar gráfico: {e}")
    except ValueError as e:
        raise ValueError(f"Erro de configuração do Plotly/Kaleido: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro inesperado ao salvar gráfico: {e}")

    