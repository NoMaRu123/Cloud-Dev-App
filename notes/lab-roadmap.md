# Lab roadmap: from here to a deployed app

Cloud App Dev (BSHC4SDFD). Built from slides W03, W05, W06, W09 (Front-end + Validations), W10, W11 Part I and II, and W12.
Tick items off as you go: `- [x]`.

---

## Where I am (2026-10-08)

| Week | Topic | Status |
|---|---|---|
| W03 | Web frameworks (Flask calculator, UI) | ✅ Done |
| W05 | Singleton | ✅ Done |
| W05 | Observer + cloud design patterns | ⬜ Not started (small) |
| W06 | Unit + integration tests | ✅ Done (Flask + FastAPI, 17 tests) |
| — | Port to FastAPI | ✅ Done |
| W09 | CRUD backend (5 routes) | 🟡 Done + committed, duplicate names → 409. **Tests not written yet** |
| W09 | Validations + logging | ⬜ |
| W09 | React front-end | ⬜ |
| W10 | Bulk upload (Mockaroo CSV) | ⬜ |
| W11 | Terraform + manual deploy to AWS EC2 | ⬜ |
| W12 | Automated deploy (user_data) | ⬜ |

**The goal of the whole module:** the CRUD app, tested and validated, filled with ~1000 rows, and deployed to AWS **automatically** by Terraform.

---

## Stage A: Finish the W09 backend (~2 hours)

**A1. ✅ Commit chunk 2** (read one, update, delete).

**A2. Chunk 3: tests:** `crud-app/backend/test_main.py` (in-memory DB, `dependency_overrides`, fixture). Run `pytest` from `crud-app/backend` → 6 passed. Add your own "update missing → 404" test.

**A3. Validations (W09 Validations slides).** Three layers:
- [ ] **Pydantic** (API): `name: str = Field(min_length=1, max_length=100)`, so empty names get a 422.
- [x] **Database**: `name = Column(String, index=True, nullable=False, unique=True)`. This is the **exact** line from the W10 slide, and W10 depends on it.
- [x] Handle the duplicate crash. Without handling, a duplicate name gives a **500** (that's what the lecturer's W10 output shows). Done in `commit_or_409()` in `main.py`: catches `IntegrityError` → `db.rollback()` → **409 Conflict**. Used by create and update.
- [ ] ⚠️ **Delete `crud-app/backend/test.db` now.** `models.py` changed, and `create_all` never changes an existing table, so the old file has no unique rule.
- [ ] Tests for: empty name → 422, duplicate → 409 (create **and** rename to an existing name).

**A4. Logging:** `logging.basicConfig(filename='server.log', ...)` plus a `logging.info` line in each route. Check that `server.log` fills up (it's already in `.gitignore`).

---

## Stage B: React front-end (W09 Front-end) (~2–3 hours)

- [ ] Add `CORSMiddleware` to `main.py`, allowing `http://localhost:3000` (cheatsheet section 1 explains why).
- [ ] Create the front-end in `crud-app/frontend`. The lecturer uses `create-react-app` (deprecated in 2025 but still works). **Vite** is the modern option: `npm create vite@latest frontend -- --template react`. Ask the lecturer which they prefer.
- [ ] `npm install axios`, then type in the lecturer's `App.js` + `App.css` and understand `useState`, `useEffect` and axios.
- [ ] Run both: backend on :8000, front-end on :3000. Create, edit and delete from the UI.
- [ ] Add `node_modules/` to `.gitignore` **before** committing (it's huge).
- [ ] Improvements from the slides: show items in a **table**, nicer design (optional: Tailwind).

---

## Stage C: Bulk upload (W10) (~1 hour)

- [ ] **Mockaroo** (mockaroo.com): 2 fields, `name` and `description`, 1000 rows, download CSV → `MOCK_DATA.csv`.
- [ ] `pip install requests` (it isn't installed yet), then freeze requirements.
- [ ] Type in the upload script from the slide (`csv.DictReader` + `requests.post`, counting successes). Use the URL **`/items/`** with the trailing slash, to match the route.
- [ ] Run it: total insertions **< 1000**, because Mockaroo repeats names and your `unique=True` rejects them. Check the count matches Swagger GET `/items/?limit=2000`.
- [ ] Add `MOCK_DATA.csv` to `.gitignore`, or commit it as sample data (your choice).
- [ ] Optional (slide "What's next"): time the upload (`time.perf_counter()`), locally vs on AWS later.

---

## Stage D: Get the repo ready for deployment (~30 min)

The slides' deploy commands assume `main.py` and `requirements.txt` are at the **repo root**. Yours are in `crud-app/backend/`, so adapt them:

- [x] Create **`crud-app/backend/requirements.txt`** with only what the backend needs (`fastapi`, `uvicorn`, `sqlalchemy`). It's lighter and safer on Linux than the full Windows freeze (which includes Flask, pytest, colorama...).
- [x] Deploy commands then become:
  ```bash
  git clone https://github.com/NoMaRu123/Cloud-Dev-App.git
  cd Cloud-Dev-App/crud-app/backend
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 80
  ```
- [ ] Test locally first with `--host 0.0.0.0` and check that `/docs` works.
- [ ] Push. The repo must be **public** (it is) so the server can `git clone` without a password.

---

## Stage E: Terraform basics (W11 Part I) (~1 hour)

- [ ] Install Terraform: `winget install Hashicorp.Terraform`, then reopen the terminal and run `terraform -version`.
- [x] `infra/` folder created with `main.tf` + `variables.tf` + `user_data.tpl`. **Still read and understand each block:**
  - `provider "aws"`: which cloud and region (`us-east-1`)
  - `data "aws_ssm_parameter"`: look up the latest Ubuntu 26.04 image
  - `resource "aws_security_group"`: firewall, open port **80** (web) to everyone and **22** (SSH) to EC2 Instance Connect only
  - `resource "aws_instance"`: the VM itself (`t2.micro`)
  - `output "public_ip"`: prints the IP when it's done
- [x] Added to `.gitignore` (before the first `terraform init`):
  ```
  .terraform/
  *.tfstate
  *.tfstate.*
  ```
  The state file can contain sensitive values. **Never commit it, and never commit AWS credentials.**

---

## Stage F: Manual deploy to AWS (W11 Part II) (~1–2 hours)

- [ ] AWS Academy → **Start Lab** → wait for the green dot → **AWS Details → AWS CLI: Show** → paste into **`C:\Users\ASUS\.aws\credentials`**.
  - These credentials **expire** when the lab session ends (~4 h), so you'll need to re-paste them each session.
- [ ] In `infra/`: `terraform init` → `terraform plan` (read what it will create) → `terraform apply` → note the `public_ip`.
- [ ] AWS console → EC2 → Instances → `sandbox` → **Connect** → EC2 Instance Connect.
- [ ] On the VM: run the Stage D commands as root (`sudo -i`).
- [ ] Browser: `http://<public_ip>/docs`. **Your API on the internet.** 🎉
- [ ] **Clean up:** `terraform destroy`, then **End Lab**, to save the lab budget.

---

## Stage G: Automated deploy (W12) (~1 hour)

The VM installs and starts your app **by itself** at boot, using `user_data.tpl`.

- [x] `infra/user_data.tpl` uses this repo's URL and `cd Cloud-Dev-App/crud-app/backend`.
- [x] ⚠️ **Fixed in `infra/main.tf`:** the slides' script uses `${app_port}`, but the slides' `main.tf` loads it with `file("user_data.tpl")`. **`file()` doesn't fill in `${...}` placeholders**, so the port would be empty and uvicorn wouldn't start. Now uses:
  ```hcl
  user_data = templatefile("${path.module}/user_data.tpl", { app_port = 80 })
  ```
- [x] Also added: `user_data_replace_on_change = true` (user_data only runs on first boot, so the VM is rebuilt when the script changes) and `.gitattributes` (keeps the script's LF line endings, because bash on Linux fails on Windows CRLF with errors like `$'\r': command not found`).
- [ ] `terraform apply` → wait 2–3 minutes (the VM is installing everything) → `http://<public_ip>/docs`.
- [ ] If it doesn't work, connect to the VM and read:
  - `/var/log/cloud-init-output.log`: the output of your user_data script
  - `uvicorn.log`: your app's output
- [ ] `terraform destroy` + **End Lab**.

---

## Stage H: Leftovers (any time, small)

- [ ] **W05 Observer pattern**: run the refactoring.guru Python example and trace attach → notify → update.
- [ ] **W05 cloud patterns**: read Publisher-Subscriber, Retry and Circuit Breaker in the Azure pattern catalog.
- [ ] Optional stretch (slides' "Looking for more"): run uvicorn as a **systemd** service, use AWS RDS instead of SQLite, add a load balancer.

---

## Missing information

- **W04, W08** had no files. Are there videos or pages?
- **The final project brief**: the most important document. Its requirements decide which stretch items matter.
- **Lecturer preference**: create-react-app or Vite?
