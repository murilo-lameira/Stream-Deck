# Script para registrar o Stream Deck na inicializacao automatica do Windows
# Ele cria uma chave no Registro do Usuario (HKCU) apontando para o iniciar_streamdeck.vbs

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$vbsPath = Join-Path -Path $scriptPath -ChildPath "iniciar_streamdeck.vbs"
$registryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$name = "StreamDeckServer"

Write-Host "Configurando Stream Deck para iniciar com o Windows..." -ForegroundColor Cyan

if (Test-Path $vbsPath) {
    # Registra no run usando o wscript.exe para garantir que rodará em background
    Set-ItemProperty -Path $registryPath -Name $name -Value "wscript.exe `"$vbsPath`""
    Write-Host "Sucesso! O atalho invisivel foi registrado no Windows." -ForegroundColor Green
    Write-Host "Caminho configurado: $vbsPath" -ForegroundColor DarkGray
} else {
    Write-Host "Erro: Arquivo iniciar_streamdeck.vbs nao encontrado na pasta do script." -ForegroundColor Red
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

