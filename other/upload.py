import csv
import sys          # NEW: lets the script read what you type after its name
import time         # NEW: to measure how long the upload takes
import requests

# NEW: use the URL typed on the command line, or the local backend if none is given
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/items/"
insertions = 0
start = time.perf_counter()             # NEW: start the stopwatch

with open("MOCK_DATA.csv", encoding="utf-8", newline="") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        response = requests.post(URL, json=row)
        if response.status_code == 200:
            insertions += 1
        else:
            print(row, response.status_code)

elapsed = time.perf_counter() - start   # NEW: stop the stopwatch
print(f"Total insertions: {insertions} to {URL} in {elapsed:.1f} seconds")