import sqlite3
import pandas as pd
import os

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# 1. Importar map_ativo.csv
df_ativos = pd.read_csv("Back4App_data/map_ativo.csv")
df_ativos.to_sql("ativos", conn, if_exists="replace", index=False)

# 2. Importar arquivos historico_<ativo>.csv
for arquivo in os.listdir("Back4App_data"):
    if arquivo.startswith("historico_") and arquivo.endswith(".csv"):
        ativo = arquivo.replace("historico_", "").replace(".csv", "").lower()
        df = pd.read_csv(f"Back4App_data/{arquivo}")
        df["ativo"] = ativo
        df["valor"] = df["valor"].str.replace("R$ ", "").str.replace(",", ".").astype(float)
        df.to_sql("historico", conn, if_exists="append", index=False)

# 3. Importar arquivos alert_value_<ativo>.csv
for arquivo in os.listdir("Back4App_data"):
    if arquivo.startswith("alert_value_") and arquivo.endswith(".csv"):
        ativo = arquivo.replace("alert_value_", "").replace(".csv", "").lower()
        df = pd.read_csv(f"Back4App_data/{arquivo}")
        df["ativo"] = ativo
        df["valor"] = df["valor"].str.replace("R$ ", "").str.replace(",", ".").astype(float)
        df.to_sql("alertas", conn, if_exists="append", index=False)

conn.close()
print("FIM")