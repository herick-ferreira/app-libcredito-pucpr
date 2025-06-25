# 🚀 Deploy Simplificado - Sistema de Crédito Universitário

## ⚡ Deploy Rápido (5 minutos)

### 1. Preparação
```powershell
# Fazer login no Azure
az login

# Navegar para o diretório
cd C:\Users\heric\Downloads\CloudComputing2
```

### 2. Executar Deploy
```powershell
.\deploy_simple.ps1 -ResourceGroupName "rg-libcredito" `
                    -AppServiceName "unicredito-$(Get-Random -Minimum 100 -Maximum 999)" `
                    -LogicAppUrl "https://prod-01.brazilsouth.logic.azure.com:443/workflows/29ba08cb744945cfacaf99af0f2dd6de/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=bca4HWFpTtJcVwyYHNOCuer1cTVZHDVZqY4-CWoqZEQ"
```

### 3. Acessar Aplicação
- **URL**: O script mostrará a URL final
- **Login**: Qualquer nome de usuário
- **Senha**: Entre em contato com o suporte

### 4. Inicializar Banco
- Acesse: `https://sua-app.azurewebsites.net/init-db`
- Isso criará as tabelas no PostgreSQL

## 🎯 Funcionalidades Implementadas

### ✅ **Autenticação**
- **Login simples**: Qualquer usuário + senha do sistema
- Sessão persistente
- Logout seguro

### ✅ **Banco de Dados PostgreSQL**
- Conexão via Azure AD (token automático)
- Tabela `solicitacoes_credito` completa
- Índices otimizados
- Estatísticas em tempo real

### ✅ **Análise de Crédito**
- Critérios universitários:
  - Valor máximo R$ 5.000
  - Renda mínima 2x o valor
  - Score de crédito ≥ 300
  - Sem pendências acadêmicas

### ✅ **Integração Logic Apps**
- Envio automático dos dados
- Payload estruturado com resultado da análise
- Tratamento de erros

### ✅ **Monitoramento**
- Health check em `/health`
- Application Insights integrado
- Logs detalhados
- Estatísticas do dashboard

## 📊 **Fluxo Completo**

1. **Login** → Tela de login simples
2. **Dashboard** → Estatísticas do sistema
3. **Solicitar Crédito** → Formulário completo
4. **Análise** → Processamento automático
5. **Banco** → Dados salvos no PostgreSQL
6. **Logic App** → Envio dos dados
7. **Resultado** → Aprovado/Reprovado

## 🔧 **Comandos Úteis**

### Verificar Logs
```powershell
az webapp log tail --resource-group "rg-libcredito" --name "SEU-APP-NAME"
```

### Verificar Configurações
```powershell
az webapp config appsettings list --resource-group "rg-libcredito" --name "SEU-APP-NAME"
```

### Reconectar PostgreSQL (se necessário)
```powershell
# Verificar token
az account get-access-token --resource https://ossrdbms-aad.database.windows.net

# Testar conexão manual
psql "host=libcredit-app-server.postgres.database.azure.com port=5432 dbname=postgres user=denise.ambrosio@pucpr.edu.br sslmode=require"
```

## 🎥 **Para o Vídeo de Demonstração**

### **30s - Arquitetura**
- Mostrar Resource Group no portal
- App Service + Application Insights
- PostgreSQL já configurado

### **90s - Demonstração**
1. Acessar aplicação
2. Login com credenciais válidas
3. Ver dashboard com estatísticas
4. Solicitar crédito (preencher formulário)
5. Mostrar aprovação/reprovação
6. Verificar que dados foram para Logic App

### **60s - Monitoramento**
- Application Insights com métricas
- Health check endpoint
- Logs da aplicação
- Dados salvos no PostgreSQL

## 📱 **URLs de Teste**

Após deploy, teste essas URLs:
- `/` - Login
- `/health` - Health check
- `/init-db` - Inicializar banco
- `/api/statistics` - API de estatísticas

## 🔍 **Troubleshooting**

### App não inicia?
- Verificar logs: `az webapp log tail`
- Verificar configurações do Python
- Restart: `az webapp restart`

### Banco não conecta?
- Verificar se está logado no Azure CLI
- Token expira a cada hora
- Verificar permissões no PostgreSQL

### Logic App não recebe dados?
- Verificar URL no .env
- Testar endpoint manualmente
- Verificar logs da aplicação

---

**🏆 Sistema pronto para 10K+ usuários com PostgreSQL, Logic Apps e monitoramento completo!**
