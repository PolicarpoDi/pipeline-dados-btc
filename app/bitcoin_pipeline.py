import json
import time

import joblib
import pandas as pd
import requests
from kafka import KafkaProducer
from sklearn.linear_model import LinearRegression


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

# Treina o modelo de Machine Learning
def train_model():
    df = get_bitcoin_data()
    if df is None or df.empty:
        print("Erro: Dados do Bitcoin não disponíveis.")
        return None

    df['price_previous'] = df['price'].shift(1)
    df = df.dropna()
    X = df[['price_previous']]
    y = df['price']
    
    model = LinearRegression()
    model.fit(X, y)
    
    joblib.dump(model, 'bitcoin_model.pkl')
    
    return "Modelo treinado com sucesso"
    
# Previsão do preço do Bitcoin
def predict_price():
    df = get_bitcoin_data()
    
    if df.empty:
        raise ValueError("Erro: Dados do Bitcoin não foram coletados corretamente.")
    
    # Carrega o modelo treinado
    model = joblib.load('bitcoin_model.pkl')
    
    last_price = df['price'].iloc[-1]
    
    # Passando como Dataframe com o nome correto da coluna
    input_data = pd.DataFrame([[last_price]], columns=['price_previous'])
    
    predicted_price = model.predict(input_data)[0]  # Pegamos apenas o primeiro valor da previsão
    
    # Formatando para duas casas decimais
    predicted_price_formatted = round(float(predicted_price), 2)
    
    return predicted_price_formatted

    
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