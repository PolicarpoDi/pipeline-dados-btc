# Projeto de Pipeline de Dados Open-Source:

## Objetivo do Projeto:
Criar uma pipeline de dados em um container para coleta, transformação, análise, entrega contínua de dados e uso de ML para predição. Vamos usar Apache Kafka para streaming de dados em tempo real, Apache Spark para processamento distribuído, Apache Airflow para orquestração e agendamento, PostgreSQL para armazenamento, GitLab CI/CD para automação do processo scikit-learn para criação do modelo.

Coleta dados do Bitcoin utilizando uma API.
Processa os dados e faz a previsão usando um modelo de Machine Learning.
Orquestra todo o processo com o Apache Airflow.
Implementa um processo de CI/CD para automação.

### 1. Arquitetura Geral
A arquitetura geral do sistema será composta por:

Kafka: Coleta de dados em tempo real.
Spark: Processamento e transformação de dados.
PostgreSQL: Armazenamento final dos dados transformados.
Airflow: Orquestração da pipeline de dados.
GitLab CI/CD: Automação do processo de integração contínua e entrega contínua.
Scikit-learn: Modelo de ML


