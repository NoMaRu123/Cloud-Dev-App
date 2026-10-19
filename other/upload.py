import csv          # reads CSV files
import requests     # sends HTTP requests from Python (like fetch in JavaScript)

URL = "http://127.0.0.1:8000/items/"   # trailing slash: must match the route exactly
insertions = 0                          # how many rows were accepted

# utf-8 so names with accents read correctly; newline="" is what the csv module expects
with open("MOCK_DATA.csv", encoding="utf-8", newline="") as csv_file:
    reader = csv.DictReader(csv_file)   # each row becomes a dict: {"name": ..., "description": ...}
    for row in reader:
        response = requests.post(URL, json=row)   # send this row to the API as JSON
        if response.status_code == 200:
            insertions += 1                       # accepted
        else:
            print(row, response.status_code)      # rejected: show which row and why (409 = duplicate)

print(f"Total insertions: {insertions}")
