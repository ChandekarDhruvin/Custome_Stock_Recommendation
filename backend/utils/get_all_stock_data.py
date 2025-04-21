from utils.stock_analysis import get_stock_indicators
from utils.predict_next_day import predict_next_day_price
from utils.get_stock_recommendation import get_stock_recommendation
import yfinance as yf
import pandas as pd


CUSTOM_STOCKS = [
    "ZOMATO.NS", "IRFC.NS", "RELIANCE.NS"
    # , "HDFCBANK.NS", "ICICIBANK.NS"
    # "AXISBANK.NS", "DIXON.NS", "DIVISLAB.NS", "TATAMOTORS.NS", "RVNL.NS", "ITC.NS",
    # "TIPSMUSIC.NS"
]


def fetch_stock_data():
    try:
        data = yf.download(CUSTOM_STOCKS, period="1y")
        
        if data.empty:
            return {"error": "Failed to fetch stock data"}
        
        close_prices = data.get("Close", pd.DataFrame())
        open_prices = data.get("Open", pd.DataFrame())
        
        daily_change_percent = ((close_prices - open_prices) / open_prices) * 100
        
        result = []
        
        for stock in CUSTOM_STOCKS:
            if stock in close_prices.columns:
                eps_growth, rsi, trend, buying_price = get_stock_indicators(stock)
                future_price = predict_next_day_price(stock)
                recommendation = get_stock_recommendation(stock)
                
                result.append({
                    "symbol": stock,
                    "current_price": round(float(close_prices[stock].iloc[-1]), 2),
                    "daily_change_percent": round(float(daily_change_percent[stock].iloc[-1]), 2),
                    "eps_growth": eps_growth,
                    "future_price": round(float(future_price), 2) if future_price else "N/A",
                    "rsi": rsi,
                    "trend": trend,
                    "buying_price": buying_price,
                    "recommendation": recommendation
                })
        
        return sorted(result, key=lambda x: x["daily_change_percent"], reverse=True)
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return {"error": f"Error fetching stock data: {str(e)}"}