def calculate(payload):
    try:
        number1 = float(payload["number1"])
        number2 = float(payload["number2"])
        operation = payload["operation"]

        if operation == "+":
            result = number1 + number2
        elif operation == "-":
            result = number1 - number2
        elif operation == "*":
            result = number1 * number2
        elif operation == "/":
            result = number1/number2
        else:
            return {"error":"Invalid Operation: Use +,-,*,/ "}, 400
        
        return {"result": result}

    except KeyError as e:
        return {"error": f"Missing field: {e.args[0]}"}, 400 # for missing field Operation
    except (ValueError, TypeError):
         return {"error": "number1 and number2 must be valid numbers"}, 400
    except ZeroDivisionError:
        return {"error":"Cannot devided by zero"}, 400