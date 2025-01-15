# Use uma imagem base oficial mínima
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos de dependência para aproveitar o cache das camadas
COPY requirements.txt ./

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto
COPY . .

# Exponha a porta 5000
EXPOSE 5000

# Define o comando de inicialização da aplicação
CMD ["python", "app.py"]
