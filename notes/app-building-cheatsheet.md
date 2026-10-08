# App-building cheatsheet

Patterns from the Cloud App Dev lab (BSHC4SDFD) to look up when building my own app.
Each section is short on purpose. Explanations are linked where a longer version exists.

**Contents**
1. [Page talks to API: the 5-step pattern](#1-page-talks-to-api-the-5-step-pattern)
2. [Inside a FastAPI route: the request journey](#2-inside-a-fastapi-route-the-request-journey)
3. [Error handling: one consistent shape](#3-error-handling-one-consistent-shape)
4. [Where each error comes from](#4-where-each-error-comes-from)
5. [Debugging checklist](#5-debugging-checklist)
6. [Reading a response in JavaScript](#6-reading-a-response-in-javascript)
7. [Methods vs properties: when to use `()`](#7-methods-vs-properties-when-to-use-)
8. [Testing an API](#8-testing-an-api)
9. [Project setup commands](#9-project-setup-commands)

---

## 1. Page talks to API: the 5-step pattern

Front-end (browser JavaScript):
```js
async function doSomething() {
  const output = document.getElementById("output");

  // 1. READ inputs from the page
  const payload = { field: document.getElementById("field").value };

  try {
    // 2. SEND them to the API
    const response = await fetch("/your-endpoint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    // 3. PARSE the reply
    const data = await response.json();

    // 4. DECIDE success or error, using the status code
    if (response.ok) {
      // 5. SHOW the result
      output.textContent = data.something;
    } else {
      output.textContent = "Error: " + (data.error ?? "request failed (" + response.status + ")");
    }
  } catch (err) {
    output.textContent = "Error: no valid reply from the server";
    console.error(err);
  }
}
```

Back-end (FastAPI):
```python
class YourRequest(BaseModel):     # must match the payload keys
    field: str

@app.post("/your-endpoint")       # must match the fetch URL + method
def your_endpoint(request: YourRequest):
    return {"something": ...}     # must match what the page reads
```

**The 4 agreements.** Front-end and back-end must match on:

| | Front-end | Back-end |
|---|---|---|
| URL | `fetch("/x")` | `@app.post("/x")` |
| Method | `method: "POST"` | `@app.post` |
| Request shape | payload keys | `BaseModel` fields |
| Response shape | `data.something` / `data.error` | returned dict keys |

If **any** of them disagree, the page shows `undefined` or an error.

**Same server vs different server:** `fetch("/x")` works when the page is served by the same app (same port). A separate front-end (React on :3000 calling the API on :8000) needs the full URL **and** `CORSMiddleware` on the back-end.

Full line-by-line explanation: [calculator-html-explained.md](calculator-html-explained.md)

---

## 2. Inside a FastAPI route: the request journey

### The journey (user click → my function → reply)
```
BROWSER   click → JS reads inputs (always STRINGS, "2") → JSON.stringify → fetch POST /calculate
SERVER    uvicorn receives it → hands it to the FastAPI app
          ROUTER     finds the function for POST + /calculate      (none → 404, wrong method → 405)
          PARAMETERS reads the type hints → "CalcRequest = read the JSON body"
          PYDANTIC   validates + converts each field ("2" → 2.0)   (fails → 422, my function never runs)
          builds the CalcRequest object → CALLS my function with it
MY CODE   calculate_route(request) runs with data that's already valid
REPLY     return a dict → FastAPI turns it into JSON text (200) → browser → response.json() → page
```
**Key idea:** by the time my first line runs, the input is already checked. I never call the route function myself. FastAPI calls it.

### `request: CalcRequest` = parameter NAME : TYPE HINT
```python
def calculate_route(request: CalcRequest):
#                   ───────  ───────────
#                   any name  the type: FastAPI READS this
```
Normal Python ignores type hints. **FastAPI uses them to decide where the data comes from:**

| Parameter looks like | FastAPI gets it from | Example |
|---|---|---|
| `item: SomeBaseModel` | **JSON body** (validated) | `def create_item(item: ItemCreate)` |
| `item_id: int`, with `{item_id}` in the path | **URL path** | `@app.get("/items/{item_id}")` |
| `skip: int = 0`, not in the path | **query string** | `/items?skip=0&limit=10` |

### The function, line by line
```python
@app.post("/calculate")                          # route: POST + this URL → this function
def calculate_route(request: CalcRequest):        # FastAPI passes in the validated object
    result = calculate(request.model_dump())      # object → dict → my maths function
    if isinstance(result, tuple):                 # my calculate() returns a TUPLE on error
        body, status = result                     # unpack: ({"error": ...}, 400)
        return JSONResponse(content=body, status_code=status)  # error, with the right status
    return result                                 # success dict → JSON, 200
```

- **Pydantic object vs dict:** `request.number1` (dot) on the object, `payload["number1"]` (brackets) on a dict. `.model_dump()` converts **object → dict**. It's needed because `calculate()` uses brackets.
- **Flask vs FastAPI tuples:** Flask understands `return (dict, 400)`. **FastAPI doesn't**: it would send the tuple as a list with status 200. Use `JSONResponse(..., status_code=...)`.
- **Right side of `=`:** you can only use names that **already exist** (parameters, imports, earlier variables), never the one being created on that line. `result = calculate(result...)` crashes.

---

## 3. Error handling: one consistent shape

**Rule:** every error the API returns should have the **same JSON shape**, so the front-end only needs one line to display it. In this lab the shape is:
```json
{"error": "human-readable message"}
```

### Errors my own code raises
Return a `JSONResponse` with the shape and a status code:
```python
from fastapi.responses import JSONResponse

return JSONResponse(status_code=400, content={"error": "Cannot divide by zero"})
```
Or raise `HTTPException`. Note that this uses the key `detail`, not `error`, so don't mix the two in one app:
```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Item not found")
```

### Errors FastAPI raises for me (422 validation)
By default FastAPI replies with `{"detail": [ {...}, ... ]}`, which is a different shape.
To make it match, register an **exception handler** once, near the top of the app:
```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    first = exc.errors()[0]              # the first thing that was wrong
    field = first["loc"][-1]             # which field, e.g. "number1"
    return JSONResponse(
        status_code=422,
        content={"error": f"{field}: {first['msg']}"}
    )
```
Result (tested):
| Input | Reply |
|---|---|
| `"number1": "abc"` | `422 {"error": "number1: Input should be a valid number, ..."}` |
| `operation` missing | `422 {"error": "operation: Field required"}` |

Now **every** error has an `error` key, and the front-end's `data.error` always works.

### Don't weaken the types to get your own error message
Changing `number1: float` to `number1: str` *looks* like it lets my own `try/except` produce the error. But tested, it **breaks** normal requests: Pydantic v2 won't turn a JSON number `2` into a string, so `{"number1": 2}` gets a 422. Keep the real types, and customise the error with a handler instead.

---

## 4. Where each error comes from

The front-end **doesn't decide** error messages. It prints whatever text arrives in `data.error`. The message is written by whichever layer stopped the request:

| Request | Stopped by | Status | Body (before the handler) |
|---|---|---|---|
| Wrong URL | FastAPI router | 404 | `{"detail": "Not Found"}` |
| Wrong method (GET on a POST route) | FastAPI router | 405 | `{"detail": "Method Not Allowed"}` |
| Bad/missing field | Pydantic (`BaseModel`) | 422 | `{"detail": [ ... ]}` |
| `5 / 0`, bad operation | My code (`calculator.py`) | 400 | `{"error": "..."}` |
| Bug in my code | Python crash | 500 | `Internal Server Error` (**plain text, not JSON**) |

Order: router → Pydantic → my code. A request that fails an earlier layer **never reaches** the later ones. For example, `"abc"` never reaches `calculator.py`.

---

## 5. Debugging checklist

When the page shows something vague ("undefined", nothing at all):

1. **Browser DevTools → Network tab:** click the request and check:
   - **Status code.** That tells you which layer failed (table above).
   - **Response tab.** What did the server *actually* send?
   - **Request URL and method.** Do they match the route?
2. **Server terminal:** read the traceback. The **last lines** name the error and the file/line.
3. **`/openapi.json` or `/docs`:** shows the routes FastAPI *really* registered, which can differ from what I think I wrote.
4. **DevTools → Console:** front-end JavaScript errors and `console.log` output.
5. If `.json()` fails, temporarily use `await response.text()` and `console.log` it to see the raw reply.

---

## 6. Reading a response in JavaScript

| Method | Gives | Use for |
|---|---|---|
| `response.json()` | JS object | APIs |
| `response.text()` | string | HTML, plain text, debugging |
| `response.blob()` | binary | images, files |
| `response.ok` | `true` for 2xx | deciding success vs error |
| `response.status` | number (200, 404...) | showing or handling specific codes |

- The body can only be read **once**.
- `.json()` **throws** if the body isn't JSON (e.g. a 500 crash page).
- JS ↔ Python: `JSON.parse` ↔ `json.loads`, and `JSON.stringify` ↔ `json.dumps`.
- A missing key gives `undefined` in JS (Python raises `KeyError`). Use `value ?? "fallback"` to avoid displaying it.

---

## 7. Methods vs properties: when to use `()`

**`()` = do something. No `()` = read a value that's already stored.**

| | Method (needs `()`) | Property (no `()`) |
|---|---|---|
| Meaning | "go and **do** this work" | "**give me** this stored value" |
| Examples | `response.json()`, `JSON.stringify(x)`, `getElementById("id")` | `response.ok`, `response.status`, `data.result`, `output.textContent` |
| Python equivalent | `my_list.append(5)`, `response.json()` | `response.status_code`, `request.number1` |

- `response.json()` is a method because it has **work to do** (read the body, parse it). That's also why it needs `await`.
- `response.status` is a property because the answer **already arrived** with the reply.
- Some properties can be **assigned** too: `output.textContent = "Hi"` changes the page.

**Mix-ups:**
```js
response.json      // no () → you get the function itself, not the data
data.result()      // () on a value → TypeError: data.result is not a function
```
"**... is not a function**" means you put `()` on something that's a value.

**How to tell which is which:** the first time you use something, check the docs (MDN for JavaScript). They label each one as either a "method" or a "property". After a while it becomes intuitive: **verbs** like `json`, `stringify` and `getElementById` are methods, and **nouns** like `ok`, `status` and `result` are properties.

---

## 8. Testing an API

**Arrange → Act → Assert:**
```python
from fastapi.testclient import TestClient     # Flask: app.test_client()
from my_app import app

client = TestClient(app)

def test_something():
    payload = {"field": "value"}                       # Arrange
    response = client.post("/endpoint", json=payload)  # Act
    assert response.status_code == 200                 # Assert status
    assert response.json() == {"something": "..."}     # Assert body
```
- Function names must start with `test_`, or pytest won't collect them.
- Check the **body**, not only the status. A test that can't fail isn't testing anything.
- To check a key exists without fixing the message text: `assert "error" in response.json()`
- Test the error paths too: 400 (my errors), 404/405 (routing), 422 (validation).
- Flask uses `response.get_json()`, FastAPI uses `response.json()`.
- Unit test = call a function directly. Integration test = call the app over HTTP with a test client.

---

## 9. Project setup commands

### Virtual environment (Windows PowerShell)
```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
- A venv **can't be moved**. If the folder moves, delete `venv` and recreate it.
- Save dependencies as UTF-8 (on PowerShell 5.1, a plain `>` writes UTF-16):
  ```
  pip freeze | Out-File -Encoding utf8 requirements.txt
  ```

### Running
```
uvicorn calc_app:app --reload          # FastAPI → http://127.0.0.1:8000  (/docs = Swagger)
python -m flask --app hello_flask run  # Flask   → http://127.0.0.1:5000
pytest                                 # run all test_*.py files
```

### Git
```
git init                               # once per project
git remote add origin <url>            # once, link to GitHub
git push -u origin main                # first push

git add .                              # every time after that
git commit -m "what and why"
git push
```
- `.gitignore` should contain at least `venv/`, `__pycache__/`, `.pytest_cache/`.
- Never commit passwords, tokens or `.env` files.
