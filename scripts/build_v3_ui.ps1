$ErrorActionPreference = "Stop"

$StudioDir = "C:\dev\ui-studio"
$TargetDist = Join-Path $PSScriptRoot "..\src\ui_dist"

if (-not (Test-Path $StudioDir)) {
    throw "UI Studio directory not found: $StudioDir"
}

Push-Location $StudioDir
try {
    npm run build:rightwheel-v3
    if ($LASTEXITCODE -ne 0) {
        throw "Vite rightwheel-v3 build failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

if (Test-Path $TargetDist) {
    Remove-Item -Recurse -Force $TargetDist
}
Copy-Item -Recurse -Force (Join-Path $StudioDir "dist-rightwheel-v3") $TargetDist
Write-Host "Built and synced RightWheel V3 UI -> $TargetDist"
