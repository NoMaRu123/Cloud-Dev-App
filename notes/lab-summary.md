# Cloud App Dev lab: what I learned and what we did

This covers the weekly lab, from the Flask calculator to the React front-end, up to 18 October 2026. Each section has what I built, the ideas behind it, and the problems I hit with their fixes.

Two kinds of work were written by Claude rather than by me:

- Sections marked (speed run) were written on 8 October, when I rushed to reach the AWS deploy. I didn't understand them at the time, so they are the ones to re-study.
- The front-end polish (table, styling, browser validation) was written by Claude on purpose, because front-end isn't my focus.

Everything else I typed myself, with Claude explaining first and checking afterwards.

## The stages at a glance

| # | Stage | Slides | Status |
|---|---|---|---|
| 1 | Flask calculator | W03 | done |
| 2 | Singleton pattern | W05 | done (Observer not yet) |
| 3 | Git and GitHub | none | done |
| 4 | Unit and integration tests | W06 | done, 17 tests |
| 5 | The calculator rebuilt in FastAPI | W06 | done |
| 6 | The JavaScript I needed | W03, W09 | done |
| 7 | CRUD backend with a database | W09 | done, 11 tests |
| 8 | Cloud deployment with Terraform | W11, W12 | done, by hand and automatically |
| 9 | React front-end | W09 | done, full CRUD |
| 10 | Serving the built front-end from FastAPI | none | nearly done |

---

## 1. Flask calculator (W03)

I built a small Flask API (`hello_flask.py`): `/` returns a JSON message, `/calculate` takes two numbers and an operation, and `/ui` serves an HTML calculator page. The maths lives in `calculator.py`, kept apart from the web code.

Ideas:

- A route connects a URL and an HTTP method to a Python function.
- The API talks in JSON. Status codes tell the client what happened: 200 worked, 400 bad input, 404 no such URL, 405 the URL exists but not for that method.
- A venv is a private set of packages for one project. `requirements.txt` is the list that rebuilds it anywhere.

| Problem | Cause | Fix |
|---|---|---|
| Dividing by zero showed "Error: undefined" on the page | the backend sent the key `Error`, the page read `error` | one spelling everywhere |
| The tests still passed with that bug | the tests also checked for `Error` | a test only proves the code matches the test |
| `flask` crashed with "Unable to create process" | I had moved the project folder, and a venv stores its own path | delete the venv and rebuild it from `requirements.txt` |

## 2. Singleton pattern (W05)

The lecturer's Singleton uses a metaclass. `SingletonMeta.__call__` runs every time the code writes `Singleton()`. The first time, it creates the object and stores it in `_instances`. Every time after that, it returns the stored one, which is why `id(s1) == id(s2)`.

The Observer pattern from the same slides isn't done yet. It is planned for the CA (see the end of this file).

## 3. Git and GitHub

- `.gitignore` keeps out things that shouldn't be shared: `venv/`, caches, databases, secrets.
- `git add` stages changes, `git commit` saves a snapshot, `git push` sends commits to GitHub.
- A small commit with a message that says why is easier to understand later than one big commit.

| Problem | Cause | Fix |
|---|---|---|
| Push failed: "Password authentication is not supported" | GitHub stopped accepting account passwords for Git | sign in through the browser window or use a token |
| A new token still failed | an old saved login in Windows Credential Manager was used instead | delete the old entry (its name included `LegacyGeneric:target=`), then sign in again |
| "LF will be replaced by CRLF" warnings | Windows and Linux end lines differently | harmless for Python. Bash scripts for Linux must keep LF, which `.gitattributes` enforces (speed run) |

## 4. Testing (W06)

- A unit test calls a function directly. An integration test calls the running app over HTTP through a test client.
- pytest only collects files named `test_*.py` and functions named `test_*`.
- Each test follows arrange, act, assert. Check the response body as well as the status code, otherwise the test can pass when the answer is wrong.
- `GET /calculate` returns 405, not 404, because the URL exists but only accepts POST.

## 5. The calculator rebuilt in FastAPI

Ideas:

- A Pydantic model (`class CalcRequest(BaseModel)`) describes the JSON the API expects. FastAPI checks every request against it before my function runs and rejects bad input with 422.
- The type hint on a parameter tells FastAPI where the data comes from: a Pydantic model means the JSON body, `{item_id}` in the URL means the path, anything else means the query string.
- `.model_dump()` turns a Pydantic object into a plain dict.
- Flask understands `return (data, 400)`. FastAPI doesn't, so errors need `JSONResponse(content=..., status_code=...)`.
- An exception handler can make FastAPI's own 422 errors use the same `{"error": ...}` shape as mine, so the front-end reads every error the same way.
- `/docs` (Swagger) is drawn from `/openapi.json`, the API description FastAPI generates. It's OpenAPI, with a P.
- uvicorn and FastAPI do different jobs. uvicorn is the web server that listens on a port, and FastAPI decides what to answer. The analogy was a waiter and a kitchen.

| Problem | Cause | Fix |
|---|---|---|
| The page showed "Error: undefined" again | the route was `@app.post("/")` but the page posted to `/calculate`, so the server answered 405 | found it by reading `openapi.json` in the browser's Network tab |
| Every calculation returned 500 | `calculate(result.model_dump())` used `result` on the line that creates it | use the parameter: `request.model_dump()` |
| `JSON.Stringify is not a function` | JavaScript is case sensitive | `JSON.stringify` |
| The error handler itself crashed | `console.error(error)` inside `catch (err)` | the names must match |
| Fixes didn't seem to work | the browser was still running the old page | Ctrl+F5 after editing HTML |

## 6. The JavaScript I needed

- `fetch` sends a request. `JSON.stringify` turns an object into JSON text before sending, and `response.json()` turns the reply back into an object.
- `response.ok` is true for any 2xx status. `try`/`catch` handles a server that is down or a reply that isn't JSON.
- `console.log` and `console.error` print in the browser's F12 console, not in the server's terminal. Output appears wherever the code runs.
- Brackets mean "do something" (`response.json()`), no brackets mean "read a stored value" (`response.ok`).
- `A ? B : C` means if A then B, otherwise C. `X && Y` means show Y only if X is true.

## 7. CRUD backend with a database (W09)

Ideas:

- A SQLAlchemy model is a database table. A Pydantic schema is the JSON shape of the API. They are two different classes that can share a name.
- `get_db` with `yield`, used through `Depends(get_db)`, gives each request its own database session and closes it afterwards, even if something crashes. This is dependency injection.
- REST means the same URL with different methods does different things:

| CRUD | Method | URL |
|---|---|---|
| Create | POST | `/items/` |
| Read | GET | `/items/` or `/items/{id}` |
| Update | PUT | `/items/{id}` |
| Delete | DELETE | `/items/{id}` |

- Saving works like Git: `db.add` stages, `db.commit` saves, `db.refresh` reloads the row with the id the database gave it.
- `.filter(...).first()` returns `None` when nothing matches, which becomes a 404.
- PUT replaces every field. The update copies them with a `setattr` loop.
- `create_all` never changes a table that already exists, so after editing `models.py` the old `test.db` has to be deleted.

Written in the speed run, to re-study:

- `unique=True` on the name column, catching `IntegrityError`, calling `rollback`, and returning 409 (`commit_or_409`).
- `get_item_or_404`, which replaced three copies of the same code.
- `Field(min_length=1, max_length=100)` validation.
- Logging every request to `server.log`.
- The tests: an in-memory database with `StaticPool`, `app.dependency_overrides` to swap in the test session, and a fixture that empties the tables before each test.

By the end, validation happened in three layers: the browser (`required`, `maxLength`), the API (Pydantic, 422) and the database (`unique=True`, 409).

## 8. Cloud deployment with Terraform (W11, W12)

The long explanation is in `cloud-deployment-explained.md`. The short version:

- Cloud means renting someone else's computers. An EC2 instance is a rented virtual machine, a security group is its firewall, an AMI is the operating system image it starts from, and the region (`us-east-1`) is the data centre.
- The AWS Academy Learner Lab is a school account with a $50 budget. A session lasts 4 hours, the keys from AWS Details expire with it, and ending the session stops (but doesn't delete) the VM.
- Terraform creates infrastructure from files. `init` downloads the AWS plugin, `plan` shows the changes without making them, `apply` makes them, `destroy` deletes them. A `data` block looks something up and a `resource` block creates something.
- One block refers to another (`aws_security_group.server_sg.id`), which tells Terraform the order: the firewall before the VM, and the reverse when destroying.
- `terraform.tfstate` is Terraform's receipt. Deleting it doesn't delete the VM. Terraform just forgets it, and the VM keeps using the budget.
- After a VM stops and starts it gets a new public IP. `terraform apply -refresh-only` updates the receipt.
- Inside the VM, `hostname -I` shows only the private IP (172.31.x.x). AWS forwards the public address to it.

The manual deploy (W11) used the same commands as on my laptop, on Linux: become root, install the venv tool, create a venv, `git clone`, `pip install`, then `uvicorn main:app --host 0.0.0.0 --port 80`.

- `--host 0.0.0.0` accepts connections from other computers. The default, 127.0.0.1, only accepts the same machine.
- Port 80 is the default for http, so the URL needs no port number. Ports below 1024 need root.
- A request has to pass two doors: the program has to listen to outside connections, and the firewall has to allow the port.

The automatic deploy (W12) gives Terraform a startup script, `user_data.tpl`, that runs those same commands once, as root, on the VM's first boot.

- The lecturer's `main.tf` loaded the script with `file()`, which leaves `${app_port}` blank. `templatefile()` fills it in.
- The script starts in `/`, so the venv ended up at `/venv` rather than `/root/venv`.
- `> uvicorn.log 2>&1 &` sends the output to a file and runs uvicorn in the background. `ps aux` showed `?` in its terminal column, meaning no terminal, so it survives disconnects.
- `/var/log/cloud-init-output.log` holds everything the script printed.

| Problem | Cause | Fix |
|---|---|---|
| The credentials file was `credentials.txt.txt` | Windows hides file extensions | rename it, and turn on File name extensions in Explorer |
| `terraform` not recognised after installing | VS Code kept the old PATH | restart VS Code completely |
| `git clone` on the VM asked for a password | I used the slide's placeholder URL | the real repo URL |
| `Could not import module "main"` | uvicorn was started in the repo root | `cd crud-app/backend` first |
| `DNS_PROBE_FINISHED_NXDOMAIN` | I typed `http//` without the colon | `http://` |
| The app died when my laptop shut down | a program stops when its terminal session ends | W12 runs it in the background |
| `Got unexpected extra arguments (port 80)` | a space in `-- port` | `--port` |
| I opened "Launch instance" in the console | that form is the click version of what Terraform had already done | Cancel, and use Terraform |

## 9. React front-end (W09)

Ideas:

- JavaScript has the same tools as Python under other names: Node.js runs the tools, npm installs packages, `package.json` lists them, and `node_modules` holds them, like a venv. `package-lock.json` pins the exact versions and should be committed.
- Vite has two jobs: a dev server with live reload (`npx vite`), and a build that turns JSX into plain files (`npm run build`).
- A component is a function that returns what the page should look like. `useState` remembers data, and changing it makes React redraw the page.
- `useEffect(..., [])` runs once when the page first appears. In development it runs twice because of `StrictMode`, which only happens locally.
- State only lives in browser memory, so a refresh resets it. That's why the app needs the backend and database.
- Vite also listens on localhost only. `npx vite --host` opened it to my Wi-Fi, and the page worked on my phone.
- PowerShell swallows a bare `--`, so `npm run dev -- --host` loses the flag. `npx vite --host` works.

CORS, which I chose over the Vite proxy because it's the lecturer's way and worth showing in the CA:

- An origin is protocol, address and port, so `localhost:5173` and `localhost:8000` are different origins.
- The browser does the blocking, not the server. The console showed `200 OK` and `ERR_FAILED` together: the server answered, but the browser refused to hand over the reply.
- The fix is a header from the server, `Access-Control-Allow-Origin: http://localhost:5173`, added by `CORSMiddleware`.
- Before a request that changes data (POST with JSON, PUT, DELETE), the browser sends an `OPTIONS` preflight to ask permission first.
- The API address comes from `VITE_API_URL` in `.env.development`. It is empty in the built version, so the same code works locally and deployed.

CRUD in React: controlled inputs keep each box and its state in sync, `[...items, data]` adds to the list, `.filter` removes, `.map` swaps the edited item, and one `editingId` value switches the form between adding and editing.

Bugs I made along the way: a stray comma after `useState([])`, `deletItem` instead of `deleteItem`, quotes instead of backticks around `${id}`, and `item,id` instead of `item.id`.

## 10. Serving the built front-end from FastAPI

- `npm run build` creates `dist/`: an almost empty `index.html`, one JavaScript file and one CSS file.
- `app.mount("/", StaticFiles(directory=..., html=True))` serves those files. FastAPI checks routes in the order they were registered and the first match wins, so the mount, which matches everything, must be last. The old `/` message moved to `/health`.
- A relative path is measured from the folder the program was started in, not from the file. There were two `test.db` files in the project because of `"sqlite:///./test.db"`. Building the path from `__file__` works however the app is started.
- The CA brief asks for a standalone front-end, so this one-server design may change in the CA.

---

## Not finished yet

These are being done in the CA project (`budget-tracker`), where they count for marks:

- W13 CI/CD: GitHub Actions running tests and Terraform
- Deploying the full app, UI and API together
- Restarting the app automatically after a VM reboot (systemd)
- W10 bulk upload: becomes importing transactions from a CSV file
- W05 Observer pattern: becomes budget alerts when a transaction is added
- W05 cloud design patterns reading
- Testing the built front-end at `localhost:8000`

## What to re-study

- Everything marked (speed run) in sections 3 and 7.
- The front-end table, styling and validation, enough to explain them in the video.

## Where to look things up

- `app-building-cheatsheet.md`: patterns and commands, including relative paths, route order and CORS (sections 10 to 12)
- `cloud-deployment-explained.md`: cloud, EC2, the Learner Lab and Terraform in plain words
- `lab-roadmap.md`: the lab's step-by-step history
- `..\budget-tracker\notes\PLAN.md`: the CA plan
