from flask import Flask, request, render_template
from calculator import calculate

app = Flask(__name__)

@app.route("/")
def read_root():
    return {"message": "Hello, Microservice!"}

@app.post("/endpoint")
def function_name():
    data = request.get_json()
    return {"message": "Success", "data": data}

@app.post("/calculate")
def calculate_route():
    payload = request.get_json()
    return calculate(payload)

@app.get("/ui")
def ui():
    return render_template("calculator.html")