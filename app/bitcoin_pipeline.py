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
    df['price_previous'] = df['price'].shift(1)
    df = df.dopna()
    x = df[['price_previous']]
    y = df['price']
    
    model = LinearRegression()
    model.fit(x, y)
    
    joblib.dump(model, 'bitcoin_model.pkl')
    
# Previsão do preço do Bitcoin
def predict_price():
    df = get_bitcoin_data()
    model = joblib.load('bitcoin_model.pkl')
    last_price = df['price'].iloc[-1]
    predicted_price = model.predict([[last_price]])
    print(f"💲Preço previsto para o próximo dia: {predicted_price[0]}")
    
# Kafka Producer para enviar previsões
def kafka_producer():
    producer = KafkaProducer(bootstrap_servers='kafka:9093', value_serializer=lambda v: str(v).encode('utf-8'))
    while True:
        predicted_price = predict_price()
        producer.send('bitcoin_predictions', predicted_price)
        time.sleep(60) # Envia uma previsão a cada minuto