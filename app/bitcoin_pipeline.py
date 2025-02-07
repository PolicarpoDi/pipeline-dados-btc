import json
import time

import joblib
import pandas as pd
import requests
from kafka import KafkaProducer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


# coleta os dados do Bitcoin via API
def get_bitcoin_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "30"}
    response = requests.get(url, params)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Treina os modelos de Machine Learning
def train_model():
    df = get_bitcoin_data()
    
    if df is None or df.empty:
        print("Erro: Dados do Bitcoin não disponíveis.")
        return None
    
    # Criando a coluna para prever o preço do próximo dia
    df['price_next_day'] = df['price'].shift(1)
    df = df.dropna()
    
    # 📌 Modelo 1: Regressão Linear para prever preço do BTC no próximo dia
    X_price = df[['price']]
    y_price = df[['price_next_day']]
    
    model_price = LinearRegression()
    model_price.fit(X_price, y_price)
    joblib.dump(model_price, 'bitcoin_price_model.pkl')
    
    # 📌 Modelo 2: Regressão Logística para prever subida/descida do BTC
    df['price_change'] = df['price_next_day'] - df['price']
    df['price_movement'] = df['price_change'].apply(lambda x: 1 if x > 0 else 0)
    
    X_move = df[['price']]
    y_move = df['price_movement']
    X_train, X_test, y_train, y_test = train_test_split(X_move, y_move, test_size=0.2, shuffle=False)
    
    model_movement = LogisticRegression()
    model_movement.fit(X_train, y_train)
    y_pred = model_movement.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"A Acurácia do modelo de movimentação: {accuracy:.2f}")
    
    joblib.dump(model_movement, 'bitcoin_movement_model.pkl')
    
    return "Modelo treinado com sucesso"
    
# Previsão do preço e do movimento do Bitcoin
def predict_price_and_movement():
    df = get_bitcoin_data()
    
    if df.empty:
        raise ValueError("Erro: Dados do Bitcoin não foram coletados corretamente.")
    
    last_price = df['price'].iloc[-1]
    
    # Carrega os modelos treinados
    model_price = joblib.load('bitcoin_price_model.pkl')
    model_movement = joblib.load('bitcoin_movement_model.pkl')
    
    # Previsão de preço
    input_data = pd.DataFrame([[last_price]], columns=['price'])
    predicted_price = model_price.predict(input_data)[0][0]
    predicted_price = round(float(predicted_price), 2)
    
    # Previsão de subida/descida
    predicted_movement = model_movement.predict(input_data)[0]
    movement_label = "Subida" if predicted_movement == 1 else "Descida"
    
    return predicted_price, movement_label
    
# Kafka Producer para enviar previsões
def kafka_producer(predicted_price):
    try:
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # Serializa em JSON
            acks='all',  # Confirmação de escrita
            retries=5,  # Tenta novamente em caso de falha
            linger_ms=100,  # Atraso antes de enviar para agrupamento de mensagens
            batch_size=16384  # Tamanho de lote para otimização de desempenho
        )
        
        # Envia a previsão de preço se for válida
        if predicted_price:
            producer.send('bitcoin_predictions', predicted_price)
            print(f"✅ Previsão enviada para o Kafka: {predicted_price}")
        else:
            print("⚠️ Previsão inválida. Não enviada para o Kafka.")
        
        producer.flush()  # Garante que a mensagem seja enviada
        producer.close()
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Kafka: {e}")