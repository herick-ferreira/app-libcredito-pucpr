# Sistema de Liberação de Crédito Universitário

Uma aplicação Flask para processamento de solicitações de crédito educacional, integrada com Azure AD para autenticação e Azure Logic Apps para workflow automatizado.

## 🏗️ Arquitetura

### Componentes Principais
- **Frontend**: Flask com Bootstrap 5 (responsivo e moderno)
- **Autenticação**: Azure Active Directory (MSAL)
- **Segurança**: Azure Key Vault para armazenamento de segredos
- **Workflow**: Azure Logic Apps para processamento
- **Hosting**: Azure App Service
- **Monitoramento**: Application Insights

### Fluxo de Operação
1. **Autenticação**: Login via Microsoft Azure AD
2. **Solicitação**: Preenchimento do formulário de crédito
3. **Análise**: Processamento automático baseado em critérios
4. **Integração**: Envio para Logic App e Sistema X
5. **Notificação**: E-mail automático ao cliente

## 🎯 Critérios de Aprovação

- ✅ Valor solicitado ≤ R$ 5.000
- ✅ Renda mínima = 2x o valor solicitado
- ✅ Score de crédito ≥ 300
- ✅ Sem pendências acadêmicas

## 🚀 Instalação Local

### Pré-requisitos
- Python 3.8+
- Azure CLI
- Git

### Configuração
```bash
# Clone o repositório
git clone <repository-url>
cd CloudComputing2

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações Azure
```

### Variáveis de Ambiente
```
AZURE_CLIENT_ID=seu-client-id
AZURE_CLIENT_SECRET=seu-client-secret
AZURE_TENANT_ID=seu-tenant-id
AZURE_KEY_VAULT_URL=https://seu-keyvault.vault.azure.net/
FLASK_SECRET_KEY=sua-chave-secreta
LOGIC_APP_URL=sua-url-logic-app
```

### Executar Localmente
```bash
python app.py
```

## ☁️ Deploy no Azure

### 1. Criar App Registration
```bash
# Criar app registration
az ad app create --display-name "UniCredito-App" \
  --available-to-other-tenants false \
  --homepage "https://seu-app.azurewebsites.net" \
  --reply-urls "https://seu-app.azurewebsites.net/getAToken"
```

### 2. Criar Key Vault
```bash
# Criar Key Vault
az keyvault create --name "keyvault-unicredito" \
  --resource-group "rg-libcredito" \
  --location "Brazil South"

# Adicionar segredos
az keyvault secret set --vault-name "keyvault-unicredito" \
  --name "flask-secret-key" --value "sua-chave-super-secreta"
```

### 3. Criar App Service
```bash
# Criar App Service Plan
az appservice plan create --name "plan-unicredito" \
  --resource-group "rg-libcredito" \
  --sku F1 --is-linux

# Criar Web App
az webapp create --name "unicredito-app" \
  --resource-group "rg-libcredito" \
  --plan "plan-unicredito" \
  --runtime "PYTHON|3.9"
```

### 4. Configurar Variáveis de Ambiente
```bash
# Configurar App Settings
az webapp config appsettings set --resource-group "rg-libcredito" \
  --name "unicredito-app" \
  --settings \
    AZURE_CLIENT_ID="seu-client-id" \
    AZURE_CLIENT_SECRET="seu-client-secret" \
    AZURE_TENANT_ID="seu-tenant-id" \
    AZURE_KEY_VAULT_URL="https://keyvault-unicredito.vault.azure.net/" \
    FLASK_SECRET_KEY="sua-chave-secreta" \
    LOGIC_APP_URL="sua-url-logic-app"
```

### 5. Deploy do Código
```bash
# Deploy via ZIP
zip -r app.zip . -x "*.git*" "__pycache__/*" "*.pyc"
az webapp deploy --resource-group "rg-libcredito" \
  --name "unicredito-app" \
  --src-path "app.zip"
```

### 6. Habilitar Managed Identity
```bash
# Habilitar System Managed Identity
az webapp identity assign --resource-group "rg-libcredito" \
  --name "unicredito-app"

# Dar permissão ao Key Vault
az keyvault set-policy --name "keyvault-unicredito" \
  --object-id "managed-identity-object-id" \
  --secret-permissions get
```

## 🔧 Configuração Azure AD

### App Registration
1. Acesse Azure Portal → Azure Active Directory
2. App registrations → New registration
3. Configure:
   - Name: `UniCredito-App`
   - Redirect URI: `https://seu-app.azurewebsites.net/getAToken`
4. Certificates & secrets → New client secret
5. API permissions → Microsoft Graph → User.Read

## 📊 Monitoramento

### Application Insights
```bash
# Habilitar Application Insights
az monitor app-insights component create \
  --app "unicredito-insights" \
  --location "Brazil South" \
  --resource-group "rg-libcredito"

# Configurar no App Service
az webapp config appsettings set \
  --resource-group "rg-libcredito" \
  --name "unicredito-app" \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="sua-instrumentation-key"
```

### Health Check
- Endpoint: `https://seu-app.azurewebsites.net/health`
- Retorna status da aplicação em JSON

## 🔒 Segurança

### Recursos Implementados
- ✅ Autenticação Azure AD (MSAL)
- ✅ HTTPS obrigatório
- ✅ Secrets no Key Vault
- ✅ Managed Identity
- ✅ CSRF Protection
- ✅ Input Validation
- ✅ Error Handling

### Network Security Groups
```bash
# Criar NSG
az network nsg create --resource-group "rg-libcredito" \
  --name "nsg-unicredito"

# Regra HTTPS
az network nsg rule create --resource-group "rg-libcredito" \
  --nsg-name "nsg-unicredito" --name "AllowHTTPS" \
  --protocol tcp --direction inbound --priority 1000 \
  --source-address-prefix Internet --source-port-range '*' \
  --destination-address-prefix '*' --destination-port-range 443 \
  --access allow
```

## 📈 Escalabilidade

### Auto-scaling
```bash
# Configurar auto-scale
az monitor autoscale create \
  --resource-group "rg-libcredito" \
  --resource "/subscriptions/SUB-ID/resourceGroups/rg-libcredito/providers/Microsoft.Web/serverfarms/plan-unicredito" \
  --name "autoscale-unicredito" \
  --min-count 1 --max-count 10 --count 2

# Regra de scale-out
az monitor autoscale rule create \
  --resource-group "rg-libcredito" \
  --autoscale-name "autoscale-unicredito" \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

## 🔄 Backup e Restore

### Backup Automático
```bash
# Habilitar backup
az webapp config backup update \
  --resource-group "rg-libcredito" \
  --webapp-name "unicredito-app" \
  --enabled true \
  --frequency 1440 \
  --retain-one true \
  --retention-period-in-days 30
```

## 📞 URLs de Acesso

### Produção
- **Aplicação**: `https://unicredito-app.azurewebsites.net`
- **Health Check**: `https://unicredito-app.azurewebsites.net/health`
- **Logic App**: Já configurado no código

### Desenvolvimento
- **Local**: `http://localhost:5000`

## 🎥 Vídeo de Demonstração

Para criar o vídeo de 3 minutos solicitado, inclua:

1. **Overview da Arquitetura** (30s)
   - Mostrar Resource Group no Azure Portal
   - Visão geral dos recursos criados

2. **Demonstração da Aplicação** (90s)
   - Login com Azure AD
   - Fluxo de solicitação de crédito
   - Aprovação/Reprovação
   - Integração com Logic App

3. **Monitoramento e Backup** (60s)
   - Application Insights Dashboard
   - Logs e métricas
   - Configurações de backup e auto-scale

## 📞 Suporte

Para dúvidas ou suporte:
- Email: suporte@unicredito.com
- Portal: Azure Portal → Support

---

**Desenvolvido para Azure Cloud Computing**  
*Arquitetura escalável, segura e resiliente para 10K+ usuários*
