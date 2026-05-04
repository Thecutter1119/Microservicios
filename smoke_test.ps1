param(
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Continue"

$services = @(
    @{ Name="ms-autenticacion"; Url="http://localhost:8101/health" },
    @{ Name="ms-roles"; Url="http://localhost:8102/health" },
    @{ Name="ms-usuarios"; Url="http://localhost:8103/health" },
    @{ Name="ms-inventario"; Url="http://localhost:8104/health" },
    @{ Name="ms-espacios"; Url="http://localhost:8105/health" },
    @{ Name="ms-reservas"; Url="http://localhost:8106/health" },
    @{ Name="ms-presupuesto"; Url="http://localhost:8107/health" },
    @{ Name="ms-gastos"; Url="http://localhost:8108/health" },
    @{ Name="ms-facturacion"; Url="http://localhost:8109/health" },
    @{ Name="ms-pedidos"; Url="http://localhost:8110/health" },
    @{ Name="ms-domicilios"; Url="http://localhost:8111/health" },
    @{ Name="ms-proveedores"; Url="http://localhost:8112/health" },
    @{ Name="ms-programas"; Url="http://localhost:8113/health" },
    @{ Name="ms-matriculas"; Url="http://localhost:8114/health" },
    @{ Name="ms-calificaciones"; Url="http://localhost:8115/health" },
    @{ Name="ms-horarios"; Url="http://localhost:8116/health" },
    @{ Name="ms-notificaciones"; Url="http://localhost:8117/health" },
    @{ Name="ms-auditoria"; Url="http://localhost:8118/health" },
    @{ Name="ms-reportes"; Url="http://localhost:8119/health" }
)

function Test-Endpoint($name, $url) {
    try {
        $res = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 5
        return [pscustomobject]@{
            name = $name
            url = $url
            ok = $true
            success = $res.success
            message = $res.message
        }
    } catch {
        return [pscustomobject]@{
            name = $name
            url = $url
            ok = $false
            success = $false
            message = $_.Exception.Message
        }
    }
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$last = @()

do {
    $last = @()
    foreach ($svc in $services) {
        $last += Test-Endpoint $svc.Name $svc.Url
    }
    $failed = $last | Where-Object { -not $_.ok }
    if ($failed.Count -eq 0) {
        break
    }
    Start-Sleep -Seconds 3
} while ((Get-Date) -lt $deadline)

Write-Host ""
Write-Host "==== RESULTADO SMOKE TEST ===="
$last | ForEach-Object {
    $status = if ($_.ok) { "OK" } else { "FAIL" }
    Write-Host "$status`t$($_.name)`t$($_.url)`t$($_.message)"
}

$failCount = ($last | Where-Object { -not $_.ok }).Count
if ($failCount -gt 0) {
    Write-Host ""
    Write-Warning "Hay $failCount servicio(s) sin health OK."
    exit 1
}

Write-Host ""
Write-Host "Todos los servicios respondieron /health correctamente."
exit 0
