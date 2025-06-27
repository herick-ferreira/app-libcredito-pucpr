# Docker Deployment Guide for Azure

Este guia explica como fazer deploy da aplicação Flask no Azure usando Docker.

## Arquivos Criados

- `Dockerfile`: Configuração para build da imagem Docker
- `docker-compose.yml`: Para desenvolvimento local
- `docker-compose.azure.yml`: Para deploy no Azure
- `.dockerignore`: Exclui arquivos desnecessários do build

## Opções de Deploy no Azure

### 1. Azure Container Instances (ACI)
Mais simples e adequado para aplicações pequenas:

```bash
# Login no Azure
az login

# Criar resource group
az group create --name rg-libcredito --location eastus

# Deploy usando docker-compose
az container create \
  --resource-group rg-libcredito \
  --name app-libcredito \
  --image <your-registry>/app-libcredito:latest \
  --dns-name-label app-libcredito-pucpr \
  --ports 80 \
  --environment-variables FLASK_ENV=production PORT=8000
```

### 2. Azure Container Apps
Mais recursos e escalabilidade:

```bash
# Instalar extensão
az extension add --name containerapp

# Criar ambiente
az containerapp env create \
  --name libcredito-env \
  --resource-group rg-libcredito \
  --location eastus

# Deploy da aplicação
az containerapp create \
  --name app-libcredito \
  --resource-group rg-libcredito \
  --environment libcredito-env \
  --image <your-registry>/app-libcredito:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars FLASK_ENV=production PORT=8000
```

### 3. Azure App Service (Web App for Containers)
Para aplicações que precisam de mais controle:

```bash
# Criar App Service Plan
az appservice plan create \
  --name libcredito-plan \
  --resource-group rg-libcredito \
  --sku B1 \
  --is-linux

# Criar Web App
az webapp create \
  --resource-group rg-libcredito \
  --plan libcredito-plan \
  --name app-libcredito-pucpr \
  --deployment-container-image-name <your-registry>/app-libcredito:latest

# Configurar porta
az webapp config appsettings set \
  --resource-group rg-libcredito \
  --name app-libcredito-pucpr \
  --settings WEBSITES_PORT=8000 FLASK_ENV=production
```

## Build e Push da Imagem

### Usando Azure Container Registry

```bash
# Criar registry
az acr create \
  --resource-group rg-libcredito \
  --name libcreditoacr \
  --sku Basic

# Login no registry
az acr login --name libcreditoacr

# Build e push
docker build -t libcreditoacr.azurecr.io/app-libcredito:latest .
docker push libcreditoacr.azurecr.io/app-libcredito:latest
```

### Usando Docker Hub

```bash
# Build da imagem
docker build -t seu-usuario/app-libcredito:latest .

# Push para Docker Hub
docker push seu-usuario/app-libcredito:latest
```

## Testes Locais

```bash
# Build e run local
docker-compose up --build

# Ou apenas build
docker build -t app-libcredito .
docker run -p 8000:8000 app-libcredito

# Testar
curl http://localhost:8000
```

## Configurações de Produção

### Variáveis de Ambiente Recomendadas
- `FLASK_ENV=production`
- `PORT=8000`
- `PYTHONUNBUFFERED=1`

### Recursos Mínimos Recomendados
- CPU: 0.5 vCPU
- Memória: 512MB
- Para maior tráfego: 1 vCPU, 1GB RAM

## Monitoramento e Logs

```bash
# Ver logs do container
az container logs --resource-group rg-libcredito --name app-libcredito

# Para Container Apps
az containerapp logs show --name app-libcredito --resource-group rg-libcredito

# Para Web Apps
az webapp log tail --name app-libcredito-pucpr --resource-group rg-libcredito
```

## Segurança

- Container roda com usuário não-root
- Health checks configurados
- Portas mínimas expostas
- Variáveis de ambiente para configuração sensível

## Troubleshooting

### Container não inicia
1. Verificar logs: `docker logs <container-id>`
2. Testar localmente primeiro
3. Verificar se porta 8000 está correta

### Aplicação não responde
1. Verificar health check
2. Confirmar que gunicorn está rodando na porta correta
3. Verificar se todos os arquivos foram copiados

### Problemas de permissão
- Container usa usuário não-root
- Verificar se arquivos têm permissões corretas
