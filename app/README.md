# 🚀 Bitcoin Price Prediction Pipeline

## 📖 Visão Geral

Este projeto implementa um **pipeline de dados** para analisar e prever a variação do preço do **Bitcoin (BTC)**. Utiliza tecnologias avançadas, incluindo:

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
git clone https://github.com/seuusuario/bitcoin-pipeline.git
cd bitcoin-pipeline
```

🐍 2. Instale as Dependências do Python
bash
Copiar
Editar
pip install -r requirements.txt
🚀 3. Suba os Serviços com Docker Compose
bash
Copiar
Editar
docker-compose up -d
🎯 4. Acesse os Serviços
Airflow Web UI: http://localhost:8080
Kafka UI (Kafdrop): http://localhost:9000

📊 Modelo de Machine Learning
Tipo: Classificação Binária (Subida ou Queda)
Modelo: LogisticRegression
Entrada: Preço do Bitcoin nos últimos dias
Saída: 1 (Subida) ou 0 (Queda)
Métrica de Avaliação: Acurácia


## Rodando o teste
Dentro do container, execute os testes com:
```bash
docker-compose exec airflow pytest tests/test_bitcoin_pipeline.py
```

Adicionar na rede manualmente
                                                                                                   
docker network connect my_network kafka
docker network connect my_network kafdrop
docker network connect my_network postgres
docker network connect my_network airflow
docker network connect my_network spark-master
docker network connect my_network spark-worker
docker network connect my_network zookeeper