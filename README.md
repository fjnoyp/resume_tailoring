## Running Instructions

### 1. Setting up the virtual environment:

#### **Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### **Windows (CMD)**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### **Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Running the app locally

```bash
langgraph dev
```

## Running the evaluator

```bash
python evaluators/production_evaluator.py --user-id [target_user_id] --job-id [target_job_id]
```