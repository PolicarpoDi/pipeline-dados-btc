#!/bin/bash

# Habilitar modo debug para visualizar erros
set -e

# Iniciar o banco de dados do Airflow (caso necessário)
airflow db init

# Criar o usuário admin do Airflow se ainda não existir
airflow users create \
    --username admin \
    --password admin \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@example.com || true

# Iniciar o scheduler e o webserver
airflow scheduler & airflow webserver --port 8080