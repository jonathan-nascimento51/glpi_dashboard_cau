# Elevação de privilégios
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`
    [Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Start-Process powershell.exe "-File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "🔧 Restaurando configurações padrão do Windows..."

# 1. Reativar o Serviço de Impressão (PrintSpooler)
Write-Host "`n🖨️  Reativando o serviço de impressão..."
try {
    Set-Service -Name "PrintSpooler" -StartupType Automatic -ErrorAction Stop
    Start-Service -Name "PrintSpooler" -ErrorAction Stop
    Write-Host "✅ Serviço de impressão reativado e iniciado."
}
catch {
    Write-Host "⚠️  Não foi possível reativar o serviço de impressão. Erro: $($_.Exception.Message)"
}

# 2. Reativar o Monitoramento em Tempo Real do Windows Defender
Write-Host "`n🛡️  Reativando o monitoramento em tempo real do Windows Defender..."
try {
    Set-MpPreference -DisableRealtimeMonitoring $false
    Write-Host "✅ Monitoramento em tempo real do Defender reativado."
}
catch {
    Write-Host "⚠️  Não foi possível reativar o Defender. Erro: $($_.Exception.Message)"
}

# 3. Reativar sugestões de conteúdo e notificações
Write-Host "`n🔔 Reativando sugestões e notificações..."
$regPathSuggestions = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
Set-ItemProperty -Path $regPathSuggestions -Name "SubscribedContent-338387Enabled" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
Write-Host "✅ Sugestões de conteúdo reativadas."

$regPathSync = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
Set-ItemProperty -Path $regPathSync -Name "ShowSyncProviderNotifications" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
Write-Host "✅ Notificações de sincronização reativadas."

# 4. Abrir links para reinstalar Apps
Write-Host "`n"
Write-Host "--- Ações Manuais Necessárias ---" -ForegroundColor Yellow
Write-Host "Os links a seguir serão abertos no seu navegador."
Start-Process "ms-windows-store://pdp/?productid=9NZKPSTSNW4P" # Xbox Game Bar
Start-Process "https://www.microsoft.com/pt-br/microsoft-365/onedrive/download" # OneDrive

Write-Host "`n🎉 Restauracao concluida. Pode ser necessario reiniciar o sistema para que todas as alteracoes tenham efeito."
