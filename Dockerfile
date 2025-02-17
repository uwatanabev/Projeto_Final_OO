# Use uma imagem base Python slim
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos para o container
COPY requirements.txt ./

# Instala as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask-socketio eventlet

# Copia todo o código do projeto para o diretório de trabalho
COPY . .

# Expõe a porta 5000 para acesso externo
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "main.py"]

