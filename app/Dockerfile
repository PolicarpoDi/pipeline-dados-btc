# Usando a imagem oficial do Python
FROM python:3.13

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    libpq-dev \
    curl \
    gnupg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar o Apache Kafka, Spark e PostgreSQL via Docker
# Kafka, Spark e PostgreSQL serão configurados via docker-compose.yml

# Instalando as bibliotecas Python necessárias
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Definindo o diretório de trabalho
WORKDIR /app

# Copiar o código do projeto para dentro do container
COPY . /app

# Comando para iniciar o Airflow (caso o Airflow esteja sendo usado)
CMD ["airflow", "webserver", "--port", "8080"]
