# 🚀 Guia de Deploy - Sistema de Liberação de Crédito Universitário

## 📋 Pré-requisitos

### Ferramentas Necessárias
- Azure CLI instalado e configurado
- PowerShell (Windows) ou Bash (Linux/Mac)
- Git
- Python 3.8+ (para testes locais)

### Contas e Permissões
- Conta Azure com privilégios de Contributor
- Azure for Students ou assinatura paga
- Acesso ao Azure Active Directory

## 🔧 Passo a Passo do Deploy

### 1. Preparação Inicial

```powershell
# Fazer login no Azure
az login

# Definir a assinatura (se necessário)
az account set --subscription "sua-subscription-id"

# Verificar se está logado
az account show
```

### 2. Criar App Registration no Azure AD

```powershell
# Via Portal Azure (Recomendado):
# 1. Acesse: https://portal.azure.com
# 2. Azure Active Directory > App registrations > New registration
# 3. Nome: "UniCredito-App"
# 4. Redirect URI: https://SEU-APP-NAME.azurewebsites.net/getAToken
# 5. Copie o Application (client) ID e Directory (tenant) ID
# 6. Certificates & secrets > New client secret > Copie o valor
```

### 3. Executar Script de Deploy

```powershell
# Navegue até o diretório do projeto
cd C:\Users\heric\Downloads\CloudComputing2

# Execute o script de deploy
.\deploy.ps1 -ResourceGroupName "rg-libcredito" `
            -AppServiceName "unicredito-app-SEU-NOME" `
            -KeyVaultName "kv-unicredito-SEU-NOME" `
            -ClientId "SEU-CLIENT-ID" `
            -ClientSecret "SEU-CLIENT-SECRET" `
            -TenantId "SEU-TENANT-ID" `
            -LogicAppUrl "https://prod-01.brazilsouth.logic.azure.com:443/workflows/29ba08cb744945cfacaf99af0f2dd6de/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=bca4HWFpTtJcVwyYHNOCuer1cTVZHDVZqY4-CWoqZEQ"
```

### 4. Configurar Redirect URI

Após o deploy, atualize o App Registration:
1. Azure Portal > Azure AD > App registrations > UniCredito-App
2. Authentication > Redirect URIs
3. Adicione: `https://SEU-APP-NAME.azurewebsites.net/getAToken`

### 5. Testar a Aplicação

```powershell
# Acesse no navegador
start https://SEU-APP-NAME.azurewebsites.net

# Verificar health check
start https://SEU-APP-NAME.azurewebsites.net/health
```

## 🔐 Configuração de Segurança

### Network Security Group (NSG)
```powershell
# Criar NSG para maior segurança
az network nsg create --resource-group "rg-libcredito" --name "nsg-unicredito"

# Permitir apenas HTTPS
az network nsg rule create --resource-group "rg-libcredito" `
  --nsg-name "nsg-unicredito" --name "AllowHTTPS" `
  --protocol tcp --direction inbound --priority 1000 `
  --source-address-prefix Internet --source-port-range '*' `
  --destination-address-prefix '*' --destination-port-range 443 `
  --access allow
```

### SSL/TLS
```powershell
# Forçar HTTPS (já configurado no script)
az webapp update --resource-group "rg-libcredito" `
  --name "SEU-APP-NAME" --https-only true
```

## 📊 Configuração de Monitoramento

### Application Insights
```powershell
# Configurar alertas
az monitor metrics alert create `
  --name "High-CPU-Alert" `
  --resource-group "rg-libcredito" `
  --scopes "/subscriptions/SEU-SUB-ID/resourceGroups/rg-libcredito/providers/Microsoft.Web/sites/SEU-APP-NAME" `
  --condition "avg Percentage CPU > 80" `
  --description "Alert when CPU exceeds 80%"
```

### Log Analytics
```powershell
# Criar workspace do Log Analytics
az monitor log-analytics workspace create `
  --resource-group "rg-libcredito" `
  --workspace-name "log-unicredito"
```

## 📈 Configuração de Escalabilidade

### Auto-scaling
```powershell
# Configurar auto-scale
az monitor autoscale create `
  --resource-group "rg-libcredito" `
  --resource "/subscriptions/SEU-SUB-ID/resourceGroups/rg-libcredito/providers/Microsoft.Web/serverfarms/SEU-APP-NAME-plan" `
  --name "autoscale-unicredito" `
  --min-count 1 --max-count 10 --count 2

# Regra de scale-out (CPU > 70%)
az monitor autoscale rule create `
  --resource-group "rg-libcredito" `
  --autoscale-name "autoscale-unicredito" `
  --condition "Percentage CPU > 70 avg 5m" `
  --scale out 1

# Regra de scale-in (CPU < 30%)
az monitor autoscale rule create `
  --resource-group "rg-libcredito" `
  --autoscale-name "autoscale-unicredito" `
  --condition "Percentage CPU < 30 avg 10m" `
  --scale in 1
```

## 🔄 Backup e Restore

### Backup Automático
```powershell
# Criar conta de armazenamento para backup
az storage account create `
  --name "stunicreditobackup" `
  --resource-group "rg-libcredito" `
  --location "Brazil South" `
  --sku Standard_LRS

# Configurar backup
az webapp config backup update `
  --resource-group "rg-libcredito" `
  --webapp-name "SEU-APP-NAME" `
  --enabled true `
  --frequency 1440 `
  --retain-one true `
  --retention-period-in-days 30
```

## 🌐 Configuração de CDN (Opcional)

```powershell
# Criar perfil CDN
az cdn profile create `
  --resource-group "rg-libcredito" `
  --name "cdn-unicredito" `
  --sku Standard_Microsoft

# Criar endpoint CDN
az cdn endpoint create `
  --resource-group "rg-libcredito" `
  --profile-name "cdn-unicredito" `
  --name "unicredito-cdn" `
  --origin "SEU-APP-NAME.azurewebsites.net"
```

## 🚨 Configuração de Alertas

### Alertas de Disponibilidade
```powershell
# Alerta de disponibilidade
az monitor metrics alert create `
  --name "App-Availability-Alert" `
  --resource-group "rg-libcredito" `
  --scopes "/subscriptions/SEU-SUB-ID/resourceGroups/rg-libcredito/providers/Microsoft.Web/sites/SEU-APP-NAME" `
  --condition "avg Http2xx < 95" `
  --description "Alert when availability drops below 95%"
```

### Alertas de Performance
```powershell
# Alerta de tempo de resposta
az monitor metrics alert create `
  --name "Response-Time-Alert" `
  --resource-group "rg-libcredito" `
  --scopes "/subscriptions/SEU-SUB-ID/resourceGroups/rg-libcredito/providers/Microsoft.Web/sites/SEU-APP-NAME" `
  --condition "avg AverageResponseTime > 2000" `
  --description "Alert when response time exceeds 2 seconds"
```

## 🔍 Troubleshooting

### Logs da Aplicação
```powershell
# Ver logs em tempo real
az webapp log tail --resource-group "rg-libcredito" --name "SEU-APP-NAME"

# Download dos logs
az webapp log download --resource-group "rg-libcredito" --name "SEU-APP-NAME"
```

### Diagnóstico
```powershell
# Verificar configurações
az webapp config show --resource-group "rg-libcredito" --name "SEU-APP-NAME"

# Verificar app settings
az webapp config appsettings list --resource-group "rg-libcredito" --name "SEU-APP-NAME"
```

## 📱 URLs Importantes

Após o deploy, você terá acesso a:

- **Aplicação Principal**: `https://SEU-APP-NAME.azurewebsites.net`
- **Health Check**: `https://SEU-APP-NAME.azurewebsites.net/health`
- **Application Insights**: Portal Azure → SEU-APP-NAME-insights
- **Key Vault**: Portal Azure → kv-unicredito-SEU-NOME

## 🎯 Critérios de Sucesso

Verifique se:
- ✅ Aplicação carrega sem erros
- ✅ Login com Azure AD funciona
- ✅ Formulário de crédito submete corretamente
- ✅ Logic App recebe os dados
- ✅ Health check retorna status healthy
- ✅ Application Insights coleta telemetria

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Confirme as configurações do App Registration
3. Verifique as permissões do Key Vault
4. Teste o endpoint do Logic App

---

**🏆 Sistema pronto para atender 10K+ usuários com alta disponibilidade!**
