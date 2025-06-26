# 🚀 GUIA COMPLETO DE DEPLOY PARA AZURE APP SERVICE

## 📋 PRÉ-REQUISITOS

### 1. **Recursos Azure Necessários**
- ✅ **Azure SQL Database** (já configurado)
- ✅ **Logic App** (já configurado) 
- 🔄 **Azure App Service** (vamos criar)

### 2. **Ferramentas Necessárias**
- **Azure CLI** ou **Portal Azure**
- **Git** (para deploy via repositório)
- **Visual Studio Code** (recomendado)

---

## 🏗️ MÉTODO 1: DEPLOY VIA PORTAL AZURE (RECOMENDADO)

### **PASSO 1: Criar o App Service**

1. **Acesse o Portal Azure:** https://portal.azure.com
2. **Clique em "Criar um recurso"**
3. **Busque por "Web App"** e selecione
4. **Configure:**
   ```
   Resource Group: (use o mesmo do Azure SQL)
   Name: app-libcredito-pucpr
   Runtime Stack: Python 3.11
   Operating System: Linux
   Region: Brazil South (mesma do SQL Database)
   Pricing Tier: Basic B1 (ou Free F1 para testes)
   ```

### **PASSO 2: Configurar Variáveis de Ambiente**

1. **Vá para o App Service criado**
2. **Menu lateral > Settings > Configuration**
3. **Application Settings > New application setting**
4. **Adicione TODAS as variáveis:**

```bash
# Banco de Dados
AZURE_SQL_SERVER=server-db-libcredito.database.windows.net
AZURE_SQL_DATABASE=db-libcredito
AZURE_SQL_USERNAME=deniseambrosio
AZURE_SQL_PASSWORD=[sua senha do banco]

# Logic App
LOGIC_APP_URL=https://prod-01.brazilsouth.logic.azure.com:443/workflows/29ba08cb744945cfacaf99af0f2dd6de/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=bca4HWFpTtJcVwyYHNOCuer1cTVZHDVZqY4-CWoqZEQ

# Flask
FLASK_SECRET_KEY=super-secret-key-production-2025

# Runtime
PORT=8000
WEBSITES_PORT=8000
```

5. **Clique em "Save"**

### **PASSO 3: Configurar Deploy**

#### **Opção A: Deploy via GitHub (Recomendado)**

1. **No App Service > Deployment Center**
2. **Source: GitHub**
3. **Conecte sua conta GitHub**
4. **Selecione o repositório e branch**
5. **Build Provider: App Service Build Service**

#### **Opção B: Deploy via ZIP**

1. **Compacte apenas os arquivos essenciais:**
   ```
   app.py
   requirements.txt
   wsgi.py
   web.config
   static/
   templates/
   ```

2. **No App Service > Deployment Center**
3. **ZIP Deploy > Browse > Upload o ZIP**

---

## 🏗️ MÉTODO 2: DEPLOY VIA AZURE CLI

### **PASSO 1: Instalar Azure CLI**
```powershell
# Windows (PowerShell como Admin)
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

### **PASSO 2: Login e Deploy**
```bash
# Login no Azure
az login

# Criar Resource Group (se não existir)
az group create --name rg-libcredito --location brazilsouth

# Criar App Service Plan
az appservice plan create --name plan-libcredito --resource-group rg-libcredito --sku B1 --is-linux

# Criar Web App
az webapp create --resource-group rg-libcredito --plan plan-libcredito --name app-libcredito-pucpr --runtime "PYTHON|3.11"

# Configurar variáveis de ambiente
az webapp config appsettings set --resource-group rg-libcredito --name app-libcredito-pucpr --settings \
  AZURE_SQL_SERVER="server-db-libcredito.database.windows.net" \
  AZURE_SQL_DATABASE="db-libcredito" \
  AZURE_SQL_USERNAME="deniseambrosio" \
  AZURE_SQL_PASSWORD="[sua senha]" \
  LOGIC_APP_URL="[sua URL do Logic App]" \
  FLASK_SECRET_KEY="super-secret-key-production-2025"

# Deploy via ZIP
az webapp deployment source config-zip --resource-group rg-libcredito --name app-libcredito-pucpr --src deploy.zip
```

---

## 📁 ARQUIVOS NECESSÁRIOS PARA DEPLOY

### **1. requirements.txt** (já existe)
```python
Flask==2.3.3
python-dotenv==1.0.0
requests==2.31.0
SQLAlchemy==2.0.21
pymssql==2.2.8
```

### **2. wsgi.py** (já existe)
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### **3. web.config** (já existe)
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="D:\home\Python\python.exe"
                  arguments="D:\home\site\wwwroot\wsgi.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
    </httpPlatform>
  </system.webServer>
</configuration>
```

---

## ✅ CHECKLIST PRÉ-DEPLOY

### **Verificar Arquivos Essenciais:**
- ✅ `app.py` (aplicação principal)
- ✅ `requirements.txt` (dependências)
- ✅ `wsgi.py` (entry point)
- ✅ `web.config` (configuração IIS)
- ✅ `static/` (CSS, JS, imagens)
- ✅ `templates/` (HTML templates)
- ✅ `.env` (apenas para desenvolvimento local)

### **Verificar Configurações:**
- ✅ Variáveis de ambiente configuradas no Azure
- ✅ Azure SQL Database acessível
- ✅ Logic App URL válida
- ✅ Porta configurada (8000)

---

## 🧪 TESTANDO O DEPLOY

### **1. Verificar Health Check**
```
https://app-libcredito-pucpr.azurewebsites.net/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-26T...",
  "version": "1.0.0",
  "database": "ok"
}
```

### **2. Testar Aplicação**
```
https://app-libcredito-pucpr.azurewebsites.net/
```

### **3. Verificar Logs**
```bash
# Via Azure CLI
az webapp log tail --name app-libcredito-pucpr --resource-group rg-libcredito

# Via Portal Azure
App Service > Monitoring > Log stream
```

---

## 🔧 CONFIGURAÇÕES AVANÇADAS

### **1. Custom Domain (Opcional)**
```bash
# Adicionar domínio customizado
az webapp config hostname add --webapp-name app-libcredito-pucpr --resource-group rg-libcredito --hostname libcredito.pucpr.edu.br
```

### **2. SSL Certificate**
```bash
# Habilitar HTTPS apenas
az webapp update --name app-libcredito-pucpr --resource-group rg-libcredito --https-only true
```

### **3. Auto-scaling (Opcional)**
```bash
# Configurar auto-scaling
az monitor autoscale create --resource-group rg-libcredito --resource app-libcredito-pucpr --resource-type Microsoft.Web/serverfarms --name autoscale-libcredito --min-count 1 --max-count 3 --count 1
```

---

## 🚨 TROUBLESHOOTING

### **Erro: "Application Error"**
1. **Verificar logs:** App Service > Log stream
2. **Verificar variáveis de ambiente**
3. **Verificar requirements.txt**

### **Erro: "Database Connection Failed"**
1. **Verificar connection string no Azure SQL**
2. **Verificar firewall do Azure SQL**
3. **Adicionar IP do App Service no firewall**

### **Erro: "Logic App não recebe dados"**
1. **Verificar URL do Logic App**
2. **Testar Logic App manualmente**
3. **Verificar logs da aplicação**

---

## 📋 COMANDOS ÚTEIS

### **Restart da Aplicação**
```bash
az webapp restart --name app-libcredito-pucpr --resource-group rg-libcredito
```

### **Ver Configurações**
```bash
az webapp config appsettings list --name app-libcredito-pucpr --resource-group rg-libcredito
```

### **Backup**
```bash
az webapp config backup create --resource-group rg-libcredito --webapp-name app-libcredito-pucpr --backup-name backup-$(date +%Y%m%d) --storage-account-url "[storage-url]"
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Deploy inicial** ✅
2. **Teste completo** ✅  
3. **Configurar domínio customizado** (opcional)
4. **Configurar monitoramento** (Application Insights)
5. **Backup automático** 
6. **Documentação de usuário**

---

## 📞 SUPORTE

- **Azure Documentation:** https://docs.microsoft.com/azure/app-service/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Azure SQL Documentation:** https://docs.microsoft.com/azure/sql-database/

**🚀 Aplicação pronta para produção!**
