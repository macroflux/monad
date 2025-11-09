# Orchestrator-REN Demo Script (PowerShell)
# Demonstrates ticket creation and execution

Write-Host "==> Starting Orchestrator-REN..." -ForegroundColor Green

# Start the service in background
$job = Start-Job -ScriptBlock {
    # Use the script's directory as the working directory
    Set-Location $using:PSScriptRoot
    # Use the Python executable from the virtual environment, relative to the script location
    & "$using:PSScriptRoot/../../.venv/Scripts/python.exe" main.py
}

Start-Sleep -Seconds 3

Write-Host "`n==> 1. Check service health" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
$response | ConvertTo-Json -Depth 5

Write-Host "`n==> 2. Create a drive ticket" -ForegroundColor Cyan
$ticketBody = @{
    command = "drive"
    params = @{
        speed = 1.5
        direction = 90
        duration_seconds = 5
    }
    priority = "high"
} | ConvertTo-Json

$ticket = Invoke-RestMethod -Uri "http://localhost:8000/ticket" -Method Post -Body $ticketBody -ContentType "application/json"
$ticket | ConvertTo-Json -Depth 5
$ticketId = $ticket.id
Write-Host "Created ticket: $ticketId" -ForegroundColor Yellow

Write-Host "`n==> 3. Execute the ticket" -ForegroundColor Cyan
$executeBody = @{
    ticket_id = $ticketId
} | ConvertTo-Json

$executeResult = Invoke-RestMethod -Uri "http://localhost:8000/execute" -Method Post -Body $executeBody -ContentType "application/json"
$executeResult | ConvertTo-Json -Depth 5

Write-Host "`n==> 4. Check ticket status" -ForegroundColor Cyan
$ticketStatus = Invoke-RestMethod -Uri "http://localhost:8000/ticket/$ticketId" -Method Get
$ticketStatus | ConvertTo-Json -Depth 5

Write-Host "`n==> 5. Create a scan ticket" -ForegroundColor Cyan
$scanBody = @{
    command = "scan"
    params = @{}
    priority = "normal"
} | ConvertTo-Json

$scanTicket = Invoke-RestMethod -Uri "http://localhost:8000/ticket" -Method Post -Body $scanBody -ContentType "application/json"
$scanTicket | ConvertTo-Json -Depth 5

Write-Host "`n==> 6. List all tickets" -ForegroundColor Cyan
$tickets = Invoke-RestMethod -Uri "http://localhost:8000/tickets?limit=10" -Method Get
$tickets | ConvertTo-Json -Depth 5

Write-Host "`n==> 7. View metrics" -ForegroundColor Cyan
$metrics = Invoke-RestMethod -Uri "http://localhost:8000/telemetry/metrics" -Method Get
$metrics | ConvertTo-Json -Depth 5

Write-Host "`n==> 8. View events" -ForegroundColor Cyan
$events = Invoke-RestMethod -Uri "http://localhost:8000/telemetry/events" -Method Get
$events | ConvertTo-Json -Depth 5

Write-Host "`n==> Stopping service..." -ForegroundColor Green
Stop-Job -Job $job
Remove-Job -Job $job

Write-Host "Demo complete!" -ForegroundColor Green
