import os
from unittest.mock import MagicMock, patch

import pytest
from bitcoin_pipeline import (get_bitcoin_data, kafka_producer,
                              predict_price_and_movement, train_model)
from pyspark.sql import SparkSession


# Fixture para iniciar e parar o SparkSession
@pytest.fixture(scope="module")
def spark():
    spark_session = SparkSession.builder.appName("BitcoinPipelineTest").getOrCreate()
    yield spark_session
    spark_session.stop()

# Testando a função get_bitcoin_data
@patch("requests.get")
def test_get_bitcoin_data(mock_get, spark):
    # Mock da resposta da API
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'prices': [
            [1609459200000, 30000],
            [1609545600000, 32000]
        ]
    }
    mock_get.return_value = mock_response

    # Chamando a função
    df = get_bitcoin_data()

    # Verificando se o DataFrame foi criado corretamente
    assert df.count() == 2
    assert df.columns == ["timestamp", "price"]

# Testando a função train_model
@patch("bitcoin_pipeline.get_bitcoin_data")
def test_train_model(mock_get_bitcoin_data):
    spark = SparkSession.builder.master("local").appName("test").getOrCreate()

    # Criando um mock do DataFrame com preços variados
    mock_get_bitcoin_data.return_value = spark.createDataFrame(
        [
            (1609459200000, 30000), 
            (1609545600000, 32000), 
            (1609632000000, 28000),  # Queda (gera classe 0)
            (1609718400000, 35000),  # Subida (gera classe 1)
            (1609804800000, 34000),  # Queda (gera classe 0)
            (1609891200000, 36000),  # Subida (gera classe 1)
        ],  
        ["timestamp", "price"]
    )

    # Chamando a função train_model
    result = train_model()

    # Verificando o retorno da função
    assert result == "Modelo treinado com sucesso"

    # Verificando se os modelos foram salvos corretamente
    assert os.path.exists("bitcoin_price_model.pkl")
    assert os.path.exists("bitcoin_movement_model.pkl")

# Testando a função predict_price_and_movement
@patch("bitcoin_pipeline.get_bitcoin_data")
@patch("joblib.load")
def test_predict_price_and_movement(mock_load, mock_get_bitcoin_data, spark):
    # Mock do DataFrame de entrada
    mock_get_bitcoin_data.return_value = spark.createDataFrame(
        [(1609459200000, 30000), (1609545600000, 32000)],
        ["timestamp", "price"]
    )

    # Mock dos modelos carregados
    mock_model_price = MagicMock()
    mock_model_price.predict.return_value = [32000]
    
    mock_model_movement = MagicMock()
    mock_model_movement.predict.return_value = [1]
    
    mock_load.side_effect = [mock_model_price, mock_model_movement]

    predicted_price, movement_label = predict_price_and_movement()

    # Verificando as previsões
    assert predicted_price == 32000
    assert movement_label == "Subida"

# Testando a função kafka_producer
@patch("bitcoin_pipeline.KafkaProducer")
def test_kafka_producer(mock_kafka_producer):
    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    predicted_price = 32000

    # Chamando a função para enviar para Kafka
    kafka_producer(predicted_price)

    # Verificando se o send foi chamado corretamente
    mock_producer.send.assert_called_with('bitcoin_predictions', predicted_price)
    mock_producer.flush.assert_called_once()
    mock_producer.close.assert_called_once()

# Testando a função kafka_producer com preço inválido
@patch("bitcoin_pipeline.KafkaProducer")
def test_kafka_producer_no_price(mock_kafka_producer):
    mock_producer = MagicMock()
    mock_kafka_producer.return_value = mock_producer

    predicted_price = None

    # Chamando a função com preço inválido
    kafka_producer(predicted_price)

    # Verificando que nada foi enviado
    mock_producer.send.assert_not_called()
    mock_producer.flush.assert_called_once()
    mock_producer.close.assert_called_once()
