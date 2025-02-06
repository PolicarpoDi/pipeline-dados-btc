import time
from datetime import datetime, timedelta

from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python_operator import PythonOperator

from app.bitcoin_pipeline import (get_bitcoin_data, kafka_producer,
                                  predict_price, train_model)

# Definindo os argumentos padrão
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025,1,1),
}

# Definindo a Dag
dag = DAG(
    'bitcoin_etl',
    default_args=default_args,
    description='ETL para Bitcoin',
    schedule_interval='@daily', # Executa todos os dias
)

# Tarefa 1: Coleta de dados do Bitcoin
def collect_bitcoin_data():
    data = get_bitcoin_data()
    print("Dados coletados do Bitcoin:", data.head())
    return data

collect_data_task = PythonOperator(
    task_id='collect_bitcoin_data',
    python_callable=collect_bitcoin_data,
    dag=dag,
)

# Tarefa 2: Treinamento do modelo de ML
def train_bitcoin_model():
    model = train_model()
    print("Modelo treinado com sucesso")
    return model

train_model_task = PythonOperator(
    task_id='train_bitcoin_model',
    python_callable=train_bitcoin_model,
    dag=dag,
)

# Tarefa 3: Previsão de preço do Bitcoin
def predict_bitcoin_price():
    prediction = predict_price()
    print(f"Preço previsto para o próximo dia: {prediction}")
    return prediction

predict_price_task = PythonOperator(
    task_id='predict_bitcoin_price',
    python_callable=predict_bitcoin_price,
    dag=dag,
)

# Tarefa 4: Enviar previsão para o Kafka
def send_to_kafka():
    kafka_producer()
    print("Previsão enviada para o Kafka")
    
send_to_kafka_task = PythonOperator(
    task_id='send_to_kafka',
    python_callable=send_to_kafka,
    dag=dag,
)

# Definindo a ordem das tarefas

collect_data_task >> train_model_task >> predict_price_task >> send_to_kafka_task