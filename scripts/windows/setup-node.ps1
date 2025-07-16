# Caminho onde o nvm-windows foi instalado
$NvmPath = "C:\nvm4w"
$NodeSymlinkPath = "C:\Program Files\nodejs"

# Verifica e adiciona ao PATH, se necessário
if (-not ($env:Path -like "*$NvmPath*")) {
    $env:Path += ";$NvmPath;$NodeSymlinkPath"
    Write-Host "[✔] PATH ajustado para incluir NVM e Node"
}

# Lê a versão do Node (via .nvmrc ou usa LTS)
$nodeVersion = if (Test-Path ".nvmrc") {
    Get-Content .nvmrc | Select-Object -First 1
} else {
    "lts"
}

Write-Host "`n📦 Instalando Node.js versão: $nodeVersion"
nvm install $nodeVersion
nvm use $nodeVersion

# Verificações básicas
Write-Host "`n✅ Verificando versões instaladas:"
node -v
npm -v
npx -v

# Instala dependências do projeto
if (Test-Path "package.json") {
    Write-Host "`n📁 Instalando dependências do projeto..."
    npm install
}

# Instala playwright se detectado
if (Test-Path "node_modules/playwright") {
    Write-Host "`n🎭 Instalando navegadores do Playwright..."
    npx playwright install
}

# Instala extras se detectado no package.json
if (Test-Path "package.json") {
    $pkg = Get-Content package.json -Raw | ConvertFrom-Json

    if ($pkg.devDependencies."vite") {
        Write-Host "`n⚡ Vite detectado – ok"
    }

    if ($pkg.devDependencies."typescript") {
        Write-Host "`n🔠 TypeScript detectado – ok"
    }

    if ($pkg.devDependencies."tailwindcss") {
        Write-Host "`n🌬️ TailwindCSS detectado – ok"
    }
}

Write-Host "`n🎉 Setup concluído com sucesso!"
