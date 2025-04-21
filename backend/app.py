from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import nltk
import sys
from flask_cors import CORS


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from utils.news_fetcher import fetch_all_news, fetch_news_sentiment
from utils.stock_analysis import get_stock_indicators
from utils.get_all_stock_data import fetch_stock_data

app = Flask(__name__, template_folder='../frontend')
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow frontend requests to API

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

nltk.download('vader_lexicon')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news/<symbol>')
def get_news(symbol):
    return jsonify(fetch_all_news(symbol))

@app.route('/sentiment/<symbol>')
def get_sentiment(symbol):
    return jsonify({"sentiment": fetch_news_sentiment(symbol)})

@app.route('/stock/<symbol>')
def stock_info(symbol):
    eps, rsi, trend, price = get_stock_indicators(symbol)
    return jsonify({"EPS": eps, "RSI": rsi, "Trend": trend, "Buying Price": price})


@app.route('/api/get_all_stocks', methods=['GET'])
def get_all_stocks():
    return jsonify(fetch_stock_data())

if __name__ == '__main__':
    app.run(debug=True)

