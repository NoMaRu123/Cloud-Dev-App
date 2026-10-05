from hello_flask import app

client = app.test_client()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Hello, Microservice!"}

def test_calculate_multiply():
    payload = {"number1": 2, "operation": "*", "number2": 3}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    assert response.get_json() == {"result": 6.0}

def test_calculate_divide_by_zero():
    payload = {"number1": 5, "operation": "/", "number2": 0}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_calculate_get_not_allowed():
    response = client.get("/calculate")
    assert response.status_code == 405
