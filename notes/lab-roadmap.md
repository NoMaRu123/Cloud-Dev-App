# Lab roadmap: rebuild with understanding, then finish

Cloud App Dev (BSHC4SDFD). Built from slides W03–W12.
**Mode: Guided.** I type everything. Claude explains each step first, I predict the result, then we check.
Tick items off as I go: `- [x]`.

---

## Where I am (2026-10-09)

| Week | Topic | Status |
|---|---|---|
| W03 | Flask calculator + UI | ✅ |
| W05 | Singleton | ✅ |
| W05 | Observer + cloud patterns | ⬜ small, any time |
| W06 | Unit + integration tests | ✅ 17 calculator tests |
| — | FastAPI port | ✅ |
| W09 | CRUD backend + validation + logging + 11 tests | ✅ *written by Claude in speed mode, so re-study it* |
| W11 | Terraform + manual deploy to EC2 | ✅ *worked once, but I didn't understand it, so rebuild* |
| W12 | Automatic deploy (user_data) | ⬜ files ready in `infra/` |
| W09 | React front-end (Vite) | ⬜ |
| W10 | Bulk upload (Mockaroo) | ⬜ |

⚠️ **Still in AWS from 2026-10-08:** 1 VM + 1 security group created from `ec2-backend/` (IP was 54.160.134.189). The VM is stopped but **not deleted**. Phase 0 removes it.

---

## ⚡ Speed-run log: re-study these

On **2026-10-08** I said:

> "I need to get through this to the AWS fast, Give me the code, I will go through this again once I went though all of it, will also ask you after everything done for this project to create me an .md file summarise what I learn and what did we do (not now, at the end)."

From that point on we **speed-ran**: Claude wrote the code and I ran it. **I got through it but had no idea what was happening.** On 2026-10-09 we switched back to Guided mode.

Everything below was done without understanding, so it all needs re-studying. Tick each one once I can explain it in my own words:

| Done in speed mode | Where | Re-studied? |
|---|---|---|
| Duplicate names → 409 (`unique=True`, `IntegrityError`, `rollback`, `commit_or_409`) | `crud-app/backend/models.py`, `main.py` | ⬜ |
| Backend-only `requirements.txt` (why separate from the root one) | `crud-app/backend/requirements.txt` | ⬜ |
| `get_item_or_404` helper (removing repeated code) | `crud-app/backend/main.py` | ⬜ |
| Validation with `Field(min_length=..., max_length=...)` | `crud-app/backend/schemas.py` | ⬜ |
| Logging to `server.log` | `crud-app/backend/main.py` | ⬜ |
| 11 CRUD tests: in-memory DB, `dependency_overrides`, fixtures | `crud-app/backend/test_main.py` | ⬜ |
| `.gitattributes` (LF line endings for Linux scripts) | `.gitattributes` | ⬜ |
| Terraform files with the W12 fixes (`templatefile`, repo path, `user_data_replace_on_change`) | `infra/` | ✅ 2026-10-10 |
| Installing Terraform, AWS credentials file | — | ✅ 2026-10-10 |
| W11 manual deploy to EC2 (worked, but I didn't understand it) | `ec2-backend/` | ✅ 2026-10-10 |

> The end-of-project summary (`notes/lab-summary.md`) must clearly mark these speed-run parts, so I know what to revise.

---

## Phase 1: Understand first (no lab needed, ~30 min)

- [x] Read **[cloud-deployment-explained.md](cloud-deployment-explained.md)**.
- [x] Answer these without looking, then check against the note (2026-10-09: 5 and 6 right first time; 1 and 2 partly; 3 and 4 fixed on the re-check):
  1. What's the difference between my laptop, GitHub and the EC2 VM in the deploy?
  2. What do `terraform plan`, `apply` and `destroy` each do?
  3. Why `--host 0.0.0.0` on the VM but not on my laptop?
  4. What is `terraform.tfstate`, and why must I not delete it while the VM exists?
  5. What's the difference between W11 and W12?
- [ ] Re-read `crud-app/backend/main.py`, `schemas.py` and `test_main.py` (written in speed mode). Ask Claude about anything unclear.

---

## Phase 0 + 2 + 3: One lab session (~2 hours)

### Phase 0: Clean up the old deploy
- [x] Start Lab → green dot → paste **fresh** keys into `.aws\credentials`.
- [x] `cd ec2-backend` → `terraform destroy` → read what it will delete → `yes`.

### Phase 2: Rebuild W11 manually (with `ec2-backend/`): ✅ done 2026-10-10 
- [x] `terraform plan`: predict what will be created *before* reading the output.
- [x] `terraform apply` → note the public IP.
- [x] EC2 → Connect → run the deploy commands **one at a time, predicting each one first**.
- [x] Open `http://<ip>/docs`, create an item, and watch the request appear in the VM's terminal.
- [x] `terraform destroy`.

### Phase 3: W12 automatic (with `infra/`): ✅ done 2026-10-10 (swagger worked, uvicorn running in background as `?`)
- [x] Read `infra/main.tf` and `infra/user_data.tpl` with Claude. Spot the 3 differences from `ec2-backend/`.
- [x] `cd infra` → `terraform init` → `plan` → `apply`.
- [x] Wait ~3 min, then open `http://<ip>/docs`. **I typed no commands on the VM.**
- [x] Connect anyway and read `/var/log/cloud-init-output.log`, the script's own output.
- [ ] `terraform destroy` → **End Lab**.

> Only one of `ec2-backend/` and `infra/` can be deployed at a time. Both create a security group called `server-allow-http`.

---

## Phase 4: React front-end, locally (no lab needed, ~3 hours)

- [ ] Install a Vite React app in `crud-app/frontend`.
- [ ] `npm run dev` gives a **live preview with instant reload**, so the Live Server extension isn't needed (it's for plain HTML, not React).
- [ ] Build the lecturer's `App.jsx` (create, list, edit, delete) and understand `useState`, `useEffect` and `fetch`/axios.
- [ ] Connect it to the backend on :8000 (**CORS** vs the **Vite proxy**: Claude will explain both, and we pick one).
- [ ] Improvements: show items in a **table**, display API errors (409 duplicate, 422 empty name).
- [ ] `node_modules/` in `.gitignore` **before** the first commit.

## Phase 5: The same front-end served by FastAPI, locally (~1 hour)

- [ ] `npm run build` → static files in `dist/`.
- [ ] FastAPI serves `dist/` too, so **one server on one port** gives both the UI and the API.
- [ ] Test at `http://localhost:8000`. This is exactly what the cloud will run.

**Result: both ways.**
| | Local development | Cloud |
|---|---|---|
| Front-end | `npm run dev` (instant reload, :5173) | built files served by FastAPI |
| Backend | `uvicorn --reload` (:8000) | uvicorn on the VM (:80) |
| When to use | every day while coding | to check the real deployed app |

## Phase 6: Deploy the full app (one lab session, ~1 hour)

- [ ] Update `user_data.tpl` so the VM also builds the front-end (install Node.js, `npm install`, `npm run build`).
- [ ] `terraform apply` → `http://<ip>` shows the **UI**, and `/docs` still shows the API.
- [ ] `terraform destroy` → End Lab.

## Phase 7: Bulk upload (W10) (~1 hour, part of it in a lab session)

- [ ] Mockaroo: `name` + `description`, 1000 rows → `MOCK_DATA.csv`.
- [ ] Upload script (`csv` + `requests`), counting successes. Duplicates now return **409** (not a 500).
- [ ] Run it **locally**, then against **AWS**, and time both (the slide's benchmark).

## Phase 8: Wrap-up

- [ ] W05 Observer pattern + cloud patterns reading.
- [ ] Claude writes `notes/lab-summary.md`: everything I learned and did.
- [ ] Missing information to ask the lecturer: W04/W08 content, **the final project brief**.

---

## Gotchas collected so far

- `create_all` never changes an existing table, so **delete `test.db` after changing `models.py`**.
- Placeholder URLs in slides (`your-account/your-repo`) must be replaced.
- `uvicorn main:app` must be run **in the folder that contains `main.py`**.
- Windows hides file extensions, which is how `credentials.txt.txt` happened. Turn on View → Show → File name extensions.
- New tools installed by winget need a **full VS Code restart** before the terminal sees them.
- Bash scripts must have LF line endings (`.gitattributes` handles it).
- Never put AWS keys in Git, chat or screenshots.
