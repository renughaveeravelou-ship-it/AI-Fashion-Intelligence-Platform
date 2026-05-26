Set-Location $PSScriptRoot
pip install -r backend/requirements.txt -q
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
