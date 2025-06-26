# Script PowerShell para Deploy Automatizado no Azure
# Execute como Administrador

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup = "rg-libcredito",
    
    [Parameter(Mandatory=$true)]
    [string]$AppName = "app-libcredito-pucpr",
    
    [Parameter(Mandatory=$true)]
    [string]$SqlPassword,
    
    [Parameter(Mandatory=$true)]
    [string]$LogicAppUrl
)

Write-Host "🚀 INICIANDO DEPLOY AUTOMATIZADO PARA AZURE" -ForegroundColor Green
Write-Host "=" * 60

# Verificar se Azure CLI está instalado
Write-Host "📋 Verificando Azure CLI..." -ForegroundColor Yellow
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI não encontrado. Instalando..." -ForegroundColor Red
    Write-Host "Baixando Azure CLI..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
    Write-Host "Instalando Azure CLI (aguarde)..." -ForegroundColor Yellow
    Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
    Write-Host "✅ Azure CLI instalado com sucesso" -ForegroundColor Green
}

# Login no Azure
Write-Host "🔐 Fazendo login no Azure..." -ForegroundColor Yellow
az login

# Verificar se Resource Group existe
Write-Host "📁 Verificando Resource Group..." -ForegroundColor Yellow
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "false") {
    Write-Host "📁 Criando Resource Group: $ResourceGroup" -ForegroundColor Yellow
    az group create --name $ResourceGroup --location brazilsouth
    Write-Host "✅ Resource Group criado" -ForegroundColor Green
} else {
    Write-Host "✅ Resource Group já existe" -ForegroundColor Green
}

# Verificar se App Service Plan existe
Write-Host "📋 Verificando App Service Plan..." -ForegroundColor Yellow
$planExists = az appservice plan list --resource-group $ResourceGroup --query "[?name=='plan-libcredito'].name" --output tsv
if (-not $planExists) {
    Write-Host "📋 Criando App Service Plan..." -ForegroundColor Yellow
    az appservice plan create --name plan-libcredito --resource-group $ResourceGroup --sku B1 --is-linux
    Write-Host "✅ App Service Plan criado" -ForegroundColor Green
} else {
    Write-Host "✅ App Service Plan já existe" -ForegroundColor Green
}

# Verificar se Web App existe
Write-Host "🌐 Verificando Web App..." -ForegroundColor Yellow
$appExists = az webapp list --resource-group $ResourceGroup --query "[?name=='$AppName'].name" --output tsv
if (-not $appExists) {
    Write-Host "🌐 Criando Web App: $AppName" -ForegroundColor Yellow
    az webapp create --resource-group $ResourceGroup --plan plan-libcredito --name $AppName --runtime "PYTHON|3.11"
    Write-Host "✅ Web App criado" -ForegroundColor Green
} else {
    Write-Host "✅ Web App já existe" -ForegroundColor Green
}

# Configurar variáveis de ambiente
Write-Host "⚙️ Configurando variáveis de ambiente..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $ResourceGroup --name $AppName --settings `
  AZURE_SQL_SERVER="server-db-libcredito.database.windows.net" `
  AZURE_SQL_DATABASE="db-libcredito" `
  AZURE_SQL_USERNAME="deniseambrosio" `
  AZURE_SQL_PASSWORD="$SqlPassword" `
  LOGIC_APP_URL="$LogicAppUrl" `
  FLASK_SECRET_KEY="super-secret-key-production-2025-$(Get-Random)" `
  PORT="8000" `
  WEBSITES_PORT="8000"

Write-Host "✅ Variáveis de ambiente configuradas" -ForegroundColor Green

# Preparar arquivos para deploy
Write-Host "📦 Preparando arquivos para deploy..." -ForegroundColor Yellow

# Criar diretório temporário para deploy
$deployDir = ".\deploy_temp"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copiar arquivos essenciais
$essentialFiles = @(
    "app.py",
    "requirements.txt", 
    "wsgi.py",
    "web.config",
    "static",
    "templates"
)

foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $deployDir -Recurse -Force
        Write-Host "✅ Copiado: $file" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Arquivo não encontrado: $file" -ForegroundColor Yellow
    }
}

# Criar arquivo ZIP
Write-Host "📦 Criando arquivo ZIP..." -ForegroundColor Yellow
$zipPath = ".\deploy.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

# Usar PowerShell 5+ Compress-Archive
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipPath -Force
Write-Host "✅ Arquivo ZIP criado: $zipPath" -ForegroundColor Green

# Deploy via ZIP
Write-Host "🚀 Fazendo deploy da aplicação..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $ResourceGroup --name $AppName --src $zipPath

Write-Host "✅ Deploy concluído!" -ForegroundColor Green

# Aguardar inicialização
Write-Host "⏳ Aguardando inicialização da aplicação..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Testar aplicação
Write-Host "🧪 Testando aplicação..." -ForegroundColor Yellow
$appUrl = "https://$AppName.azurewebsites.net"
$healthUrl = "$appUrl/health"

try {
    $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 30
    if ($response.status -eq "healthy") {
        Write-Host "✅ Aplicação funcionando corretamente!" -ForegroundColor Green
        Write-Host "🌐 URL da aplicação: $appUrl" -ForegroundColor Cyan
        Write-Host "🔧 Health check: $healthUrl" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ Aplicação respondendo mas com status: $($response.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro ao testar aplicação: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔍 Verifique os logs no Portal Azure" -ForegroundColor Yellow
}

# Limpeza
Write-Host "🧹 Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item $deployDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🎉 DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "📱 URL da Aplicação: $appUrl" -ForegroundColor Cyan
Write-Host "🔧 Health Check: $healthUrl" -ForegroundColor Cyan
Write-Host "📊 Portal Azure: https://portal.azure.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Acesse a aplicação e teste o login (senha: 123456)" -ForegroundColor White
Write-Host "2. Faça uma solicitação de crédito de teste" -ForegroundColor White
Write-Host "3. Verifique se o Logic App está recebendo notificações" -ForegroundColor White
Write-Host "4. Configure domínio customizado (opcional)" -ForegroundColor White
Write-Host ""
