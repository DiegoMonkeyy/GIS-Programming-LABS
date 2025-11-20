# run_lab5.ps1 - wrapper to run Lab5.py with ArcGIS Python if available
param(
    [string]$Garage = "Northside Parking Garage",
    [string]$Radius = "150",
    [switch]$DryRun
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$lab5Path = Join-Path $repoRoot 'LAB 4\Lab5.py'

# Candidate ArcGIS env python paths (adjust or add if needed)
$arcgisCandidates = @(
    "$env:USERPROFILE\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone\python.exe",
    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe",
    "$env:USERPROFILE\Miniconda3\python.exe",
    "$env:USERPROFILE\Miniconda3\envs\base\python.exe"
)

$pythonExe = $null
foreach ($p in $arcgisCandidates) {
    if (Test-Path $p) { $pythonExe = $p; break }
}

if (-not $pythonExe) {
    Write-Host "ArcGIS/conda python not found in common locations. Trying 'python' on PATH..." -ForegroundColor Yellow
    $pythonExe = 'python'
}

$argsList = @('--garage', "`"$Garage`"", '--radius', $Radius)
if ($DryRun) { $argsList += '--dry-run' }

Write-Host "Running Lab5 with interpreter: $pythonExe"
Write-Host "Command: $pythonExe $lab5Path $($argsList -join ' ')"

& $pythonExe $lab5Path @argsList

if ($LASTEXITCODE -ne 0) {
    Write-Host "Lab5 exited with code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
} else {
    Write-Host "Lab5 finished successfully" -ForegroundColor Green
}
