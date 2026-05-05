param(
    [switch]$InstallDeps = $false,
    [switch]$DryRun = $false,
    [ValidateSet("windows", "background")]
    [string]$Mode = "windows"
)

$ErrorActionPreference = "Stop"

$Root = "C:\Users\jhons\Downloads\Microservicios"
$PidFile = Join-Path $Root ".running-services.json"
$LogDir = Join-Path $Root ".service-logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$services = @(
    @{ Name="ms-roles"; Path="ms-roles"; App="app.main:app"; Port=8102 },
    @{ Name="ms-usuarios"; Path="ms-usuarios"; App="app.main:app"; Port=8103 },
    @{ Name="ms-autenticacion"; Path="ms-autenticacion"; App="app.main:app"; Port=8101 },
    @{ Name="ms-auditoria"; Path="ms-auditoria"; App="app.main:app"; Port=8118 },
    @{ Name="ms-notificaciones"; Path="ms-notificaciones"; App="app.main:app"; Port=8117 },
    @{ Name="ms-inventario"; Path="ms-inventario"; App="app.main:app"; Port=8104 },
    @{ Name="ms-espacios"; Path="ms-espacios"; App="app.main:app"; Port=8105 },
    @{ Name="ms-reservas"; Path="ms-reservas"; App="app.main:app"; Port=8106 },
    @{ Name="ms-presupuesto"; Path="ms-presupuesto"; App="app.main:app"; Port=8107 },
    @{ Name="ms-gastos"; Path="ms-gastos"; App="app.main:app"; Port=8108 },
    @{ Name="ms-facturacion"; Path="ms-facturacion"; App="app.main:app"; Port=8109 },
    @{ Name="ms-programas"; Path="ms-programas"; App="app.main:app"; Port=8113 },
    @{ Name="ms-matriculas"; Path="ms-matriculas"; App="app.main:app"; Port=8114 },
    @{ Name="ms-calificaciones"; Path="ms-calificaciones"; App="app.main:app"; Port=8115 },
    @{ Name="ms-horarios"; Path="ms-horarios"; App="app.main:app"; Port=8116 },
    @{ Name="ms-pedidos"; Path="Ms Pedidos"; App="app.main:app"; Port=8110 },
    @{ Name="ms-domicilios"; Path="MS-Domicilios\ms-domicilios-app"; App="app.main:app"; Port=8111 },
    @{ Name="ms-proveedores"; Path="ms-proveedores"; App="main:app"; Port=8112 },
    @{ Name="ms-reportes"; Path="reportes_service"; App="app.main:app"; Port=8119 }
)

function Ensure-EnvFile($serviceDir) {
    $envFile = Join-Path $serviceDir ".env"
    $exampleFile = Join-Path $serviceDir ".env.example"
    if (-not (Test-Path $envFile) -and (Test-Path $exampleFile)) {
        Copy-Item $exampleFile $envFile
    }
}

function Install-Deps($serviceDir) {
    $req = Join-Path $serviceDir "requirements.txt"
    if (Test-Path $req) {
        Write-Host "Instalando dependencias en $serviceDir"
        python -m pip install -r $req | Out-Host
    }
}

$running = @()

foreach ($svc in $services) {
    $serviceDir = Join-Path $Root $svc.Path
    if (-not (Test-Path $serviceDir)) {
        Write-Warning "No existe carpeta para $($svc.Name): $serviceDir"
        continue
    }

    Ensure-EnvFile $serviceDir
    if ($InstallDeps) {
        Install-Deps $serviceDir
    }

    $args = @("-m","uvicorn",$svc.App,"--host","0.0.0.0","--port",$svc.Port.ToString())
    $stdout = Join-Path $LogDir "$($svc.Name).out.log"
    $stderr = Join-Path $LogDir "$($svc.Name).err.log"

    if ($DryRun) {
        if ($Mode -eq "windows") {
            Write-Host "[DRY-RUN] $($svc.Name) -> powershell -NoExit -Command `"Set-Location '$serviceDir'; python $($args -join ' ')`""
        } else {
            Write-Host "[DRY-RUN] $($svc.Name) -> python $($args -join ' ')  (cwd=$serviceDir)"
        }
        continue
    }

    if ($Mode -eq "windows") {
        $escapedDir = $serviceDir.Replace("'", "''")
        $windowCmd = @(
            "`$Host.UI.RawUI.WindowTitle = '$($svc.Name) : $($svc.Port)'",
            "Set-Location -LiteralPath '$escapedDir'",
            "python $($args -join ' ')"
        ) -join "; "

        $proc = Start-Process -FilePath "powershell" `
            -ArgumentList @("-NoExit", "-Command", $windowCmd) `
            -PassThru
    } else {
        $proc = Start-Process -FilePath "python" `
            -ArgumentList $args `
            -WorkingDirectory $serviceDir `
            -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr `
            -PassThru
    }

    $running += [pscustomobject]@{
        name = $svc.Name
        pid = $proc.Id
        port = $svc.Port
        path = $serviceDir
        health = "http://localhost:$($svc.Port)/health"
    }

    Write-Host "Iniciado $($svc.Name) PID=$($proc.Id) PORT=$($svc.Port)"
    Start-Sleep -Milliseconds 300
}

if (-not $DryRun) {
    $running | ConvertTo-Json -Depth 3 | Set-Content -Path $PidFile -Encoding UTF8
    Write-Host ""
    Write-Host "Servicios iniciados. Archivo PID: $PidFile"
    if ($Mode -eq "background") {
        Write-Host "Logs: $LogDir"
    } else {
        Write-Host "Modo ventanas activo: cada microservicio corre en su propia terminal."
    }
    Write-Host "Para detener todo: .\stop_all.ps1"
}
