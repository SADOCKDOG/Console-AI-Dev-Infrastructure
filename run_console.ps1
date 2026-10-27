# Script de inicio PowerShell para la Consola de Gestion Integral
$Host.UI.RawUI.WindowTitle = "Autonomous Dev Control Center - Sdog Farm Software Factory"
Set-Location -Path $PSScriptRoot

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  AUTONOMOUS DEV CONTROL CENTER - WINDOWS DESKTOP CONSOLE" -ForegroundColor Cyan
Write-Host "  Organizacion: Sdog Farm Software Factory (sadogfarm.onmicrosoft.com)" -ForegroundColor Gray
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error en la ejecucion de la consola (Codigo: $LASTEXITCODE)." -ForegroundColor Red
    Read-Host -Prompt "Presione Enter para continuar"
}
