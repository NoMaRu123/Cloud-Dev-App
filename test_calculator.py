import unittest
from calculator import calculate


class UnitTests(unittest.TestCase):
    def test_calculator_add(self):
        data = {
            "number1": 4,
            "operation": "+",
            "number2": 4
        }
        result = calculate(data)
        print("Result ", result["result"])
        self.assertEqual(result["result"], 8)

    def test_calculator_subtract(self):
        data = {
            "number1": 10,
            "operation": "-",
            "number2": 4
        }
        result = calculate(data)
        print("Result ", result["result"])
        self.assertEqual(result["result"], 6)

    def test_calculator_multiply(self):
        data = {
            "number1": 3,
            "operation": "*",
            "number2": 4
        }
        result = calculate(data)
        print("Result ", result["result"])
        self.assertEqual(result["result"], 12)

    def test_calculator_divide(self):
        data = {
            "number1": 4,
            "operation": "/",
            "number2": 4
        }
        result = calculate(data)
        print("Result ", result["result"])
        self.assertEqual(result["result"], 1)

    def test_calculator_division_by_zero(self):
        data = {
            "number1": 3,
            "operation": "/",
            "number2": 0
        }
        result = calculate(data)
        self.assertEqual(result[1], 400)
        self.assertIn("error", result[0])

    def test_calculator_invalid_operation(self):
        data = {
            "number1": 3,
            "operation": "%",
            "number2": 2
        }
        result = calculate(data)
        self.assertEqual(result[1], 400)
        self.assertIn("error", result[0])

    def test_calculator_missing_field(self):
        data = {
            "number1": 3,
            "number2": 2
        }
        result = calculate(data)
        self.assertEqual(result[1], 400)
        self.assertEqual(result[0]["error"], "Missing field: operation")

    def test_calculator_invalid_number(self):
        data = {
            "number1": "abc",
            "operation": "+",
            "number2": 2
        }
        result = calculate(data)
        self.assertEqual(result[1], 400)
        self.assertIn("error", result[0])


if __name__ == '__main__':
    unittest.main()
