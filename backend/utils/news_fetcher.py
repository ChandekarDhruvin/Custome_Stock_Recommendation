import requests
from bs4 import BeautifulSoup
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os
import numpy as np


load_dotenv()

sia = SentimentIntensityAnalyzer()
GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

BANKING_STOCKS = ["HDFCBANK.NS", "AXISBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS"]


def convert_symbol_to_query(symbol):
    """
    Converts stock symbols like 'TATAMOTORS.NS' or 'HDFCBANK.NS' to a proper news search term.
    - For banking stocks: Splits the name (e.g., 'HDFC BANK')
    - For others: Uses the stock name as it is
    """
    if symbol in BANKING_STOCKS:
        return symbol.replace(".NS", "").replace("BANK", " Bank")  # Converts 'HDFCBANK' → 'HDFC Bank'
    else:
        return symbol.replace(".NS", "")  # Keeps non-banking names intact



def fetch_gnews(symbol):
    query = f"{symbol} stock market OR share price OR NSE OR BSE"
    url = f"https://gnews.io/api/v4/search?q={query}&token={GNEWS_API_KEY}&lang=en&max=10"
    
    response = requests.get(url)
    data = response.json()
    return [article["title"] for article in data.get("articles", [])]

def fetch_yahoo_news(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return [a.text for a in soup.find_all("h3", class_="Mb(5px)")]

def fetch_alpha_vantage_news(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if "feed" in data:
            return [article["title"] for article in data["feed"][:10]]
        return []
    except Exception as e:
        print(f"Error fetching Alpha Vantage: {e}")
        return []
    

# Fetch Google News (Web Scraping)
def fetch_google_news(symbol):
    try:
        query = convert_symbol_to_query(symbol)
        search_url = f"https://www.google.com/search?q={query}+stock+news"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd")
        return [a.text for a in articles[:10]]
    except Exception as e:
        print(f"Error fetching Google News: {e}")
        return []


def fetch_all_news(symbol):
    print(f"\n🔍 Fetching news for {symbol}...\n")
    
    gnews_results = fetch_gnews(symbol)
    yahoo_results = fetch_yahoo_news(symbol)
    alpha_vantage_results = fetch_alpha_vantage_news(symbol)
    google_results = fetch_google_news(symbol)

    all_news = {
        "GNews": gnews_results,
        "Yahoo Finance": yahoo_results,
        "Alpha Vantage": alpha_vantage_results,
        "Google News": google_results
    }
    
    return all_news

def fetch_news_sentiment(symbol):
    try:
        headlines = fetch_all_news(symbol)  # You can also use fetch_yahoo_news
        if not headlines:
            return 0  # Neutral sentiment

        sentiment_scores = [sia.polarity_scores(headline)['compound'] for headline in headlines]
        
        # Apply time-based weighting (latest news gets higher impact)
        weights = np.linspace(1, 2, len(sentiment_scores))
        weighted_sentiment = sum(s * w for s, w in zip(sentiment_scores, weights)) / sum(weights)

        return round(weighted_sentiment, 2)
    except Exception as e:
        print(f"Error fetching sentiment: {e}")
        return 0