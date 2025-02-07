# Usando a imagem oficial do Python
FROM python:3.10

# Definindo o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    openjdk-17-jdk \
    gcc \
    libpq-dev \
    graphviz \
    curl \
    gnupg \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Copiar e instalar dependências antes do código-fonte (para cache otimizado)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instalar graphviz Python library
RUN pip install graphviz

# Copiar o código do projeto para dentro do container
COPY . /app

# Definir o PYTHONPATH para incluir a pasta 'app'
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Dar permissão de execução
RUN chmod +x /app/entrypoint.sh

# Definir o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
