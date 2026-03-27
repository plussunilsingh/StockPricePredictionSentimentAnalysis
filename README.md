# Stock Price Prediction & Sentiment Analysis System

An end-to-end data-driven stock price prediction system that combines Technical Analysis (EMA, MACD, Bollinger Bands) with NLP-based Sentiment Analysis. Supporting major US and Indian market indices.

## 🚀 Features & Benefits

### Features
- **Multi-Asset Support**: Predict for AAPL, MSFT, GOOGL and Indian Indices like NIFTY 50, SENSEX, NIFTY BANK, NIFTY IT.
- **Hybrid Intelligence**: Combines technical indicators with market sentiment for holistic analysis.
- **Robust Model Options**: Toggle between **LSTM (Recurrent Neural Network)** for sequence learning and **Random Forest** for stable classification.
- **Interactive Dashboard**: Streamlit-based UI for real-time visualization and on-demand predictions.
- **Advanced Indicators**: Built-in support for EMA, MACD, RSI, and Bollinger Bands.

### Benefits
- **Better Decision Making**: Signals are backed by both math (Technical) and context (Sentiment).
- **Reduced Risk**: Multi-model verification helps identify high-confidence trades.
- **Actionable Insights**: Clear BUY/SELL/HOLD recommendations with confidence percentages.
- **Scalable Architecture**: Loosely coupled design allows easy integration of new models or data sources.

---

## 🏗 System Architecture

### 1. Overall System Integration Diagram
```mermaid
graph TD
    A[Frontend: Streamlit Dashboard] <--> B[Backend API: FastAPI]
    B --> C[Data Layer]
    C --> D[Stock Collector: CSV/yfinance]
    C --> E[News Collector: CSV/APIs]
    B --> F[ML Pipeline]
    F --> G[Feature Engineering]
    F --> H[Model Layer]
    H --> I[LSTM Model]
    H --> J[Random Forest Model]
    B --> K[Sentiment Analyzer: VADER]
```

### 2. Process Flow Diagram
```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant Model
    
    User->>Dashboard: Select Symbol & Model
    Dashboard->>API: POST /predict (symbol, model)
    API->>API: Fetch Stock & News Data
    API->>API: Feature Engineering (EMA, RSI, Sentiment)
    API->>Model: Run Prediction
    Model-->>API: Result (UP/DOWN + Confidence)
    API-->>Dashboard: JSON Result
    Dashboard->>User: Display Signal & Chart
```

### 3. Component Interaction Diagram
```mermaid
classDiagram
    class Dashboard {
        +selectSymbol()
        +requestPrediction()
    }
    class FastAPI {
        +trainModel()
        +getPrediction()
    }
    class FeatureEngineer {
        +addTechnicalIndicators()
        +mergeSentiment()
    }
    class ModelStrategy {
        <<interface>>
        +train()
        +predict()
    }
    
    Dashboard ..> FastAPI : HTTP Requests
    FastAPI --> FeatureEngineer : Preprocessing
    FastAPI --> ModelStrategy : Inference
    ModelStrategy <|-- LSTMModel
    ModelStrategy <|-- RandomForestModel
```

### 4. External System Interaction (Future Readiness)
```mermaid
graph LR
    System[Stock Prediction System] -- API Keys --> YF[Yahoo Finance API]
    System -- API Keys --> NEWS[NewsAPI.org]
    System -- Local Files --> CSV[Data Archive]
    User -- Browser --> System
```

---

## 🛠 Installation & Usage

The system is managed via the enterprise `manage.sh` script:

1. **Start System**: `./manage.sh start`
2. **Access Dashboard**: `http://localhost:8501`
3. **View Logs**: `./manage.sh logs`
4. **Stop System**: `./manage.sh stop`
5. **Check Status**: `./manage.sh status`

---

## 📂 Project Structure
- `com.stockprediction.backend`: FastAPI service and ML implementations.
- `com.stockprediction.frontend`: Streamlit dashboard.
- `data/`: CSV datasets for stocks and news.
- `scripts/`: Data generation and utility scripts.
- `tests/`: Automated backend verification tests.
