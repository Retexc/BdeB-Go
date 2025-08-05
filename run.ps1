Write-Host "🚀 Starting BdeB-Go"

# --- Backend ---
Write-Host "  • Starting admin backend on http://127.0.0.1:5001…"
& .\backend\.venv\Scripts\Activate.ps1
Start-Process -NoNewWindow -FilePath "python" `
  -ArgumentList "-m", "waitress", "--host=127.0.0.1", "--port=5001", "backend.admin:app"

# --- Frontend ---
Write-Host "  • Starting Vite UI on http://localhost:5173…"
Push-Location .\UI
Start-Process -NoNewWindow -FilePath "npm.cmd" -ArgumentList "run", "dev:frontend"
Pop-Location

Write-Host "✅ Bdeb-Go a démarré ! Ouvrez http://localhost:5173 dans votre navigateur pour accéder au tableau de bord."
