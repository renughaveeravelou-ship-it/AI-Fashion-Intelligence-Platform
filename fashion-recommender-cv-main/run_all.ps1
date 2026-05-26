# Start Smart Stylist full stack (backend + frontend)
$root = $PSScriptRoot
Write-Host "Starting API on http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; .\run_backend.ps1"
Start-Sleep -Seconds 3
Write-Host "Starting web app on http://localhost:5173 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; .\run_frontend.ps1"
Write-Host "Done. Open http://localhost:5173 in your browser."
