# Imagem base do Python
FROM python:3.12-slim

# Configuração do diretório de trabalho
WORKDIR /app

# Copiar arquivos para o container
COPY . /app

# Instalar dependências
RUN pip install flask mysql-connector-python werkzeug --upgrade paho-mqtt


# Criar o diretório para uploads de imagens
RUN mkdir -p static/images


# Expor a porta usada pela API Flask
EXPOSE 5000

# Executar o aplicativo
CMD ["python", "app.py"]
