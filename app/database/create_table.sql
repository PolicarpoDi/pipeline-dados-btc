CREATE SCHEMA IF NOT EXISTS predict_btc;

CREATE TABLE IF NOT EXISTS predict_btc.bitcoin_predictions (
    id SERIAL PRIMARY KEY,
    prediction_date TIMESTAMP NOT NULL,
    predicted_price DECIMAL(15, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS predict_btc.btc_movements (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    predicted_movement VARCHAR(10) NOT NULL  -- 'Subida' ou 'Descida'
);
