# Elevação de privilégios
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`
    [Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Start-Process powershell.exe "-File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "🔧 Otimizando Windows para ambiente de desenvolvimento..."

# Desativar serviços que consomem memória
$services = @(
    "DiagTrack",         # Telemetria
    "MapsBroker",        # Mapas em segundo plano
    "Fax",               # Fax, se não usa
    "RetailDemo",        # Modo loja
    "PrintSpooler"       # Impressora (desative se não usa)
)

foreach ($svc in $services) {
    Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
    Set-Service -Name $svc -StartupType Disabled
    Write-Host "✅ Serviço desativado: $svc"
}

# Reduzir impacto do Windows Defender sem desativar completamente
Set-MpPreference -DisableRealtimeMonitoring $true
Write-Host "⚠️ Monitoramento em tempo real do Defender desativado (pode ser reativado depois)"

# Desativar Xbox Game Bar e apps integrados inúteis
Get-AppxPackage *xbox* | Remove-AppxPackage -ErrorAction SilentlyContinue
Write-Host "🎮 Xbox apps removidos"

# Desativar sugestões de conteúdo e notificações de sincronização
$regPathSuggestions = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
if (-not (Test-Path $regPathSuggestions)) { New-Item -Path $regPathSuggestions -Force -ErrorAction SilentlyContinue | Out-Null }
Set-ItemProperty -Path $regPathSuggestions -Name "SubscribedContent-338387Enabled" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Write-Host "✅ Sugestões de conteúdo desativadas"

$regPathSync = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
if (-not (Test-Path $regPathSync)) { New-Item -Path $regPathSync -Force -ErrorAction SilentlyContinue | Out-Null }
Set-ItemProperty -Path $regPathSync -Name "ShowSyncProviderNotifications" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
Write-Host "✅ Notificações de sincronização desativadas"

# Desativar e desinstalar o OneDrive de forma mais robusta
Write-Host "☁️  Tentando desativar e desinstalar o OneDrive..."
Stop-Process -Name "OneDrive" -Force -ErrorAction SilentlyContinue

$oneDriveUninstaller = if (Test-Path "$env:SystemRoot\SysWOW64\OneDriveSetup.exe") {
    "$env:SystemRoot\SysWOW64\OneDriveSetup.exe"
} elseif (Test-Path "$env:SystemRoot\System32\OneDriveSetup.exe") {
    "$env:SystemRoot\System32\OneDriveSetup.exe"
}

if ($oneDriveUninstaller) {
    Start-Process -FilePath $oneDriveUninstaller -ArgumentList "/uninstall" -Wait
    Write-Host "✅ Desinstalação do OneDrive iniciada."
} else {
    Write-Host "⚠️  Desinstalador do OneDrive não encontrado."
}

Write-Host "`n🎉 Otimização concluída. Recomenda-se reiniciar o sistema para aplicar todas as alterações."