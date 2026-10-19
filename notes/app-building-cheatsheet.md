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
10. [Relative paths vs `__file__`](#10-relative-paths-vs-__file__)
11. [Route order, static files and health checks](#11-route-order-static-files-and-health-checks)
12. [CORS on one page](#12-cors-on-one-page)

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
- Never commit passwords or tokens. An `.env` file that holds **secrets** stays out of Git. A settings-only one, like `.env.development` with just a localhost URL, is fine to commit.

### Front-end (Vite + React)
```
npm create vite@latest frontend     # once: pick React, JavaScript
npm install                         # like pip install -r requirements.txt → fills node_modules/
npx vite                            # dev server, http://localhost:5173, reloads on save
npx vite --host                     # same, but open to other devices on the Wi-Fi
npm run build                       # production files → dist/
```
- `package.json` = requirements.txt, `node_modules/` = venv (never committed), `package-lock.json` = exact versions (**do** commit).
- **PowerShell swallows a bare `--`**, so `npm run dev -- --host` loses the flag. Use `npx vite --host`.

---

## 10. Relative paths vs `__file__`

**A relative path is measured from the folder the program was STARTED in** (the "current folder"), **not** from the file the code is written in.

```python
"./test.db"            # current folder → depends on where you ran uvicorn / pytest
"../frontend/dist"     # one up from the current folder → same problem
```
Proof from this project: `database.py` uses `"sqlite:///./test.db"`, and there were **two** `test.db` files, one in the project root (pytest was run from there) and one in `crud-app/backend` (uvicorn was run from there).

**Fix: build the path from the file's own location**, which never changes inside the repo:
```python
from pathlib import Path

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
# __file__ → .../crud-app/backend/main.py
# .parent  → .../crud-app/backend
# .parent  → .../crud-app
# / "frontend" / "dist" → .../crud-app/frontend/dist
```
- `__file__` = the full address of the current `.py` file. Python fills it in at run time, so it's right on the laptop **and** on the VM.
- Works however the app is started: a terminal in any folder, pytest from the root, a boot script (current folder `/`), a service, a scheduled job.
- The other fix is to **`cd` first** (what `user_data.tpl` does). It works, but every way of starting the app must remember to do it.
- Same effect on Linux: `python3 -m venv venv` made `/root/venv` by hand, and `/venv` from the boot script.

---

## 11. Route order, static files and health checks

**FastAPI checks routes in the order they were registered. The first match wins.**

```
/openapi.json, /docs        ← built in
/health
/items/  ,  /items/{item_id}
/   ← app.mount(...)        ← matches EVERYTHING, so it must be LAST
```

### Serving a built front-end from FastAPI (one server for page + API)
```python
from fastapi.staticfiles import StaticFiles

# at the very BOTTOM of main.py, after all routes
if FRONTEND_DIST.exists():                       # don't crash when it hasn't been built
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
```
`StaticFiles` turns the **URL into a file path** inside the folder and sends that file:

| URL | Handled by | Returns |
|---|---|---|
| `/items/` | API route | JSON |
| `/assets/index-abc.js` | the mount | the file `dist/assets/index-abc.js` |
| `/` | the mount | `dist/index.html` (because `html=True`) |
| `/nope` | the mount | 404, no such file |

- A page load is several requests: `/` → the HTML → it asks for its JS and CSS → the JS calls `/items/`.
- If the mount were **first**, `/items/` would be looked up as a file → 404, and the API would be unreachable.
- `/` can't also be an API route: whichever is registered first wins. That's why the old root message moved to `/health`.

### Health check
```python
@app.get("/health")
def health():
    return {"status": "ok"}
```
A tiny URL that only says "I'm running". Load balancers, monitoring and deploy scripts call it to decide whether a server is alive.

---

## 12. CORS on one page

**Origin** = protocol + address + **port**. `http://localhost:5173` and `http://localhost:8000` are different origins.

**Rule (enforced by the BROWSER, not the server):** a page may only read replies from its own origin, unless the other server gives permission.

```
Browser → server:   Origin: http://localhost:5173
Server  → browser:  Access-Control-Allow-Origin: http://localhost:5173     ← the permission
```
No matching header → the browser throws the reply away. That's why the console shows **`200 (OK)` and `ERR_FAILED` together**: the server answered, the browser refused to hand it over. Swagger, curl and Python never hit CORS, because only browsers enforce it.

**Backend fix:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # exactly who may read (port included)
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Preflight (`OPTIONS`):** before a request that **changes data** cross-origin (POST with JSON, PUT, DELETE), the browser first asks permission with an `OPTIONS` request. A plain GET is sent straight away and only the *reading* is blocked.

| | GET | POST / PUT / DELETE |
|---|---|---|
| Preflight? | no | yes, `OPTIONS` first |
| If not allowed | the request runs, the reply is hidden | the request is never sent |

**When there's no CORS at all:** when the page and the API come from the **same origin**, for example FastAPI serving the built front-end (section 11). No `Origin` check, no preflight.

**Front-end side:** the API address comes from a setting, so the same code works in both places:
```js
const API_URL = import.meta.env.VITE_API_URL ?? ''   // .env.development: http://localhost:8000 ; built: '' (same origin)
```
