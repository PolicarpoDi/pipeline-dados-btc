from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from bitcoin_pipeline import (get_bitcoin_data, kafka_producer,
                              predict_price_and_movement, train_model)
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
    data = get_bitcoin_data()  # Usando o Spark para coleta de dados
    
    if data is None or data.count() == 0:  # Verificando o Spark DataFrame
        raise ValueError("Erro: Nenhum dado foi coletado da API.")
    
    print("✅ Dados coletados do Bitcoin:", data.show(5))  # Exibe os 5 primeiros dados do Spark DataFrame
    # Armazena o DataFrame para ser usado por outras tarefas
    kwargs['ti'].xcom_push(key='bitcoin_data', value=data.toJSON().collect())  # Convertendo para JSON
    
    return "Coleta de dados concluída"

collect_data_task = PythonOperator(
    task_id='collect_bitcoin_data',
    python_callable=collect_bitcoin_data,
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
    dag=dag,
)

# Tarefa 3: Previsão de preço do Bitcoin
def predict_bitcoin_price(**kwargs):
    predicted_price, movement_label = predict_price_and_movement()
    if predicted_price is None:
        raise ValueError("Erro: Previsão retornou None")
    
    print(f"💲 Preço previsto: {predicted_price}, Movimento: {movement_label}")
    kwargs['ti'].xcom_push(key='predicted_data', value=(predicted_price, movement_label))

predicted_price_and_movement_task = PythonOperator(
    task_id='predicted_bitcoin_price_and_movement',
    python_callable=predict_bitcoin_price,
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
    ti = kwargs.get('ti')
    if not ti:
        raise ValueError("Erro: Task Instance (ti) não foi passada corretamente.")

    # Recupera os dados do XCom
    predicted_data = ti.xcom_pull(task_ids='predicted_bitcoin_price_and_movement', key='predicted_data')

    print(f"🔍 Dados recuperados do XCom: {predicted_data}")

    if not predicted_data or not isinstance(predicted_data, (list, tuple)) or len(predicted_data) != 2:
        raise ValueError("Erro: Dados de previsão ausentes ou inválidos.")

    predicted_price, movement_label = predicted_data

    # Obtendo a data de previsão
    prediction_date = datetime.now(timezone.utc) - timedelta(hours=3)

    # Conectando ao PostgreSQL
    try:
        postgres_hook = PostgresHook(postgres_conn_id='Postgres')
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                # Inserção da previsão do preço
                cursor.execute("""
                    INSERT INTO predict_btc.bitcoin_predictions (prediction_date, predicted_price)
                    VALUES (%s, %s);
                """, (prediction_date, predicted_price))

                # Inserção do movimento previsto
                cursor.execute("""
                    INSERT INTO predict_btc.btc_movements (timestamp, predicted_movement)
                    VALUES (%s, %s);
                """, (prediction_date, movement_label))

                conn.commit()

        print(f"✅ Previsões inseridas no banco de dados: Preço {predicted_price}, Movimento {movement_label}")

    except Exception as e:
        print(f"❌ Erro ao inserir no banco de dados: {e}")
        raise
    
insert_to_db_task = PythonOperator(
    task_id='insert_prediction_to_db',
    python_callable=insert_prediction_to_db,
    dag=dag,
)
    
# Tarefa 6: Enviar previsão para o Kafka
def send_to_kafka(**kwargs):
    predicted_price, movement_label = kwargs['ti'].xcom_pull(task_ids='predicted_bitcoin_price_and_movement', key='predicted_data')
    
    if not predicted_price:
        raise ValueError("Erro: Nenhuma previsão foi encontrada para enviar ao Kafka.")

    kafka_producer({"predicted_price": predicted_price, "predicted_movement": movement_label})
    #print(f"✅ Previsão enviada para o Kafka: {predicted_price}")

send_to_kafka_task = PythonOperator(
    task_id='send_to_kafka',
    python_callable=send_to_kafka,
    dag=dag,
)


# Definindo a ordem das tarefas

collect_data_task >> train_model_task >> predicted_price_and_movement_task >> test_kafka_task >> insert_to_db_task >> send_to_kafka_task