# 🚀 Bitcoin Price Prediction Pipeline

## 📖 Visão Geral

Este projeto implementa um **pipeline de dados** para analisar e prever a variação do preço e a tendencia de subida ou descida do **Bitcoin (BTC)** para o próximo dia. Utiliza tecnologias avançadas, incluindo:

- **Apache Airflow**: Orquestração de tarefas
- **Apache Kafka**: Processamento em tempo real
- **Apache Spark**: Processamento distribuído de grandes volumes de dados
- **PostgreSQL**: Armazenamento de dados históricos
- **Machine Learning**: Modelo para prever se o preço do Bitcoin irá **subir ou cair** no dia seguinte

---

## 🛠️ Tecnologias Utilizadas

- **Docker + Docker Compose** → Facilita a implantação de todos os serviços  
- **Apache Airflow** → Agendamento e orquestração de tarefas  
- **Apache Kafka** → Streaming de dados  
- **Apache Spark** → Processamento de dados em larga escala  
- **PostgreSQL** → Banco de dados relacional para armazenamento  
- **Scikit-learn** → Modelos de Machine Learning  
- **Joblib** → Serialização do modelo de IA  
- **Python** → Linguagem principal do projeto  

---

## 🏗️ Configuração e Instalação

### 📌 **Pré-requisitos**
Antes de iniciar, certifique-se de ter instalados:

- **Docker** e **Docker Compose**
- **Python 3.10+**
- **Git**

### 📥 **1. Clone o Repositório**

```bash
git clone https://github.com/PolicarpoDi/pipeline-dados-btc
cd bitcoin-pipeline/app/
```

## 🐍 2. Instale as Dependências do Python
### ✅ 2.1 Crie o ambiente virtual (utilizando _Virtualenv_)
```bash
virtualenv venv
```

### ✅2.2 Ative o ambiente virtual
```bash
Source venv/bin/active
```

## 🚀 3. Suba os Serviços com Docker Compose
```bash
docker-compose up -d
```

## 🌐 4. Configuração da rede do container
Os Serviços não estão sendo setados na rede configurada no Compose, portanto, é necessário setar manualmente com o seguinte comando 
```bash
docker network connect my_network kafka
docker network connect my_network kafdrop
docker network connect my_network postgres
docker network connect my_network airflow
docker network connect my_network spark-master
docker network connect my_network spark-worker
docker network connect my_network zookeeper
```

## 🎯 5. Acesse os Serviços
- Airflow Web UI: http://localhost:8080
- Kafka UI (Kafdrop): http://localhost:9000

## 📊 Modelos de Machine Learning Utilizados
### 🔢 LogisticRegression
- Tipo: Classificação Binária (Subida ou Queda)
- Entrada: Preço do Bitcoin nos últimos dias
- Saída: 1 (Subida) ou 0 (Queda)
- Métrica de Avaliação: Acurácia

### 📉 LinearRegression
- Tipo: Regressão (Prever preço do BTC no próximo dia)
- Entrada: Preço do Bitcoin nos últimos dias
- Saída: Preço do Bitcoin no próximo dia
- Métrica de Avaliação: Erro Quadrático Médio (MSE) 

## 🔍 Rodando os testes
Dentro do container, execute os testes com:
```bash
docker-compose exec airflow pytest tests/test_bitcoin_pipeline.py
```

## 🚀 CI/CD Pipeline para Análise de Bitcoin
Este repositório possui um pipeline automatizado de CI/CD usando GitHub Actions e Docker para garantir a qualidade e a entrega contínua do código.

### 📌 Como funciona o pipeline?
Sempre que um push ou pull request for feito na branch main, o CI/CD executa automaticamente os seguintes passos:

### 1️⃣ Build
- Constrói a imagem Docker com todas as dependências.
- Garante que o ambiente esteja pronto para execução.
### 2️⃣ Treino do Modelo
- Antes de rodar os testes, o modelo de previsão do Bitcoin é treinado.
- Isso gera os arquivos bitcoin_price_model.pkl e bitcoin_movement_model.pkl, que serão usados na predição.
### 3️⃣ Testes Automatizados
- O código passa por testes unitários usando Pytest e Spark.
- Isso garante que as previsões de preço e movimentação do Bitcoin estejam corretas.
### 4️⃣ Deploy para Produção
- Se todos os testes passarem, o código atualizado é implantado automaticamente.
- O comando docker-compose up -d sobe os containers e aplica as atualizações.