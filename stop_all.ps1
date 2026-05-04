$ErrorActionPreference = "Continue"

$Root = "C:\Users\jhons\Downloads\Microservicios"
$PidFile = Join-Path $Root ".running-services.json"

if (-not (Test-Path $PidFile)) {
    Write-Host "No se encontro archivo de procesos: $PidFile"
    exit 0
}

$items = Get-Content $PidFile -Raw | ConvertFrom-Json
foreach ($it in $items) {
    try {
        Stop-Process -Id $it.pid -Force -ErrorAction Stop
        Write-Host "Detenido $($it.name) PID=$($it.pid)"
    } catch {
        Write-Warning "No se pudo detener PID=$($it.pid) ($($it.name))"
    }
}

Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
Write-Host "Proceso de cierre completado."
