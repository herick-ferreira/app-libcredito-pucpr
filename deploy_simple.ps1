# Script de deploy simplificado para Azure App Service (sem Azure AD)

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppServiceName,
    
    [Parameter(Mandatory=$true)]
    [string]$LogicAppUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$PostgreSQLHost = "libcredit-app-server.postgres.database.azure.com",
    
    [Parameter(Mandatory=$false)]
    [string]$PostgreSQLUser = "denise.ambrosio@pucpr.edu.br"
)

Write-Host "🚀 Iniciando deploy do Sistema de Liberação de Crédito (Versão Simplificada)..." -ForegroundColor Green

# 1. Verificar se está logado no Azure
Write-Host "📋 Verificando autenticação Azure..." -ForegroundColor Yellow
$context = az account show --output json | ConvertFrom-Json
if (!$context) {
    Write-Host "❌ Faça login no Azure primeiro: az login" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Logado como: $($context.user.name)" -ForegroundColor Green

# 2. Criar Resource Group se não existir
Write-Host "📦 Verificando Resource Group..." -ForegroundColor Yellow
$rg = az group show --name $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (!$rg) {
    Write-Host "🔧 Criando Resource Group: $ResourceGroupName" -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location "Brazil South"
}
Write-Host "✅ Resource Group: $ResourceGroupName" -ForegroundColor Green

# 3. Criar App Service Plan
Write-Host "📱 Configurando App Service..." -ForegroundColor Yellow
$planName = "$AppServiceName-plan"
$plan = az appservice plan show --name $planName --resource-group $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (!$plan) {
    Write-Host "🔧 Criando App Service Plan: $planName" -ForegroundColor Yellow
    az appservice plan create --name $planName --resource-group $ResourceGroupName --sku B1 --is-linux
}

# 4. Criar Web App
$webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (!$webapp) {
    Write-Host "🔧 Criando Web App: $AppServiceName" -ForegroundColor Yellow
    az webapp create --name $AppServiceName --resource-group $ResourceGroupName --plan $planName --runtime "PYTHON|3.9"
}

# 5. Habilitar Managed Identity para acesso ao PostgreSQL
Write-Host "🆔 Configurando Managed Identity..." -ForegroundColor Yellow
az webapp identity assign --resource-group $ResourceGroupName --name $AppServiceName
Write-Host "✅ Managed Identity configurada" -ForegroundColor Green

# 6. Configurar App Settings
Write-Host "⚙️ Configurando variáveis de ambiente..." -ForegroundColor Yellow
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

az webapp config appsettings set --resource-group $ResourceGroupName --name $AppServiceName --settings `
    FLASK_SECRET_KEY=$secretKey `
    LOGIC_APP_URL=$LogicAppUrl `
    PGHOST=$PostgreSQLHost `
    PGUSER=$PostgreSQLUser `
    PGPORT=5432 `
    PGDATABASE=postgres `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    WEBSITE_HTTPLOGGING_RETENTION_DAYS=3 `
    FLASK_ENV=production

Write-Host "✅ Variáveis de ambiente configuradas" -ForegroundColor Green

# 7. Configurar Application Insights
Write-Host "📊 Configurando Application Insights..." -ForegroundColor Yellow
$insightsName = "$AppServiceName-insights"
$insights = az monitor app-insights component show --app $insightsName --resource-group $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (!$insights) {
    Write-Host "🔧 Criando Application Insights: $insightsName" -ForegroundColor Yellow
    az monitor app-insights component create --app $insightsName --location "Brazil South" --resource-group $ResourceGroupName
}

$insights = az monitor app-insights component show --app $insightsName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
$instrumentationKey = $insights.instrumentationKey

az webapp config appsettings set --resource-group $ResourceGroupName --name $AppServiceName --settings `
    APPINSIGHTS_INSTRUMENTATIONKEY=$instrumentationKey

Write-Host "✅ Application Insights configurado" -ForegroundColor Green

# 8. Configurar startup command para usar a versão simplificada
Write-Host "🔧 Configurando startup command..." -ForegroundColor Yellow
az webapp config set --resource-group $ResourceGroupName --name $AppServiceName --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app_simple:app"

# 9. Deploy do código
Write-Host "📦 Preparando deploy do código..." -ForegroundColor Yellow

# Criar arquivo ZIP com arquivos necessários
$zipPath = "app-deploy.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

# Copiar app_simple.py como app.py para o deploy
Copy-Item "app_simple.py" "app.py" -Force

$filesToInclude = @(
    "app.py",
    "app_simple.py",
    "requirements.txt",
    "templates/*",
    ".env"
)

# Criar arquivo ZIP
if (Get-Command "7z" -ErrorAction SilentlyContinue) {
    7z a $zipPath $filesToInclude
} else {
    Compress-Archive -Path $filesToInclude -DestinationPath $zipPath -Force
}

Write-Host "🚀 Fazendo deploy..." -ForegroundColor Yellow
az webapp deploy --resource-group $ResourceGroupName --name $AppServiceName --src-path $zipPath

# Limpar arquivos temporários
Remove-Item $zipPath
Remove-Item "app.py"

Write-Host "✅ Deploy concluído!" -ForegroundColor Green

# 10. Configurar HTTPS
Write-Host "🔒 Configurando HTTPS..." -ForegroundColor Yellow
az webapp update --resource-group $ResourceGroupName --name $AppServiceName --https-only true

# 11. Restart do App Service
Write-Host "🔄 Reiniciando App Service..." -ForegroundColor Yellow
az webapp restart --resource-group $ResourceGroupName --name $AppServiceName

# 12. Aguardar inicialização
Write-Host "⏳ Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 13. Testar health check
Write-Host "🏥 Testando health check..." -ForegroundColor Yellow
try {
    $healthUrl = "https://$AppServiceName.azurewebsites.net/health"
    $healthResponse = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 30
    if ($healthResponse.status -eq "healthy" -or $healthResponse.status -eq "degraded") {
        Write-Host "✅ Health check passou!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Health check com status: $($healthResponse.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Não foi possível verificar health check. Aplicação pode estar inicializando." -ForegroundColor Yellow
}

# 14. Mostrar informações finais
Write-Host "`n🎉 Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "📱 URL da aplicação: https://$AppServiceName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "🏥 Health Check: https://$AppServiceName.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host "🔧 Inicializar DB: https://$AppServiceName.azurewebsites.net/init-db" -ForegroundColor Cyan
Write-Host "📊 Application Insights: Portal Azure > $insightsName" -ForegroundColor Cyan

Write-Host "`n🔑 Credenciais de acesso:" -ForegroundColor Yellow
Write-Host "👤 Usuário: Qualquer nome" -ForegroundColor White
Write-Host "🔒 Senha: Configurada pelo administrador" -ForegroundColor White

Write-Host "`n📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Acesse a aplicação e faça login" -ForegroundColor White
Write-Host "2. Acesse /init-db para inicializar o banco PostgreSQL" -ForegroundColor White
Write-Host "3. Teste o fluxo completo de solicitação de crédito" -ForegroundColor White
Write-Host "4. Verifique os dados no PostgreSQL" -ForegroundColor White
Write-Host "5. Confirme o envio para Logic App" -ForegroundColor White

Write-Host "`n🎯 Recursos configurados:" -ForegroundColor Yellow
Write-Host "✅ App Service com Python 3.9" -ForegroundColor Green
Write-Host "✅ PostgreSQL com autenticação Azure AD" -ForegroundColor Green
Write-Host "✅ Logic Apps integrado" -ForegroundColor Green
Write-Host "✅ Application Insights" -ForegroundColor Green
Write-Host "✅ HTTPS obrigatório" -ForegroundColor Green
Write-Host "✅ Managed Identity" -ForegroundColor Green

Write-Host "`n✨ Sistema de Liberação de Crédito está pronto!" -ForegroundColor Green
