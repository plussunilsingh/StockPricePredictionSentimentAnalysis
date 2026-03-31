# 🔗 Backend API Implementation Guide

The Stock Prediction System provides an enterprise-ready FastAPI backend that produces predictive market intelligence via RESTful endpoints.

## 📡 1. Endpoints Overview

### `POST /predict`
The primary endpoint for generating predictive market intelligence.

#### Request Payload (`PredictionRequestDTO`)
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | `"NSEI"` | The Ticker Symbol (e.g. RELIANCE.NS, AAPL). |
| `modelType` | `string` | `"RF"` | The model engine to use (`RF` or `LSTM`). |
| `startDate` | `string` | `"2026-01-01"` | ISO Date (YYYY-MM-DD) for training/history start. |
| `endDate` | `string` | `"2026-03-28"` | ISO Date (YYYY-MM-DD) for prediction target. |
| `useMock` | `boolean` | `true` | Set to `false` for live Yahoo Finance data fetching. |

---

## 🛠 2. Example API Usage (curl)

### A. Predict for Reliance (Indian Market - Mock Mode)
```bash
curl -X POST http://127.0.0.1:8000/predict \
     -H "Content-Type: application/json" \
     -d '{
           "symbol": "RELIANCE.NS",
           "modelType": "RF",
           "startDate": "2026-01-01",
           "endDate": "2026-03-28",
           "useMock": true
         }'
```

### B. Predict for Apple (Global Market - Live Mode)
```bash
curl -X POST http://127.0.0.1:8000/predict \
     -H "Content-Type: application/json" \
     -d '{
           "symbol": "AAPL",
           "modelType": "RF",
           "startDate": "2026-02-01",
           "endDate": "2026-03-28",
           "useMock": false
         }'
```

---

## 🏗 3. Response Schema
```json
{
  "symbol": "RELIANCE.NS",
  "prediction": "DOWN",
  "confidence": 0.58,
  "decision": "HOLD",
  "modelUsed": "RF",
  "lastClose": 2884.7,
  "changePercent": -1.2
}
```

---

## 🌐 4. Interactive SWAGGER Documentation
The backend provides interactive OpenAPI (Swagger) documentation. Once the backend is started, visit:
**`http://localhost:8000/docs`**

Use this interface to test different combinations of models and symbols directly from your browser.
