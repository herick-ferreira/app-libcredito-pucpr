# 🔧 CONFIGURAÇÃO COMPLETA DO GITHUB ACTIONS PARA AZURE

## 📋 PASSO A PASSO PARA CONFIGURAR CI/CD

### **ETAPA 1: Obter o Publish Profile do Azure**

1. **Acesse o Portal Azure:** https://portal.azure.com
2. **Vá para seu App Service:** `app-libcredito-pucpr`
3. **Menu lateral > Deployment > Deployment Center**
4. **Clique em "Manage publish profile"**
5. **Clique em "Download publish profile"**
6. **Salve o arquivo `.PublishSettings`**

### **ETAPA 2: Configurar Secrets no GitHub**

1. **Vá para seu repositório GitHub**
2. **Settings > Secrets and variables > Actions**
3. **New repository secret**
4. **Adicione o secret:**
   ```
   Name: AZURE_WEBAPP_PUBLISH_PROFILE
   Value: [Cole todo o conteúdo do arquivo .PublishSettings]
   ```

### **ETAPA 3: Configurar Variáveis de Ambiente no Azure**

No Portal Azure, vá para seu App Service > Configuration > Application settings:

```bash
# Banco de Dados
AZURE_SQL_SERVER=server-db-libcredito.database.windows.net
AZURE_SQL_DATABASE=db-libcredito
AZURE_SQL_USERNAME=deniseambrosio
AZURE_SQL_PASSWORD=[sua senha do banco]

# Logic App
LOGIC_APP_URL=[sua URL completa do Logic App]

# Flask
FLASK_SECRET_KEY=super-secret-key-production-2025

# Runtime
PORT=8000
WEBSITES_PORT=8000
SCM_DO_BUILD_DURING_DEPLOYMENT=1
```

### **ETAPA 4: Verificar Estrutura de Arquivos**

Certifique-se de que estes arquivos estão no repositório:

```
📁 projeto/
├── 📄 app.py                    ✅ Aplicação principal
├── 📄 requirements.txt          ✅ Dependências
├── 📄 wsgi.py                   ✅ Entry point
├── 📄 web.config               ✅ Configuração IIS
├── 📁 static/                   ✅ CSS, JS, imagens
├── 📁 templates/                ✅ Templates HTML
├── 📁 .github/workflows/
│   └── 📄 azure.yml            ✅ CI/CD configurado
└── 📄 README.md
```

### **ETAPA 5: Testar o Deploy**

1. **Commit e push para branch main:**
   ```bash
   git add .
   git commit -m "feat: configurar CI/CD para Azure"
   git push origin main
   ```

2. **Verificar execução:**
   - GitHub > Actions
   - Verificar se o workflow executou com sucesso

3. **Testar aplicação:**
   ```
   https://app-libcredito-pucpr.azurewebsites.net/health
   ```

---

## 🔧 **ARQUIVO AZURE.YML CONFIGURADO**

O arquivo já foi corrigido com:

✅ **Python 3.11** (compatível com Azure App Service)  
✅ **Build separado do Deploy** (melhor prática)  
✅ **Upload de artefatos** (evita rebuild)  
✅ **Environment de produção**  
✅ **Exclusão de arquivos desnecessários**  
✅ **Trigger manual** (workflow_dispatch)  

---

## 🚨 **TROUBLESHOOTING**

### **Erro: "Publish profile secret not found"**
- Verifique se o secret `AZURE_WEBAPP_PUBLISH_PROFILE` foi criado corretamente
- Cole todo o conteúdo XML do arquivo .PublishSettings

### **Erro: "Application startup failed"**
- Verifique as variáveis de ambiente no Azure
- Verifique os logs: App Service > Log stream

### **Erro: "Database connection failed"**
- Verifique a string de conexão
- Adicione IP do Azure no firewall do SQL Database

### **Erro: "Logic App not receiving data"**
- Verifique a URL do Logic App
- Teste manualmente o endpoint

---

## 📊 **MONITORAMENTO**

### **Logs do GitHub Actions:**
```
GitHub > Repositório > Actions > Workflow run
```

### **Logs do Azure App Service:**
```bash
# Via Azure CLI
az webapp log tail --name app-libcredito-pucpr --resource-group rg-libcredito

# Via Portal
App Service > Monitoring > Log stream
```

### **Health Check:**
```
https://app-libcredito-pucpr.azurewebsites.net/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-26T...",
  "version": "1.0.0",
  "database": "ok"
}
```

---

## 🎯 **PRÓXIMOS PASSOS**

1. ✅ **Configure o publish profile** (ETAPA 1-2)
2. ✅ **Configure as variáveis no Azure** (ETAPA 3)  
3. ✅ **Faça commit do código** (ETAPA 5)
4. ✅ **Teste a aplicação**
5. 🔄 **Configure domínio customizado** (opcional)
6. 🔄 **Configure Application Insights** (monitoramento)

---

## 📞 **COMANDOS ÚTEIS**

### **Forçar novo deploy:**
```bash
git commit --allow-empty -m "trigger deploy"
git push origin main
```

### **Verificar status do App Service:**
```bash
az webapp show --name app-libcredito-pucpr --resource-group rg-libcredito --query "state"
```

### **Restart da aplicação:**
```bash
az webapp restart --name app-libcredito-pucpr --resource-group rg-libcredito
```

**🚀 Deploy automatizado configurado com sucesso!**
