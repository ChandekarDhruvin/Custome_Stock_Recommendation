

# Custom Stock Recommendation System

Welcome to the **Custom Stock Recommendation System**! This application provides real-time stock recommendations using machine learning and financial data analysis. The system analyzes stock market trends, evaluates market indicators, and provides personalized stock recommendations.

## 🚀 Project Overview

This system offers personalized stock suggestions by leveraging machine learning algorithms and financial data from various sources. It includes stock analysis features like sentiment analysis, real-time stock data fetching, and stock indicators such as EPS (Earnings Per Share), RSI (Relative Strength Index), and market trend analysis.

## 🔧 Features

- **Stock Sentiment Analysis**: Retrieves and analyzes news sentiment for a particular stock.
- **Stock Analysis**: Fetches stock indicators like EPS, RSI, trend, and recommended buying price.
- **Real-time Data**: Provides access to up-to-date stock data and financial news.
- **Machine Learning Integration**: Incorporates a transformer-based model for stock prediction and recommendation.

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Machine Learning**: TensorFlow (for the Transformer model)
- **Data Analysis**: Pandas, NumPy
- **Natural Language Processing**: NLTK (VADER Sentiment Analysis)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Flask API for communication between frontend and backend

## 📁 Project Structure

```
Custom_Stock_Recommendation_System/
├── backend/
│   ├── app.py               # Flask API backend
│   ├── transformer.py       # Transformer-based model for predictions
│   ├── utils/
│   │   ├── news_fetcher.py  # Fetches financial news and sentiment
│   │   ├── stock_analysis.py # Retrieves stock indicators
│   │   └── get_all_stock_data.py # Fetches historical stock data
├── frontend/
│   ├── index.html           # HTML frontend
│   ├── style.css            # CSS for frontend styling
│   └── script.js            # JavaScript to interact with the API
├── Images/                  # Folder for images (e.g., stock charts)
└── README.md                # This file
```

## 📥 Getting Started

### Prerequisites

- Python 3.x
- TensorFlow
- Flask
- NLTK
- Other Python dependencies (listed in `requirements.txt`)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ChandekarDhruvin/Custome_Stock_Recommendation.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Custom_Stock_Recommendation_System
   ```

3. Install required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask app:

   ```bash
   python backend/app.py
   ```

5. Open the frontend `index.html` in your browser or set up a local server to serve the frontend.

   ```bash
   open frontend/index.html
   ```

## 📡 API Endpoints

### 1. **Homepage**
- **GET** `/`
  - Serves the `index.html` page.

### 2. **Fetch Stock News**
- **GET** `/news/<symbol>`
  - Fetches the latest news for a given stock symbol.
  - **Example**: `/news/AAPL`

### 3. **Fetch News Sentiment**
- **GET** `/sentiment/<symbol>`
  - Fetches sentiment analysis of the news related to a stock.
  - **Example**: `/sentiment/AAPL`

### 4. **Stock Info**
- **GET** `/stock/<symbol>`
  - Retrieves key stock indicators such as EPS, RSI, Trend, and Buying Price for a given stock.
  - **Example**: `/stock/AAPL`

### 5. **Fetch All Stocks**
- **GET** `/api/get_all_stocks`
  - Retrieves data for all available stocks.

## 📈 Transformer Model

The transformer model is built using Keras and TensorFlow, providing advanced capabilities for stock prediction based on historical data and other indicators.

The model includes layers such as:
- **Multi-Head Attention**: Captures relationships between time steps in the sequence.
- **Feed Forward Network (FFN)**: Processes the attention output.
- **Normalization and Dropout**: Ensures stable training and avoids overfitting.

The model is compiled using **Adam** optimizer and **mean squared error** loss function, ideal for regression tasks.

```python
def build_transformer_model(input_shape, num_heads=4, ff_dim=128):
    inputs = Input(shape=input_shape)
    attn_output = MultiHeadAttention(num_heads=num_heads, key_dim=input_shape[-1])(inputs, inputs)
    attn_output = Dropout(0.1)(attn_output)
    out1 = LayerNormalization(epsilon=1e-6)(inputs + attn_output)
    
    ffn_output = Dense(ff_dim, activation="relu")(out1)
    ffn_output = Dense(input_shape[-1])(ffn_output)
    ffn_output = Dropout(0.1)(ffn_output)
    out2 = LayerNormalization(epsilon=1e-6)(out1 + ffn_output)
    
    outputs = Dense(1)(out2[:, -1, :])
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model
```
