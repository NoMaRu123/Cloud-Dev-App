# Lab roadmap: rebuild with understanding, then finish

Cloud App Dev (BSHC4SDFD). Built from slides W03–W12.
**Mode: Guided for backend and cloud.** I type, Claude explains each step first, I predict the result, then we check.
**Front-end: brief.** It isn't my focus, so Claude may write it, with a comment on every line.
Tick items off as I go: `- [x]`.

---

## ➡️ The CA project has moved (2026-10-18)

My CA project, **budget-tracker**, now lives in the sibling folder `..\budget-tracker` (GitHub: NoMaRu123/budget-tracker), created from this lab's code. Its plan is `budget-tracker\notes\PLAN.md`. Open that folder in VS Code for all new work. This repo stays as the lab archive.

**The lab is not fully finished.** Plan agreed on 2026-10-18: one ~2-hour local session in the lab for the items where practising twice pays off, and everything else done once in the CA.

| Lab item still open | Decision |
|---|---|
| Phase 5: test the build at `localhost:8000` | **do in the lab** (~10 min) |
| W05 Observer pattern | ✅ **done 2026-10-19** (`other/observer.py`, the lecturer's code, traced by hand). Next: budget alerts in CA Phase B. Recap of the OOP behind it: `notes/python-oop-recap.md` |
| W10 bulk upload, local (Mockaroo + upload script) | ✅ **done 2026-10-19**: `other/upload.py` + `other/MOCK_DATA.csv`. 1000 rows → **951 inserted**, 49 rejected with 409 (exactly the 49 repeated names in the file). The database then held 953 = 951 + 2 earlier items. Posting to `/items` (no slash) gives 405 because of the Phase 5 catch-all mount, so the URL is `/items/`. Next: CSV import in CA Phase B |
| W05 cloud patterns | **Claude writes a one-page note** (`notes/cloud-patterns.md`), then CA Phase H for the references |
| **W13 demo flow (updated 2026-10-19)** | **do in the lab AND the CA.** The lecturer's demo-steps slide (`course-materials/CA-demo-steps-slide.jpg`) must be done in full, with no step skipped. See "Demo flow" below |
| Phase 6: deploy UI + API together | **replaced** by the demo flow: the front-end runs on my laptop and calls the backend's IP on AWS |
| systemd restart after reboot | CA Phase E only (the demo builds a fresh stack each time, so it isn't needed for the demo) |

### Demo flow (the lecturer's 8 demo steps), to do in the lab first

| # | Step | Status |
|---|---|---|
| 1 | Start the AWS Academy lab | done before (by hand) |
| 2 | Paste the AWS keys into **GitHub Secrets** | ⬜ never done |
| 3 | Run a **GitHub workflow** that launches the Terraform stack | ⬜ (Terraform was always run from my laptop) |
| 4 | Show the successful workflow: **testing and deployment** | 🟡 testing ✅ (`.github/workflows/ci.yml`, green on 2026-10-19). Deployment: `deploy.yml` next |
| 5 | Paste the backend's IP into the front-end (`VITE_API_URL`) | ⬜ the front-end has only ever called a local backend |
| 6 | Start the front-end (`npx vite`) | done, locally |
| 7 | Code walkthrough: front-end, library, backend, testing | partly (no library in the lab, that's CA only) |
| 8 | Stop the stack with a **GitHub workflow** | ⬜ (`terraform destroy` was always run from my laptop) |

Build order: a CI workflow that runs the tests (no AWS needed), then deploy and destroy workflows adapted from W13's `workflows.zip` (Terraform in `infra/`, AWS keys from GitHub Secrets, and **the state file in a private S3 bucket**, decided 2026-10-19. W13 commits the state to the repo instead, but the repo is public, so that was rejected. The repo itself must stay public, because the VM clones it without a login and the W11 slide asks for a public repo), then one full rehearsal of steps 1 to 8 in a lab session.
| Phase 6b pull-script auto-update | **dropped** (W13's GitHub Actions replaces it) |
| W10 timing comparison on AWS | **dropped** (optional in the slides) |

## ▶ Resume here (updated 2026-10-12)

**Starting a new Claude session?** Say: *"Read notes/lab-roadmap.md and continue from Resume here."*

- **Now:** Phase 5, step 3. `main.py` already serves the built front-end (the `/health` route, and the `StaticFiles` mount at the bottom), and `npm run build` has been run. **Not committed yet.**
- **Next action:** with uvicorn running and Vite **off**, open `http://localhost:8000`, add an item, and look at terminal #2. Is there an `OPTIONS` line before the `POST`? (Expected: no. The page and the API are now the same origin, so there's no CORS check.) Then commit and push.
- **After that:** Phase 6 (deploy the full app), 6b (auto-update), 7 (bulk upload), 8 (wrap-up).
- **AWS:** nothing running. Both Terraform folders hold 0 resources.
- **Course materials:** all slides and the CA brief are in `course-materials/` (ignored by Git: the repo is public). Still missing: W08, W04, W07, W01–W02.
- ⚠️ **The CA brief arrived 2026-10-18** (midpoint check 6 Nov, due 16 Dec). It changes Phases 6–8: a **standalone** front-end with Bootstrap and components, a **library beyond CRUD**, more test types, and **CI/CD with GitHub Actions** (W13). Re-plan before Phase 6.

## Where I am (2026-10-12)

| Week | Topic | Status |
|---|---|---|
| W03 | Flask calculator + UI | ✅ |
| W05 | Singleton | ✅ |
| W05 | Observer + cloud patterns | ⬜ small, any time |
| W06 | Unit + integration tests | ✅ 17 calculator tests |
| — | FastAPI port | ✅ |
| W09 | CRUD backend + validation + logging + 11 tests | ✅ *written by Claude in speed mode, still to re-study (see the speed-run log)* |
| W11 | Terraform + manual deploy to EC2 | ✅ rebuilt by hand and understood, 2026-10-10 |
| W12 | Automatic deploy (user_data) | ✅ 2026-10-10 |
| W09 | React front-end (Vite), full CRUD + CORS | ✅ 2026-10-12 |
| — | Front-end served by FastAPI (one server) | 🟡 Phase 5, nearly done |
| — | Full app (UI + API) on AWS | ⬜ Phase 6 |
| W10 | Bulk upload (Mockaroo) | ⬜ Phase 7 |

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

## Phase 4: React front-end, locally (no lab needed): ✅ done 2026-10-12

- [x] Vite React app created in `crud-app/frontend` (React + JavaScript + Oxlint). `node_modules` is ignored by Vite's own `.gitignore`.
- [x] `npm run dev` / `npx vite`: live preview + HMR (state survives edits, F5 resets it).
- [x] Two doors again: `npx vite --host` opened it to the Wi-Fi, so it worked on my phone at `192.168.1.93:5173`.
- [x] **Chose CORS** (the lecturer's way, good for the CA): saw the browser block it (`200 OK` + `ERR_FAILED`), added `CORSMiddleware` for `http://localhost:5173`, then saw `Access-Control-Allow-Origin` appear.
- [x] API address in `.env.development` (`VITE_API_URL`), empty in the AWS build, so the same code works both ways.
- [x] READ: list loads on page load (`useEffect`, `items.map`). 2 GETs in dev = StrictMode, normal.
- [x] CREATE: form with controlled inputs, POST, errors shown in red. `App.jsx` has a comment on every line.
- [x] The 4 experiments from step 7d (duplicate → 409 from `commit_or_409`, empty name → 422 from `schemas.py`, `OPTIONS` preflight before POST/PUT/DELETE).
- [x] DELETE (button per row, `items.filter`) and UPDATE (`editingId` mode switch, one form for add + edit, `items.map`). I typed these; Claude fixed 4 typos (`deletItem`, quotes instead of backticks, `item,id`).
- [x] Table + CSS, and the front-end validation layer (`required`, `maxLength`). **Written by Claude** on 2026-10-12, because front-end isn't my focus. Every line is commented.
- [x] Final click-test of the finished page: everything worked. Committed and pushed (`0eeae36`).

**All three W09 validation layers now exist:** browser (`required`/`maxLength` in `App.jsx`) → API (`Field(...)` in `schemas.py`, 422) → database (`unique=True` in `models.py`, 409).

> **PowerShell gotcha:** a bare `--` gets swallowed (`npm run dev -- --host` doesn't work). Use `npx vite --host`, or quote it: `'--'`.
> **Starting work:** terminal #1 → `cd crud-app\frontend` → `npx vite`; terminal #2 (venv) → `cd crud-app\backend` → `uvicorn main:app --reload`.

## Phase 5: The same front-end served by FastAPI, locally: 🟡 nearly done

- [x] `npm run build` → plain files in `crud-app/frontend/dist/` (`index.html` + one JS + one CSS). `dist` is ignored by Git.
- [x] `main.py` (I typed it): `/` became **`/health`**, and `app.mount("/", StaticFiles(...))` is the **last** thing registered. The folder path is built from `__file__`, not a relative path.
- [x] Understood why: relative paths are measured from the **folder the program was started in**, not from the file (proof: two `test.db` files in the project). Routes are checked **top to bottom, first match wins**, so the catch-all mount must be last. See the cheatsheet, sections 10 and 11.
- [ ] Test at `http://localhost:8000` with Vite off. This is exactly what the cloud will run. Check for `OPTIONS` lines.
- [ ] Commit and push.

**Result: both ways.**
| | Local development | Cloud |
|---|---|---|
| Front-end | `npm run dev` (instant reload, :5173) | built files served by FastAPI |
| Backend | `uvicorn --reload` (:8000) | uvicorn on the VM (:80) |
| When to use | every day while coding | to check the real deployed app |

## Phase 6: Deploy the full app (one lab session, ~1 hour)

- [ ] `dist/` isn't in Git, so the VM has nothing to serve after `git clone`. Decide: the VM **builds it** (install Node.js, `npm ci`, `npm run build` in `user_data.tpl`), or we **commit `dist/`**.
- [ ] Update `user_data.tpl` for that choice.
- [ ] `terraform apply` → `http://<ip>` shows the **UI**, and `/docs` still shows the API.
- [ ] `terraform destroy` → End Lab.

## Phase 6b (optional): Auto-update the VM when I push (my friend's idea)

Right now, updating the app on AWS means `terraform destroy` + `apply` (a fresh VM each time).
The idea: the **VM checks GitHub itself** and pulls new commits, so a `git push` is all it takes.

- [ ] A small **shell script** on the VM (`.sh`, the Linux version of a Windows `.bat` file): `git pull`, reinstall packages if needed, restart uvicorn.
- [ ] **cron** (Linux's Task Scheduler) runs it every few minutes. Both get set up by `user_data.tpl`, so it's still automatic.
- [ ] Needs **no AWS keys**: the VM only reads from the public GitHub repo. (Correction, 2026-10-18: automating Terraform from GitHub Actions **is** possible. W13 does it by storing the Learner Lab keys as GitHub secrets, re-pasted each session.)
- [ ] This is called **continuous deployment (CD)**. Good material for the CA.

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
