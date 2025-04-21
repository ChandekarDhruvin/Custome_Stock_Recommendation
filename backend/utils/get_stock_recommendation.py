
import yfinance as yf
from utils.stock_analysis import get_stock_indicators
from utils.news_fetcher import fetch_news_sentiment
def get_stock_recommendation(symbol):
    sentiment_score = fetch_news_sentiment(symbol)
    eps_growth, rsi, trend, buying_price = get_stock_indicators(symbol)

    # Fetch broader market (Nifty 50) & Banking sector trend (Bank Nifty)
    nifty = yf.Ticker("^NSEI").history(period="6mo")["Close"].pct_change().mean()
    bank_nifty = yf.Ticker("^NSEBANK").history(period="6mo")["Close"].pct_change().mean()

    # Fetch stock fundamentals
    stock = yf.Ticker(symbol)
    stock_info = stock.fast_info

    pe_ratio = stock_info.get("trailingPE", None)
    revenue_growth = stock_info.get("revenueGrowth", None)
    debt_to_equity = stock_info.get("debtToEquity", None)

    # Determine sector movement based on stock type
    banking_stocks = ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "SBIN.NS", "KOTAKBANK.NS"]
    sector_movement = bank_nifty if symbol in banking_stocks else nifty

    # Convert values safely
    try:
        eps_growth = float(eps_growth) if eps_growth != "N/A" else None
        rsi = float(rsi) if rsi != "N/A" else None
        pe_ratio = float(pe_ratio) if pe_ratio else None
        revenue_growth = float(revenue_growth) if revenue_growth else None
        debt_to_equity = float(debt_to_equity) if debt_to_equity else None
    except ValueError:
        return "Hold"

    # **Overbought Condition**
    if rsi and rsi > 70:
        return "Overbought - Potential Correction"

    # **Strong Long-Term Buy**
    if (eps_growth and eps_growth > 5) and (pe_ratio and pe_ratio < 30) and \
       (debt_to_equity and debt_to_equity < 1.5) and (rsi and rsi < 60) and \
       (sentiment_score > 0.3) and (sector_movement > 0):
        return "Strong Long-Term Buy"

    # **Moderate Long-Term Buy**
    elif (eps_growth and eps_growth > 4) and (pe_ratio and pe_ratio < 30) and \
         (debt_to_equity and debt_to_equity < 2) and (rsi and rsi < 65) and \
         (sentiment_score > -0.1) and (sector_movement > -0.1):
        return "Long-Term Buy"

    # **Sell Condition**
    elif (rsi and rsi > 75) or (sentiment_score < -0.4) or (debt_to_equity and debt_to_equity > 3):
        return "Sell"

    return "Hold"