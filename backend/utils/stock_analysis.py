import yfinance as yf
import numpy as np
from utils.news_fetcher import fetch_news_sentiment

def get_stock_indicators(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="6mo")
        
        if hist.empty:
            return "N/A", "N/A", "Unknown", "N/A"
        
        eps_growth = stock.info.get("trailingEps", None)
        close_prices = hist["Close"].dropna()

        # Compute RSI
        delta = close_prices.diff() 
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = round(float(rsi.iloc[-1]), 2) if not np.isnan(rsi.iloc[-1]) else "N/A"

        # Moving Averages
        ma_20 = close_prices.rolling(window=20).mean()
        ma_50 = close_prices.rolling(window=50).mean()
        ma_200 = close_prices.rolling(window=200).mean()

        # Dynamic threshold based on volatility
        volatility = close_prices.pct_change().rolling(20).std().iloc[-1] * 100
        threshold = max(0.5, volatility)  # Adaptive threshold
        sentiment_score = fetch_news_sentiment(symbol)


        # Trend determination
        if ma_20.iloc[-1] > ma_50.iloc[-1] > ma_200.iloc[-1]:
            trend = "Strong Uptrend"
        elif ma_20.iloc[-1] > ma_50.iloc[-1]:
            trend = "Uptrend"
        elif ma_20.iloc[-1] < ma_50.iloc[-1] < ma_200.iloc[-1]:
            trend = "Strong Downtrend"
        elif ma_20.iloc[-1] < ma_50.iloc[-1]:
            trend = "Downtrend"
        else:
            trend = "Sideways"

        if sentiment_score > 0.5:  # Strong bullish sentiment
            if "Downtrend" in trend:
                trend = "Possible Reversal Up (Sentiment-Based)"
            elif trend == "Uptrend":
                trend = "Strong Uptrend (Sentiment Confirmed)"

        elif sentiment_score < -0.5:  # Strong bearish sentiment
            if "Uptrend" in trend:
                trend = "Possible Reversal Down (Sentiment-Based)"
            elif trend == "Downtrend":
                trend = "Strong Downtrend (Sentiment Confirmed)"
                
        # Confirm trend with RSI
        if rsi_value < 30 and "Downtrend" in trend:
            trend += " (Oversold - Reversal Possible)"
        elif rsi_value > 70 and "Uptrend" in trend:
            trend += " (Overbought - Pullback Possible)"

        buying_price = get_buying_price(stock)
        
        return round(float(eps_growth), 2) if eps_growth else "N/A", rsi_value, trend, buying_price
    except Exception as e:
        return "N/A", "N/A", "Unknown", "N/A"


def get_buying_price(stock):
    try:
        hist = stock.history(period="1y")
        if hist.empty:
            return "N/A"

        close_prices = hist["Close"]
        ma_60 = close_prices.rolling(window=60).mean()
        ma_200 = close_prices.rolling(window=200).mean()
        
        current_price = close_prices.iloc[-1]
        rsi_value = compute_rsi(close_prices)

        # Compute Bollinger Bands
        rolling_mean = close_prices.rolling(window=20).mean()
        rolling_std = close_prices.rolling(window=20).std()
        bb_lower = rolling_mean - (2 * rolling_std)

        # Print debug values
        print(f"========={stock}")
        print(f"Current Price: {current_price}")
        print(f"RSI: {rsi_value}")
        print(f"MA 60: {ma_60.iloc[-1]}")
        print(f"MA 200: {ma_200.iloc[-1]}")
        print(f"Lower Bollinger Band: {bb_lower.iloc[-1]}")
        print(f"100-day Low: {min(close_prices[-100:])}")

        # Define support level dynamically
        if rsi_value < 30:  # Strongly oversold
            support_level = min(close_prices[-100:])  # Buy at 100-day low
        elif rsi_value < 55 and current_price < bb_lower.iloc[-1]:  
            support_level = bb_lower.iloc[-1]  # Buy near lower Bollinger Band
        elif current_price > ma_60.iloc[-1]:
            support_level = ma_60.iloc[-1]
        elif current_price > ma_200.iloc[-1] * 1.02:  # Avoid false breakdowns
            support_level = ma_200.iloc[-1]
        else:
            support_level = min(close_prices[-100:])  # Default strong support level

        print(f"Final Buying Price: {support_level}")  # Debugging Output

        return round(float(support_level), 2) if not np.isnan(support_level) else "N/A"
    
    except Exception as e:
        print(f"Error calculating buying price: {e}")
        return "N/A"



def compute_rsi(close_prices, window=14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2) if not np.isnan(rsi.iloc[-1]) else "N/A"

