
# First-Time Run Checklist — Inequality Inertia Simulator (VS Code)

## 0) Prereqs
- Install **Python 3.10+** (check "Add Python to PATH" on Windows).
- Install **Visual Studio Code** + extensions: *Python* (ms-python.python), *Pylance*.

## 1) Open the project
- VS Code → **File → Open Folder…** → select the folder with `app.py` and `requirements.txt`.

## 2) Create a virtual environment
```bash
# Windows (Command Prompt)
python -m venv venv

# Windows (PowerShell)
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

## 3) Activate the environment
```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

> If PowerShell blocks activation: run **as Admin** once:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4) Select the interpreter in VS Code
- **Ctrl+Shift+P** (Cmd+Shift+P on macOS) → `Python: Select Interpreter` → pick the one inside **venv**.

## 5) Install dependencies
```bash
pip install -r requirements.txt
```

## 6) Run the app
```bash
streamlit run app.py
```
- Open the local URL (e.g., http://localhost:8501).

## 7) Update dependencies (optional)
```bash
pip install <package>
pip freeze > requirements.txt
```

## 8) Deactivate when done
```bash
deactivate
```

---

## Quick Troubleshooting
- **`streamlit: command not found`**: your venv isn’t active or install failed → activate and `pip install -r requirements.txt`.
- **PowerShell policy error**: run the `Set-ExecutionPolicy` command above, then re-activate.
- **Altair/Chart display issues**: update Altair and Streamlit → `pip install -U altair streamlit`.
- **Wrong Python selected**: re-run `Python: Select Interpreter` and choose the `venv` one.
