# Azure Deployment Script for SEO-GEO-AEO API (PowerShell)
# This script deploys the application to Azure using ARM templates

$ErrorActionPreference = "Stop"

# Configuration
$RESOURCE_GROUP = "rg-seo-geo-aeo"
$LOCATION = "eastus"
$APP_SERVICE_NAME = "seo-geo-aeo-api"
$APP_SERVICE_PLAN = "asp-seo-geo-aeo"
$CONTAINER_REGISTRY = "YOUR_REGISTRY.azurecr.io"
$IMAGE_NAME = "seo-geo-aeo-api:latest"

Write-Host "🚀 Starting Azure Deployment..." -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Login to Azure (if not already logged in)
Write-Host "Checking Azure login status..."
try {
    az account show | Out-Null
} catch {
    Write-Host "Logging in to Azure..."
    az login
}

# Create Resource Group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION

# Deploy ARM Template
Write-Host "Deploying resources using ARM template..." -ForegroundColor Yellow
az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file azure-deployment.json `
  --parameters `
    appServiceName=$APP_SERVICE_NAME `
    appServicePlanName=$APP_SERVICE_PLAN `
    containerRegistry=$CONTAINER_REGISTRY `
    imageName=$IMAGE_NAME `
    sku=B2

# Get Container Registry credentials (if using ACR)
Write-Host "Retrieving container registry credentials..." -ForegroundColor Yellow
$ACR_NAME = $CONTAINER_REGISTRY.Split('.')[0]
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv

# Update App Service with container settings
Write-Host "Configuring App Service..." -ForegroundColor Yellow
az webapp config container set `
  --name $APP_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --docker-custom-image-name "$CONTAINER_REGISTRY/$IMAGE_NAME" `
  --docker-registry-server-url "https://$CONTAINER_REGISTRY" `
  --docker-registry-server-user "$ACR_USERNAME" `
  --docker-registry-server-password "$ACR_PASSWORD"

# Configure App Settings
Write-Host "Setting environment variables..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $APP_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings `
    WEBSITES_PORT=8001 `
    WEBSITE_HTTPSCALEV2_ENABLED=1

# Restart the app
Write-Host "Restarting App Service..." -ForegroundColor Yellow
az webapp restart `
  --name $APP_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP

# Get the URL
$APP_URL = az webapp show `
  --name $APP_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query defaultHostName -o tsv

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your application is available at: https://$APP_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 To view logs:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
Write-Host ""
