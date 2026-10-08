from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from calculator import calculate

# Note: FileResponse sends a file back as-is. 
# BaseModel comes from Pydantic, the validation library FastAPI is built on. 

app = FastAPI() # Create the App

class CalcRequest(BaseModel): # Describes the shape of the JSON you expect
    number1: float # json that returns must have this and it's number!
    operation: str
    number2: float

@app.get("/")
def read_root():
    return {"message": "Hello, Microservice!"}

@app.post("/calculate")
def calculate_route(request: CalcRequest):
    result = calculate(request.model_dump())
    if isinstance(result, tuple):
        body, status = result
        return JSONResponse(content=body, status_code=status)
    return result

@app.get("/ui")
def ui():
    return FileResponse("templates/calculator.html")

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    first = exc.errors()[0]
    field = first["loc"][-1]
    return JSONResponse(status_code=422, content={"error": f"{field}: {first['msg']}"})
