import requests
import time

BASE_URL = "http://localhost:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print("Root test passed!")

def test_train():
    payload = {
        "symbol": "AAPL",
        "startDate": "2026-03-01",
        "endDate": "2026-03-15",
        "useMock": True
    }
    response = requests.post(f"{BASE_URL}/train", json=payload)
    if response.status_code != 200:
        print(f"Train failed: {response.json()}")
    assert response.status_code == 200
    print("Train test passed!")

def test_predict():
    payload = {
        "symbol": "AAPL",
        "startDate": "2026-03-01",
        "endDate": "2026-03-15",
        "useMock": True
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    if response.status_code != 200:
        print(f"Predict failed: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "decision" in data
    print(f"Predict test passed! Result: {data}")

if __name__ == "__main__":
    try:
        test_root()
        test_train()
        test_predict()
    except Exception as e:
        print(f"Tests failed: {e}")
