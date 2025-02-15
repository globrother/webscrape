# Use uma imagem base oficial mínima
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos de dependência para aproveitar o cache das camadas
COPY requirements.txt ./

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto
COPY . .

# Define variáveis de ambiente
ENV APPLICATION_ID=${APPLICATION_ID}
ENV CLIENT_KEY=${CLIENT_KEY}

# Exponha a porta 8080
EXPOSE 8080

# Define o comando de inicialização da aplicação
# CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
