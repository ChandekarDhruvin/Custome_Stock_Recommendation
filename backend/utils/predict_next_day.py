import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from models.transformer_model import build_transformer_model

sentiment_cache = {}  # Store past sentiment scores


def fetch_past_sentiment(symbol, days=14):
    if symbol in sentiment_cache and len(sentiment_cache[symbol]) >= days:
        return sentiment_cache[symbol][-days:]  # Return last `days` scores
    else:
        return [0] * days  # Return neutral sentiment if no history exists


def predict_next_day_price(symbol):
    try:
        stock = yf.download(symbol, period="1y")  # Use 1 year for better training
        nifty = yf.download("^NSEI", period="1y")  

        if stock.empty or len(stock) < 14:  # Ensure enough data
            return None

        # Get close prices and calculate indicators
        close_prices = stock['Close'].values.reshape(-1, 1)
        nifty_trend = nifty['Close'].pct_change().fillna(0).values.reshape(-1, 1)
        ema_9 = stock['Close'].ewm(span=9, adjust=False).mean().values.reshape(-1, 1)
        ema_15 = stock['Close'].ewm(span=15, adjust=False).mean().values.reshape(-1, 1)

        # Ensure same length
        min_length = min(len(close_prices), len(nifty_trend), len(ema_9), len(ema_15))
        close_prices, nifty_trend, ema_9, ema_15 = (
            close_prices[-min_length:], nifty_trend[-min_length:], ema_9[-min_length:], ema_15[-min_length:]
        )

        # Fetch sentiment data (historical)
        sentiment_scores = fetch_past_sentiment(symbol, min_length)
        sentiment_series = np.array(sentiment_scores).reshape(-1, 1)

        # Combine into a dataset
        data = np.hstack([close_prices, nifty_trend, ema_15, ema_9, sentiment_series])

        # Scale data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # Prepare training data
        X, Y = [], []
        time_step = 14
        for i in range(len(scaled_data) - time_step):
            X.append(scaled_data[i:i+time_step])
            Y.append(0.7 * scaled_data[i+time_step][0] + 0.3 * np.mean(scaled_data[i:i+time_step, 0]))

        X, Y = np.array(X), np.array(Y)

        if len(X) < 10:
            return None

        # Train-test split
        train_size = int(len(X) * 0.8)
        X_train, Y_train = X[:train_size], Y[:train_size]

        # Train transformer model
        model = build_transformer_model((time_step, X.shape[-1]))
        model.fit(X_train, Y_train, epochs=20, batch_size=32, verbose=0)

        # Predict next day's price
        last_14_days = scaled_data[-time_step:].reshape(1, time_step, scaled_data.shape[1])
        predicted_price = model.predict(last_14_days)

        # Inverse transform correctly
        predicted_price = scaler.inverse_transform(
            [[predicted_price[0][0], nifty_trend[-1][0], ema_15[-1][0], ema_9[-1][0], sentiment_series[-1][0]]]
        )[0][0]

        return predicted_price
    except Exception as e:
        print(f"Error predicting price: {e}")
        return None
