Write-Host "Starting AI Coding Assistant backend..."

uvicorn backend.app.main:app --reload
