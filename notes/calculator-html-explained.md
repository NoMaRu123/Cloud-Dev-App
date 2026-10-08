# How the calculator page talks to the backend

Study notes for `templates/calculator.html` and `calc_app.py`.

---

## 1. First, a correction: this is front-end code, not backend

The `<script>` in `calculator.html` is **JavaScript that runs in the browser**, on the user's computer.
`calc_app.py` is **Python that runs on the server**.

They are two separate programs. They never call each other's functions directly. They only exchange **HTTP requests carrying JSON**:

```
 BROWSER (calculator.html)                         SERVER (calc_app.py)
 ─────────────────────────                         ────────────────────
 1. User types 2, *, 3 and clicks "="
 2. JS builds {"number1":"2","operation":"*","number2":"3"}
 3. fetch() sends  POST /calculate  ───────────►  4. FastAPI matches @app.post("/calculate")
                                                   5. Pydantic validates the JSON → CalcRequest
                                                   6. calculate() does the maths
 8. JS reads the JSON reply        ◄───────────   7. Replies 200 {"result": 6.0}
 9. JS writes "Result: 6.0" on the page
```

Everything below is a detail of one of these 9 steps.

---

## 2. The HTML the script depends on (lines 15–25)

The script finds page elements by their `id`. These are the four it uses:

| Line | Element | `id` | What the user sees |
|---|---|---|---|
| 15 | `<input>` | `number1` | First number box |
| 16–21 | `<select>` | `operation` | Dropdown with + − * / |
| 22 | `<input>` | `number2` | Second number box |
| 25 | `<p>` | `output` | Empty paragraph where the answer appears |

And line 23 connects the button to the code:

```html
<button onclick="calculate()">=</button>
```
`onclick="calculate()"` means: **when this button is clicked, run the JavaScript function named `calculate`.** The JS function in the script has the same name as the Python function in `calculator.py`, but they are completely unrelated, because they live in different programs.

---

## 3. The script, line by line

### Line 27: `<script>`
Everything between `<script>` and `</script>` is JavaScript, not HTML.

### Line 28: `async function calculate() {`
- `function calculate()` defines a function, like `def calculate():` in Python.
- `async` means "this function will **wait** for slow things (the network) without freezing the page". It's what allows `await` inside the function.

### Lines 29–33: build the payload (step 2 in the diagram)
```js
const payload = {
  number1: document.getElementById("number1").value,
  operation: document.getElementById("operation").value,
  number2: document.getElementById("number2").value
};
```
- `const payload = { ... }` creates a JavaScript **object**, which works like a Python dict.
- `document` is the whole web page.
- `.getElementById("number1")` finds the element with `id="number1"` (line 15).
- `.value` is whatever is currently typed in that box, or selected in the dropdown.

**Important detail:** `.value` is always a **string**. If the user types `2`, you get `"2"`, not the number `2`. Remember this for section 4.

### Line 35: `const response = await fetch("/calculate", {`
- `fetch(url, options)` is the browser's built-in way to send an HTTP request (step 3).
- `"/calculate"` is a **relative URL**: same server, same port as the page. The page was loaded from `http://127.0.0.1:8000/ui`, so this goes to `http://127.0.0.1:8000/calculate`.
- `await` means: pause here until the server replies, then put the reply in `response`.

### Line 36: `method: "POST",`
The HTTP method. It must match the decorator on the server: `@app.post(...)`.

### Line 37: `headers: { "Content-Type": "application/json" },`
A label on the request saying "the body is JSON". Without it, the server doesn't know how to read the body.

### Line 38: `body: JSON.stringify(payload)`
- HTTP can only carry **text**, not JavaScript objects.
- `JSON.stringify` converts the object to a JSON string: `'{"number1":"2","operation":"*","number2":"3"}'`.
- Python's equivalent is `json.dumps()`.

### Line 39: `});`
Closes the options object and the `fetch(` call.

### Line 41: `const data = await response.json();`
- The reply's body is also text. `.json()` converts it back into a JavaScript object (step 8).
- It's `await`ed because the body may still be arriving over the network.
- Python's equivalent is `json.loads()`.

### Line 42: `const output = document.getElementById("output");`
Grabs the empty `<p id="output">` from line 25, so the result can be written into it.

### Lines 44–48: show the result or the error (step 9)
```js
if (data.result !== undefined) {
  output.textContent = "Result: " + data.result;
} else {
  output.textContent = "Error: " + data.error;
}
```
- `data.result` reads the `result` key from the reply, like `data["result"]` in Python.
- In JavaScript, reading a key that doesn't exist gives **`undefined`** (not an error like Python's `KeyError`).
- `!==` means "not equal" (strict version).
- So the logic is: "if the reply has a `result`, show it; otherwise assume it's an error and show `data.error`."
- `output.textContent = ...` replaces the text inside the `<p>`, which is what makes it appear on screen.

**This is exactly where "Error: undefined" comes from.** If the reply has neither `result` nor `error`, for example `{"detail": "Method Not Allowed"}`, the `else` branch runs and `data.error` is `undefined`.

---

## 4. How each line connects to `calc_app.py`

Front-end and backend must agree on four things. When any of them disagree, it breaks:

| # | They must agree on... | Front-end (`calculator.html`) | Backend (`calc_app.py`) |
|---|---|---|---|
| 1 | **URL** | `fetch("/calculate", ...)` | `@app.post("/calculate")` |
| 2 | **Method** | `method: "POST"` | `@app.post` (not `@app.get`) |
| 3 | **Request shape** | keys `number1`, `operation`, `number2` | `class CalcRequest` with the same three fields |
| 4 | **Response shape** | reads `data.result` / `data.error` | returns `{"result": ...}` or `JSONResponse({"error": ...})` |

And one more connection:

| What | Front-end | Backend |
|---|---|---|
| Loading the page itself | Browser opens `/ui` | `@app.get("/ui")` returns `FileResponse("templates/calculator.html")` |

### The bugs you hit, seen through this table
- **Agreement #1 broken:** your route was `@app.post("/")` but the page posts to `/calculate`, so the server answers 405 `{"detail": "Method Not Allowed"}`.
- The page then reads `data.error`, gets `undefined`, and shows **"Error: undefined"**.
- The earlier `"Error"` vs `"error"` bug was **agreement #4** broken.

### Strings vs numbers (the detail from line 30)
The page sends `"2"` (a string), but `CalcRequest` says `number1: float`.
Pydantic **converts** `"2"` to `2.0` automatically, so it works.
But `"abc"` or an empty box `""` can't be converted, so FastAPI replies **422**.

### A gap you'll find when testing: 422 in the UI
FastAPI's 422 reply looks like this:
```json
{"detail": [{"loc": ["body", "number1"], "msg": "Input should be a valid number", ...}]}
```
There's no `error` key, so typing `abc` in the UI shows **"Error: undefined"**. In Flask it showed a proper message, because your own `try/except` produced `{"error": ...}`.

This is a real design decision with two possible fixes:
- **Front-end fix:** in the `else` branch, also check `data.detail`.
- **Backend fix:** make the API return errors in one consistent shape.

Agreement #4 is the one to think about here. Try fixing it yourself.

---

## 5. Why `/calculate` and not `http://127.0.0.1:8000/calculate`?

Because the page and the API come from **the same server** (port 8000), a relative URL works and the browser allows it.

In W09 the React front-end runs on **port 3000** and the API on **port 8000**. Those count as different "origins", and the browser blocks the request unless the backend explicitly allows it. That's what this part of the lecturer's CRUD app is for:
```python
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], ...)
```
You don't need it yet, but now you'll know why it's there.

---

## 6. Weak spots in this page, and how to fix them

### Weak spot 1: it guesses success from the JSON keys
`if (data.result !== undefined)` works, but it's guessing. The server already *tells* you whether it succeeded, through the status code.
`response.ok` is `true` for any 2xx status (200–299) and `false` for 4xx/5xx.

You don't need both checks (`data.result !== undefined && response.ok`). Check the status, and trust that a successful reply has a `result`.

### Weak spot 2: no handling for a crash or a dead server
- If the server is **down**, `fetch` throws an error and nothing appears on the page.
- If the server **crashes** (500), it may reply with plain text, not JSON, so `response.json()` throws.

`try { ... } catch (err) { ... }` catches both. It's JavaScript's version of Python's `try/except`.

### Weak spot 3: no validation in the browser
`type="number"` makes the browser refuse letters. Then check for empty boxes yourself before sending anything.
(`required` only blocks submission inside a `<form>`. This page uses a plain button, so it does nothing here.)

### Weak spot 4: shows "undefined" when the error has a different shape
`data.error ?? "fallback"` means "use `data.error`, but if it's `undefined`, use the fallback instead". That way the page never shows the word `undefined`.

### The improved version, with all four fixes

```html
<input id="number1" type="number" step="any" placeholder="Number 1">
<!-- select stays the same -->
<input id="number2" type="number" step="any" placeholder="Number 2">
```
(`step="any"` allows decimals. Without it, the browser only accepts whole numbers.)

```js
async function calculate() {
  const output = document.getElementById("output");
  const number1 = document.getElementById("number1").value;
  const number2 = document.getElementById("number2").value;

  // Weak spot 3: stop early if a box is empty (or had letters, which type="number" turns into "")
  if (number1 === "" || number2 === "") {
    output.textContent = "Error: please enter two numbers";
    return;                                    // don't send anything
  }

  const payload = {
    number1: number1,
    operation: document.getElementById("operation").value,
    number2: number2
  };

  try {                                        // Weak spot 2: start of the protected block
    const response = await fetch("/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();

    if (response.ok) {                         // Weak spot 1: trust the status code
      output.textContent = "Result: " + data.result;
    } else {
      // Weak spot 4: never print "undefined"
      output.textContent = "Error: " + (data.error ?? "request failed (status " + response.status + ")");
    }
  } catch (err) {                              // server down, or the reply wasn't JSON
    output.textContent = "Error: no valid reply from the server";
    console.error(err);                        // full details in DevTools → Console
  }
}
```

With these fixes, the front-end stops trusting the user (weak spot 3) and stops trusting the server (weak spots 1, 2 and 4).

---

## 7. The reusable pattern for your own apps

> This section has been moved into **[app-building-cheatsheet.md](app-building-cheatsheet.md)**, which keeps growing as you learn more. The copy below is the original.

Almost every "page talks to API" feature, including the W09 React CRUD app, is these same five steps:

```js
async function doSomething() {
  // 1. READ inputs from the page
  const payload = { field: document.getElementById("field").value };

  // 2. SEND them to the API
  const response = await fetch("/your-endpoint", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  // 3. PARSE the reply
  const data = await response.json();

  // 4. DECIDE success or error
  if (response.ok) {
    // 5. SHOW the result on the page
    document.getElementById("output").textContent = data.something;
  } else {
    document.getElementById("output").textContent = "Error: " + data.error;
  }
}
```

And the matching backend:

```python
class YourRequest(BaseModel):     # must match the payload keys
    field: str

@app.post("/your-endpoint")       # must match the fetch URL + method
def your_endpoint(request: YourRequest):
    return {"something": ...}     # must match what the page reads
```

React's `axios.post(...)` in the CRUD app is the same idea with less typing: it does the `JSON.stringify`, the header and the `.json()` for you.
