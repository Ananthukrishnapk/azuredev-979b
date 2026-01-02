#!/bin/bash

# Azure Deployment Script for SEO-GEO-AEO API
# This script deploys the application to Azure using ARM templates

set -e

# Configuration
RESOURCE_GROUP="rg-seo-geo-aeo"
LOCATION="eastus"
APP_SERVICE_NAME="seo-geo-aeo-api"
APP_SERVICE_PLAN="asp-seo-geo-aeo"
CONTAINER_REGISTRY="YOUR_REGISTRY.azurecr.io"
IMAGE_NAME="seo-geo-aeo-api:latest"

echo "🚀 Starting Azure Deployment..."

# Login to Azure (if not already logged in)
echo "Checking Azure login status..."
az account show &> /dev/null || az login

# Create Resource Group
echo "Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Deploy ARM Template
echo "Deploying resources using ARM template..."
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file azure-deployment.json \
  --parameters \
    appServiceName=$APP_SERVICE_NAME \
    appServicePlanName=$APP_SERVICE_PLAN \
    containerRegistry=$CONTAINER_REGISTRY \
    imageName=$IMAGE_NAME \
    sku=B2

# Get Container Registry credentials (if using ACR)
echo "Retrieving container registry credentials..."
ACR_NAME=$(echo $CONTAINER_REGISTRY | cut -d'.' -f1)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Update App Service with container settings
echo "Configuring App Service..."
az webapp config container set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name "$CONTAINER_REGISTRY/$IMAGE_NAME" \
  --docker-registry-server-url "https://$CONTAINER_REGISTRY" \
  --docker-registry-server-user "$ACR_USERNAME" \
  --docker-registry-server-password "$ACR_PASSWORD"

# Configure App Settings (add your environment variables here)
echo "Setting environment variables..."
az webapp config appsettings set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    WEBSITES_PORT=8001 \
    WEBSITE_HTTPSCALEV2_ENABLED=1

# Restart the app
echo "Restarting App Service..."
az webapp restart \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP

# Get the URL
APP_URL=$(az webapp show \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostName -o tsv)

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your application is available at: https://$APP_URL"
echo ""
echo "📊 To view logs:"
echo "   az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP"
echo ""
