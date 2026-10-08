from fastapi.testclient import TestClient
from calc_app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Microservice!"}

def test_calculate_multiply():
    payload = {"number1": 2, "operation": "*", "number2": 3}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    assert response.json() == {"result": 6.0}

def test_calculate_divide_by_zero():
    payload = {"number1": 5, "operation": "/", "number2": 0}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

def test_calculate_get_not_allowed():
    response = client.get("/calculate")
    assert response.status_code == 405

def test_calculate_invalid_number():
    payload = {"number1": "abc", "operation": "+", "number2": 2}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 422
    assert "error" in response.json()