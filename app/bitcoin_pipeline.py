import json

import joblib
import requests
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag
from pyspark.sql.window import Window
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# ✅ Iniciar Spark
spark = SparkSession.builder.appName("BitcoinPipeline").getOrCreate()

# 📌 1️⃣ Coleta os dados do Bitcoin via API e converte para Spark DataFrame
def get_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "30"}
    response = requests.get(url, params)
    data = response.json()
    prices = data['prices']
    
    # Criando DataFrame do Spark
    df = spark.createDataFrame(prices, ["timestamp", "price"])
    df = df.withColumn("timestamp", (col("timestamp") / 1000).cast("timestamp"))  # Converter ms para timestamp
    
    return df

# 📌 2️⃣ Treina os modelos de Machine Learning
def train_model():
    df = get_bitcoin_data()
    
    if df.count() == 0:
        print("Erro: Dados do Bitcoin não disponíveis.")
        return None
    
    # Criando a coluna para prever o preço do próximo dia usando Spark
    window_spec = Window.orderBy("timestamp")
    df = df.withColumn("price_next_day", lag("price", -1).over(window_spec))
    df = df.dropna()

    # Convertendo para Pandas para treinar modelo com Scikit-Learn
    df_pandas = df.toPandas()
    
    # 📌 Modelo 1: Regressão Linear para prever preço do BTC no próximo dia
    X_price = df_pandas[['price']]
    y_price = df_pandas[['price_next_day']]
    
    model_price = LinearRegression()
    model_price.fit(X_price, y_price)
    joblib.dump(model_price, 'bitcoin_price_model.pkl')

    # 📌 Modelo 2: Regressão Logística para prever subida/descida do BTC
    df_pandas['price_change'] = df_pandas['price_next_day'] - df_pandas['price']
    df_pandas['price_movement'] = df_pandas['price_change'].apply(lambda x: 1 if x > 0 else 0)
    
    X_move = df_pandas[['price']]
    y_move = df_pandas['price_movement']
    
    X_train, X_test, y_train, y_test = train_test_split(X_move, y_move, test_size=0.2, shuffle=False)
    
    model_movement = LogisticRegression()
    model_movement.fit(X_train, y_train)
    y_pred = model_movement.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"A Acurácia do modelo de movimentação: {accuracy:.2f}")

    joblib.dump(model_movement, 'bitcoin_movement_model.pkl')

    return "Modelo treinado com sucesso"

# 📌 3️⃣ Previsão do preço e do movimento do Bitcoin
def predict_price_and_movement():
    df = get_bitcoin_data()
    
    if df.count() == 0:
        raise ValueError("Erro: Dados do Bitcoin não foram coletados corretamente.")

    last_price = df.orderBy(col("timestamp").desc()).limit(1).select("price").collect()[0]["price"]

    # Carrega os modelos treinados
    model_price = joblib.load('bitcoin_price_model.pkl')
    model_movement = joblib.load('bitcoin_movement_model.pkl')

    # Previsão de preço
    input_data = [[last_price]]
    predicted_price = model_price.predict(input_data)[0]
    predicted_price = round(float(predicted_price), 2)

    # Previsão de subida/descida
    predicted_movement = model_movement.predict(input_data)[0]
    movement_label = "Subida" if predicted_movement == 1 else "Descida"

    return predicted_price, movement_label

# 📌 4️⃣ Kafka Producer para enviar previsões
def kafka_producer(predicted_price):
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=5,
            linger_ms=100,
            batch_size=16384
        )
        
        # Envia a previsão de preço se for válida
        if predicted_price:
            producer.send('bitcoin_predictions', predicted_price)
            print(f"✅ Previsão enviada para o Kafka: {predicted_price}")
        else:
            print("⚠️ Previsão inválida. Não enviada para o Kafka.")
        
        producer.flush()
        producer.close()
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Kafka: {e}")
