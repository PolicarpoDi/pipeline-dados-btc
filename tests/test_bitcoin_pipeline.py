import pandas as pd
import pytest

from app.bitcoin_pipeline import get_bitcoin_data, train_model


def test_get_bitcoin_data():
    # Teste que verifica se os dados retornados são um Dataframe
    data = get_bitcoin_data()
    assert isinstance(data, pd.Dataframe)
    assert 'timestamp' in data.columns
    assert 'price' in data.columns
    
def test_train_model():
    # Teste que verifica se o modelo é treinado corretamente
    model = train_model()
    assert model is not None