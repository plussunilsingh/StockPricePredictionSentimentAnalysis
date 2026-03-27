# 📊 Presentation: Stock Price Prediction & Sentiment Analysis

> **A Data-Driven Approach to Intelligent Trading signals.**

---

## 💡 The Core Idea
Financial markets are moved by **numbers** (Technical Data) and **narratives** (Market Sentiment). 
Our application bridges this gap by integrating **advanced ML models** with **real-time news analysis**.

### 🌟 Key Value Proposition
- **Hybrid Intelligence**: Technical Indicators + Sentiment Analysis.
- **Reliable Results**: Dual-model verification (LSTM & Random Forest).
- **Market Flexibility**: Out-of-the-box support for US & Indian Markets (Nifty, Sensex).

---

## 📈 Visual Showcase

### 🔍 Interactive Dashboard
The **Streamlit Dashboard** allows users to seamlessly explore different market indices and toggle between predictive models.

| Component | Functionality |
| :--- | :--- |
| **Market Selector** | Predefined US/Indian symbols + manual search. |
| **Model Toggle** | Switch between LSTM and Random Forest. |
| **Prediction Card** | High-visibility BUY/SELL signals with confidence. |
| **Trend Chart** | Real-time historical price trend visualization. |

### 🎯 Live Results (NIFTY 50)
The system provides clear, actionable signals that combine technical state with sentiment score.

![NIFTY 50 Prediction](file:///Users/suniltomar/.gemini/antigravity/brain/600be79b-d002-4a12-b643-56c8896c9366/nifty_50_results_1774615925317.png)
*NIFTY 50 prediction showing a high-confidence SELL signal during neutral sentiment.*

---

## 🏗 How it Works (Under the Hood)

1. **Data Ingestion**: Multi-source data collection (CSV Archive + Future API Hooks).
2. **Feature Engineering**: Computing 10+ features including **MACD**, **Bollinger Bands**, and **Sentiment Polarities**.
3. **ML Pipeline**: 
   - **LSTM**: Captures long-term dependencies in price sequences.
   - **RF**: Provides robust decision trees based on technical features.
4. **Decision Engine**: Normalizes model probabilities into simple BUY/SELL/HOLD recommendations.

---

## 💎 Features & Business Benefits

- **Search Anything**: Search any Indian index (Nifty Bank, IT, etc.) or US stock.
- **Risk Mitigation**: Confidence metrics help traders understand signal strength.
- **Ready for Scale**: Modular code follows clean-architecture principles for easy maintenance.

---

## 🏁 Conclusion
The **Stock Price Prediction & Sentiment Analysis System** is a powerful, production-ready starting point for data-driven financial analysis. It's ready for both local exploration and production deployment.

**Built with:** FastAPI, Streamlit, Scikit-learn, TensorFlow, and VADER.
