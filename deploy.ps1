# Script para deploy automatizado no Azure App Service

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppServiceName,
    
    [Parameter(Mandatory=$true)]
    [string]$KeyVaultName,
    
    [Parameter(Mandatory=$true)]
    [string]$ClientId,
    
    [Parameter(Mandatory=$true)]
    [string]$ClientSecret,
    
    [Parameter(Mandatory=$true)]
    [string]$TenantId,
    
    [Parameter(Mandatory=$true)]
    [string]$LogicAppUrl
)

Write-Host "🚀 Iniciando deploy do Sistema de Liberação de Crédito..." -ForegroundColor Green

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

# 3. Criar Key Vault
Write-Host "🔐 Configurando Key Vault..." -ForegroundColor Yellow
$kv = az keyvault show --name $KeyVaultName --output json 2>$null | ConvertFrom-Json
if (!$kv) {
    Write-Host "🔧 Criando Key Vault: $KeyVaultName" -ForegroundColor Yellow
    az keyvault create --name $KeyVaultName --resource-group $ResourceGroupName --location "Brazil South"
}

# Adicionar segredos ao Key Vault
Write-Host "🔑 Adicionando segredos ao Key Vault..." -ForegroundColor Yellow
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
az keyvault secret set --vault-name $KeyVaultName --name "flask-secret-key" --value $secretKey
az keyvault secret set --vault-name $KeyVaultName --name "azure-client-secret" --value $ClientSecret
Write-Host "✅ Segredos configurados no Key Vault" -ForegroundColor Green

# 4. Criar App Service Plan
Write-Host "📱 Configurando App Service..." -ForegroundColor Yellow
$planName = "$AppServiceName-plan"
$plan = az appservice plan show --name $planName --resource-group $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (!$plan) {
    Write-Host "🔧 Criando App Service Plan: $planName" -ForegroundColor Yellow
    az appservice plan create --name $planName --resource-group $ResourceGroupName --sku B1 --is-linux
}

# 5. Criar Web App
$webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (!$webapp) {
    Write-Host "🔧 Criando Web App: $AppServiceName" -ForegroundColor Yellow
    az webapp create --name $AppServiceName --resource-group $ResourceGroupName --plan $planName --runtime "PYTHON|3.9"
}

# 6. Habilitar Managed Identity
Write-Host "🆔 Configurando Managed Identity..." -ForegroundColor Yellow
az webapp identity assign --resource-group $ResourceGroupName --name $AppServiceName

# Obter Object ID da Managed Identity
$identity = az webapp identity show --resource-group $ResourceGroupName --name $AppServiceName --output json | ConvertFrom-Json
$objectId = $identity.principalId

# Dar permissão ao Key Vault
az keyvault set-policy --name $KeyVaultName --object-id $objectId --secret-permissions get

Write-Host "✅ Managed Identity configurada" -ForegroundColor Green

# 7. Configurar App Settings
Write-Host "⚙️ Configurando variáveis de ambiente..." -ForegroundColor Yellow
$keyVaultUrl = "https://$KeyVaultName.vault.azure.net/"

az webapp config appsettings set --resource-group $ResourceGroupName --name $AppServiceName --settings `
    AZURE_CLIENT_ID=$ClientId `
    AZURE_CLIENT_SECRET=$ClientSecret `
    AZURE_TENANT_ID=$TenantId `
    AZURE_KEY_VAULT_URL=$keyVaultUrl `
    FLASK_SECRET_KEY=$secretKey `
    LOGIC_APP_URL=$LogicAppUrl `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    WEBSITE_HTTPLOGGING_RETENTION_DAYS=3

Write-Host "✅ Variáveis de ambiente configuradas" -ForegroundColor Green

# 8. Configurar Application Insights
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

# 9. Deploy do código
Write-Host "📦 Preparando deploy do código..." -ForegroundColor Yellow

# Criar arquivo ZIP
$zipPath = "app-deploy.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

$filesToInclude = @(
    "app.py",
    "wsgi.py",
    "config.py",
    "requirements.txt",
    "web.config",
    "templates/*"
)

# Usar 7-Zip se disponível, senão usar PowerShell
if (Get-Command "7z" -ErrorAction SilentlyContinue) {
    7z a $zipPath $filesToInclude
} else {
    Compress-Archive -Path $filesToInclude -DestinationPath $zipPath -Force
}

Write-Host "🚀 Fazendo deploy..." -ForegroundColor Yellow
az webapp deploy --resource-group $ResourceGroupName --name $AppServiceName --src-path $zipPath

# Limpar arquivo temporário
Remove-Item $zipPath

Write-Host "✅ Deploy concluído!" -ForegroundColor Green

# 10. Configurar HTTPS e domínio customizado
Write-Host "🔒 Configurando HTTPS..." -ForegroundColor Yellow
az webapp update --resource-group $ResourceGroupName --name $AppServiceName --https-only true

# 11. Restart do App Service
Write-Host "🔄 Reiniciando App Service..." -ForegroundColor Yellow
az webapp restart --resource-group $ResourceGroupName --name $AppServiceName

# 12. Mostrar informações finais
Write-Host "`n🎉 Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "📱 URL da aplicação: https://$AppServiceName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "🏥 Health Check: https://$AppServiceName.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host "📊 Application Insights: Portal Azure > $insightsName" -ForegroundColor Cyan
Write-Host "🔐 Key Vault: https://portal.azure.com/#@/resource/subscriptions/.../resourceGroups/$ResourceGroupName/providers/Microsoft.KeyVault/vaults/$KeyVaultName" -ForegroundColor Cyan

Write-Host "`n📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure o App Registration no Azure AD com a URL de redirect: https://$AppServiceName.azurewebsites.net/getAToken" -ForegroundColor White
Write-Host "2. Acesse a aplicação e teste o fluxo completo" -ForegroundColor White
Write-Host "3. Configure alertas no Application Insights" -ForegroundColor White
Write-Host "4. Configure backup automático se necessário" -ForegroundColor White

Write-Host "`n✨ Sistema de Liberação de Crédito está pronto para uso!" -ForegroundColor Green
