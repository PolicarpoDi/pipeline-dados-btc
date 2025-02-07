import time
from datetime import datetime, timedelta

import psycopg2
from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from bitcoin_pipeline import (get_bitcoin_data, kafka_producer, predict_price,
                              train_model)
from kafka import KafkaProducer

# Definindo os argumentos padrão
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    #'start_date': datetime(2025,1,1),
    #'start_date': datetime.today().date(),  # Apenas a data de hoje
    'start_date': datetime.today(),
}

# Definindo a Dag
dag = DAG(
    'bitcoin_etl',
    default_args=default_args,
    description='ETL para Bitcoin',
    schedule_interval=timedelta(hours=1), # Executa toda hora
    catchup=False,  # Evita execução retroativa
)

# Tarefa 1: Coleta de dados do Bitcoin
def collect_bitcoin_data(**kwargs):
    data = get_bitcoin_data()
    if data is None or data.empty:
        raise ValueError("Erro: Nenhum dado foi coletado da API.")
    
    print("✅ Dados coletados do Bitcoin:", data.head())
    # Armazena o DataFrame para ser usado por outras tarefas
    kwargs['ti'].xcom_push(key='bitcoin_data', value=data.to_json())
    return "Coleta de dados concluída"

collect_data_task = PythonOperator(
    task_id='collect_bitcoin_data',
    python_callable=collect_bitcoin_data,
    provide_context=True,
    dag=dag,
)

# Tarefa 2: Treinamento do modelo de ML
def train_bitcoin_model(**kwargs):
    train_model()
    print("✅ Modelo treinado com sucesso")
    return "Modelo treinado com sucesso"

train_model_task = PythonOperator(
    task_id='train_bitcoin_model',
    python_callable=train_bitcoin_model,
    provide_context=True,
    dag=dag,
)

# Tarefa 3: Previsão de preço do Bitcoin
def predict_bitcoin_price(**kwargs):
    prediction = predict_price()
    if prediction is None:
        raise ValueError("Erro: Previsão retornou None")
    
    print(f"💲 Preço previsto para o próximo dia: {prediction}")
    kwargs['ti'].xcom_push(key='predicted_price', value=prediction)
    return prediction

predict_price_task = PythonOperator(
    task_id='predict_bitcoin_price',
    python_callable=predict_bitcoin_price,
    provide_context=True,
    dag=dag,
)

# Tarefa 4: Testa conexão do Kafka
def test_kafka_connection():
    producer = KafkaProducer(bootstrap_servers=['kafka:9092'])
    try:
        # Envia uma mensagem de teste para garantir que a conexão funcione
        producer.send('test-topic', b'test message')
        producer.flush()
        producer.close()
        print("✅ Conexão com Kafka bem-sucedida!")
    except Exception as e:
        print(f"Erro na conexão com Kafka: {e}")
        raise
    
test_kafka_task = PythonOperator(
    task_id='test_kafka_connection',
    python_callable=test_kafka_connection,
    dag=dag
)

# Tarefa 5: Inserir previsão no banco de dados
def insert_prediction_to_db(**kwargs):
    predicted_price = kwargs['ti'].xcom_pull(task_ids='predict_bitcoin_price', key='predicted_price')
    if not predicted_price:
        raise ValueError("Erro: Nenhuma previsão foi encontrada para armazenar no banco de dados.")

    # Obtendo a data de previsão
    prediction_date = datetime.now()

    # Conectando ao PostgreSQL
    postgres_hook = PostgresHook(postgres_conn_id='Postgres')
    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # Comando para inserir a previsão
    insert_query = """
    INSERT INTO predict_btc.bitcoin_predictions (prediction_date, predicted_price)
    VALUES (%s, %s);
    """
    
    cursor.execute(insert_query, (prediction_date, predicted_price))
    conn.commit()

    # Fechar conexão
    cursor.close()
    conn.close()

    print(f"✅ Previsão inserida no banco de dados: {predicted_price}")
    
insert_to_db_task = PythonOperator(
    task_id='insert_prediction_to_db',
    python_callable=insert_prediction_to_db,
    provide_context=True,
    dag=dag,
)
    
# Tarefa 6: Enviar previsão para o Kafka
def send_to_kafka(**kwargs):
    predicted_price = kwargs['ti'].xcom_pull(task_ids='predict_bitcoin_price', key='predicted_price')
    
    if not predicted_price:
        raise ValueError("Erro: Nenhuma previsão foi encontrada para enviar ao Kafka.")

    kafka_producer(predicted_price)
    #print(f"✅ Previsão enviada para o Kafka: {predicted_price}")

send_to_kafka_task = PythonOperator(
    task_id='send_to_kafka',
    python_callable=send_to_kafka,
    provide_context=True,
    dag=dag,
)

# Definindo a ordem das tarefas

collect_data_task >> train_model_task >> predict_price_task >> test_kafka_task >> insert_to_db_task >> send_to_kafka_task