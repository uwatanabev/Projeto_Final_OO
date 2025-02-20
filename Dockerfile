# Dockerfile para a aplicação E-commerce Flask

# Usa uma imagem Python slim para reduzir o tamanho do container
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências e instala as bibliotecas necessárias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o container
COPY . .

# Expõe a porta 5000 para acesso externo
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "main.py"]
