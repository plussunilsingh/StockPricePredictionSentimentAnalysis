import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print("Root test passed!")

def test_train_rf():
    payload = {
        "symbol": "MSFT",
        "startDate": "2026-01-01",
        "endDate": "2026-03-31",
        "useMock": True,
        "modelType": "RF"
    }
    response = requests.post(f"{BASE_URL}/train", json=payload)
    assert response.status_code == 200
    print("Train RF MSFT test passed!")

def test_predict_rf():
    payload = {
        "symbol": "MSFT",
        "startDate": "2026-01-01",
        "endDate": "2026-03-31",
        "useMock": True,
        "modelType": "RF"
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["modelUsed"] == "RF"
    print(f"Predict RF MSFT test passed! Result: {data}")

def test_predict_googl():
    payload = {
        "symbol": "GOOGL",
        "startDate": "2026-01-01",
        "endDate": "2026-03-31",
        "useMock": True,
        "modelType": "RF"
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"Predict RF GOOGL test passed! Result: {data}")

def test_predict_nsei():
    payload = {
        "symbol": "NSEI",
        "startDate": "2026-01-01",
        "endDate": "2026-03-31",
        "useMock": True,
        "modelType": "RF"
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"Predict RF NSEI test passed! Result: {data}")

if __name__ == "__main__":
    try:
        test_root()
        test_train_rf()
        test_predict_rf()
        test_predict_googl()
        test_predict_nsei()
    except Exception as e:
        print(f"Tests failed: {e}")
