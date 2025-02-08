# Usando a imagem oficial do Python 3.10
FROM python:3.10

# Definindo o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (incluindo LZO e Maven)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    openjdk-11-jdk \
    gcc \
    libpq-dev \
    graphviz \
    curl \
    gnupg \
    git \
    wget \
    maven \
    && rm -rf /var/lib/apt/lists/*

# Instalar LZO (2.x), seguindo as instruções da documentação
RUN wget https://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz \
    && tar -xzvf lzo-2.10.tar.gz \
    && cd lzo-2.10 \
    && ./configure --enable-shared --prefix=/usr/local/lzo-2.10 \
    && make && make install \
    && rm -rf /app/lzo-2.10*

# Instalar o Hadoop-LZO (construção com Maven)
RUN wget https://github.com/twitter/hadoop-lzo/releases/download/v0.4.20/hadoop-lzo-0.4.20.jar \
    && mv hadoop-lzo-0.4.20.jar /usr/lib/hadoop/lib/

# Configurar variáveis de ambiente para o Java 11 e Hadoop-LZO
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_CLASSPATH=/usr/lib/hadoop/lib/hadoop-lzo-0.4.20.jar
ENV JAVA_LIBRARY_PATH=/usr/lib/hadoop/lib

# Copiar e instalar dependências do Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instalar a biblioteca Graphviz do Python
RUN pip install graphviz

# Copiar o código do projeto para dentro do container
COPY . /app

# Definir o PYTHONPATH para incluir a pasta 'app'
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Dar permissão de execução ao script de entrada
RUN chmod +x /app/entrypoint.sh

# Definir o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
