# How my app got onto the internet

What W11 and W12 are really about, in plain words. Read this before re-doing the deploy.

---

## 1. The whole thing in one sentence

> I **rented a computer from Amazon**, used **Terraform** to order it for me, logged into it, and ran **the same commands I run on my laptop** (venv, pip install, uvicorn), so my FastAPI app now answers on a public IP address that anyone can visit.

Everything below is detail on that sentence.

---

## 2. The big picture

```
 MY LAPTOP (Windows)                 GITHUB                    AWS (Amazon's data centre, us-east-1)
 ───────────────────                 ──────                    ─────────────────────────────────────
 code in VS Code ── git push ──►  Cloud-Dev-App repo
                                         │
 Terraform ── "please create a VM" ──────┼──────────────►  ┌───────────── EC2 VM (Ubuntu Linux) ─────────────┐
   (uses my AWS Academy keys)            │                 │  git clone ◄──┘                                  │
                                                           │  venv + pip install                              │
                                                           │  uvicorn main:app --host 0.0.0.0 --port 80       │
                                                           │        └─► FastAPI ─► SQLite (test.db on the VM) │
                                                           └──────────────────────▲───────────────────────────┘
                                                                                  │ port 80 allowed by the
 ANY BROWSER  ── http://54.160.134.189/docs ──────────────────────────────────────┘ security group (firewall)
```

There are three separate computers in this picture:
1. **My laptop**, where I write code and run Terraform.
2. **GitHub**, where the code is stored. The VM downloads it from here.
3. **The EC2 VM**, where the app actually runs for the world.

---

## 3. The words, explained

### Cloud
**Renting someone else's computers over the internet** instead of buying your own. You pay per hour, create machines in minutes, and delete them when you're done.

### AWS (Amazon Web Services)
Amazon's cloud. Others: Azure (Microsoft) and GCP (Google). AWS has hundreds of services. We used one main one:

| Service | What it is | My analogy |
|---|---|---|
| **EC2** (Elastic Compute Cloud) | A **virtual computer** (VM) you rent | renting a laptop that lives in Amazon's building |
| **Security group** | A **firewall** for the VM: which ports are open | the building's door rules: port 80 open to everyone, 22 for admin only |
| **AMI** (Amazon Machine Image) | The **operating system image** the VM starts from | "factory reset with Ubuntu 26.04 installed" |
| **Region** (`us-east-1`) | Which data centre (here, North Virginia) | the city the building is in |

### AWS Academy Learner Lab
A **school sandbox AWS account**.
- **$50 budget** for the whole module. If it runs out, everything is lost.
- **Start Lab** turns on access for a **4-hour session**. The green dot means it's ready.
- **AWS Details → AWS CLI** gives **temporary keys**, valid for that session only.
- When the session ends, AWS **stops** EC2 VMs (stops, not deletes). They still exist.

⚠️ **The terminal on the Learner Lab page** (`eee_W_...@172.31.2.87`) is **not my server**. It's a small helper machine AWS gives you for typing AWS commands. My server was the one I connected to through **EC2 → Connect** (`ubuntu@ip-172-31-42-68`).

### Credentials file (`C:\Users\ASUS\.aws\credentials`)
The **keys** that let programs on my laptop act as me in AWS. Terraform reads this file automatically.
- They're like a password, so **never commit them and never share them** (cut them out of screenshots).
- They expire after each session, so paste fresh ones every time.

### Terraform = Infrastructure as Code (IaC)
Instead of clicking around the AWS website to create a server, I **write down what I want** in `.tf` files, and Terraform makes it happen.

| Command | What it does | Analogy |
|---|---|---|
| `terraform init` | Downloads the AWS plugin (once per folder) | installing the app that talks to the shop |
| `terraform plan` | **Shows** what it would create or change, **without doing it** | reading the shopping list before paying |
| `terraform apply` | **Creates** it for real (asks `yes`) | paying and getting it delivered |
| `terraform destroy` | **Deletes** everything it created | returning it all |

**Why bother instead of clicking?**
- **Repeatable**: the same files create the same server every time, for me, a teammate or the lecturer.
- **Versioned**: the `.tf` files live in Git, like code.
- **Easy cleanup**: `destroy` removes everything, and nothing gets forgotten.

**`terraform.tfstate`** is Terraform's **memory** of what it created (IDs, IP addresses...). It's how `destroy` knows what to delete. **Don't delete it while things still exist in AWS**, and **don't commit it**.

---

## 4. What `main.tf` asks AWS for

```
provider "aws"                  → "talk to AWS, in us-east-1"
data "aws_ssm_parameter"        → "look up the newest Ubuntu 26.04 image ID"     (read-only lookup)
data "aws_ip_ranges"            → "look up EC2 Instance Connect's IP addresses"  (read-only lookup)
resource "aws_security_group"   → "create a firewall: port 80 open, port 22 for Instance Connect"
resource "aws_instance"         → "create a t2.micro VM from that image, behind that firewall"
output "public_ip"              → "print the VM's public IP when done"
```
- `data` = **look something up**. `resource` = **create something**.
- `variables.tf` holds the settings (region, VM size, name), so they're easy to change in one place.

---

## 5. What I did on the VM, and why each step

Every command is something I've **already done on Windows**, just on Linux:

| On the VM (Linux) | What it does | My Windows equivalent |
|---|---|---|
| `sudo -i` | become **root** (admin) | "Run as administrator" |
| `apt-get update -y` | refresh the list of installable software | — |
| `apt-get install -y python3.14-venv` | install Python's venv tool | installing Python |
| `python3.14 -m venv venv` | create a venv | `python -m venv venv` |
| `source venv/bin/activate` | activate it | `.\venv\Scripts\Activate.ps1` |
| `git clone https://github.com/NoMaRu123/Cloud-Dev-App.git` | download my code | — (I already have it) |
| `cd Cloud-Dev-App/crud-app/backend` | go to the app folder | same |
| `pip install -r requirements.txt` | install packages | same |
| `uvicorn main:app --host 0.0.0.0 --port 80` | start the app | `uvicorn main:app --reload` |

### The two differences in the uvicorn line
- **`--host 0.0.0.0`**: on my laptop uvicorn listens on `127.0.0.1`, which means **only this computer** can connect. `0.0.0.0` means **accept connections from anywhere**. Without it, the browser couldn't reach the VM.
- **`--port 80`**: 80 is the **default port for http**. That's why `http://54.160.134.189` works without typing `:80`. Ports below 1024 need admin rights, which is why we used `sudo -i`.

### The two mistakes I hit, and what they taught me
1. `git clone https://github.com/your-account/your-repo.git` asked for a password. That's the slide's **placeholder** URL. A repo that doesn't exist (or is private) makes GitHub ask for login. **Lesson:** replace placeholders.
2. `Could not import module "main"`: I ran uvicorn in the **repo root**, but `main.py` is in `crud-app/backend/`. **Lesson:** uvicorn's `main:app` means "`main.py` *in the current folder*", the same rule as on my laptop.

### Where my data lives
`test.db` (SQLite) is a **file on the VM**. Destroy the VM and the data goes with it. Real apps keep the database on a separate service (AWS **RDS**) so servers can be replaced without losing data. That's in the slides' "Looking for more".

---

### Finding the public IP (to visit the app)

`Uvicorn running on http://0.0.0.0:80` is **not** a URL to visit. `0.0.0.0` means "listening on every address". I need the **public IP**.

| Where | How |
|---|---|
| 💻 Laptop PowerShell, in the Terraform folder | `terraform output public_ip`. After a VM stop/start, run `terraform apply -refresh-only` first, because the IP changes |
| 🌐 AWS Console | EC2 → Instances → `sandbox` → **Public IPv4 address** (always current) |
| ☁️ VM terminal (a **2nd** tab if uvicorn is running in the first) | `curl checkip.amazonaws.com` asks an outside service what my public IP is |
| ❌ Not these | `hostname -I` / `ip addr` on the VM only show the **private** IP (172.31.x.x) |

Then visit **`http://<public-ip>/docs`**. Use **http, not https**, because there's no certificate.

---

## 6. W11 vs W12: manual vs automatic

| | W11 (what I did) | W12 (next) |
|---|---|---|
| Terraform creates | an **empty** Ubuntu VM | a VM **plus a startup script** |
| Installing the app | **I** log in and type the commands | the VM runs `user_data.tpl` **by itself** on first boot |
| Folder | `ec2-backend/` (lecturer's W11 files) | `infra/` (W12 files, with fixes) |
| After `apply` | connect, type ~8 commands | just wait ~3 min, then open the IP |

**`user_data`** = a bash script AWS runs **once, as root, the first time the VM boots**. It contains exactly the W11 commands, so W12 is "W11, automated". If it fails, its output is in `/var/log/cloud-init-output.log` on the VM.

---

## 7. Lifecycle checklist (every session)

```
START   Learner Lab → Start Lab → green dot
KEYS    AWS Details → AWS CLI → paste into .aws\credentials (they change every session!)
BUILD   terraform init (first time) → plan → apply
USE     http://<public_ip>/docs
CLEAN   terraform destroy → End Lab
```
Skipping **CLEAN** leaves things in AWS that can use up the $50 budget.

---

## 8. Glossary

| Term | Meaning |
|---|---|
| VM | Virtual machine: a computer simulated in software, many per physical server |
| EC2 instance | AWS's name for a VM |
| Public IP | The address the internet uses to reach the VM (`54.160.134.189`) |
| Private IP | The address inside AWS's network (`172.31.x.x`). Not reachable from the internet |
| Port | A numbered "door" on a computer. 80 = http, 443 = https, 22 = SSH, 8000 = my local uvicorn |
| SSH / Instance Connect | Remote terminal login to the VM |
| root | Linux admin user (`sudo -i`) |
| IaC | Infrastructure as Code: servers described in files, created by a tool |
| State file | Terraform's record of what it created |
| user_data | Startup script that runs once on a VM's first boot |
| cloud-init | The program on the VM that runs user_data |
