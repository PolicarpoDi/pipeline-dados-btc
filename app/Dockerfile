# Usando a imagem oficial do Java 11
FROM openjdk:11-jdk-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Instalando dependências do sistema e o Python 3.10
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-distutils \
    python3-pip \
    default-libmysqlclient-dev \
    gcc \
    libpq-dev \
    graphviz \
    curl \
    gnupg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Definindo o JAVA_HOME para Java 11
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Copiar o arquivo de requisitos antes do código-fonte para otimizar o cache
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Instalar a biblioteca Graphviz do Python
RUN pip3 install graphviz

# Copiar o código do projeto para dentro do container
COPY . /app

# Definir o PYTHONPATH para incluir a pasta 'app'
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Dar permissão de execução ao script de entrada
RUN chmod +x /app/entrypoint.sh

# Definir o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
