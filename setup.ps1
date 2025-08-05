Write-Host "Bootstrapping BdeB-Go..."
if (-not (Test-Path ".\backend\.venv")) {
    Write-Host '  * Creating Python virtualenv in backend/.venv...'
    python -m venv .\backend\.venv
}

Write-Host '  * Activating backend virtualenv & installing Python deps...'
. .\backend\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r .\backend\requirements.txt

Write-Host '  * Installing frontend dependencies...'
Push-Location .\UI
npm install
Pop-Location

Write-Host 'Bootstrap complete! Run .\run.ps1 to start the app.'
