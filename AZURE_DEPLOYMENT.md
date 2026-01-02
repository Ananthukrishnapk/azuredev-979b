# Azure DevOps & Microsoft AI Foundry Deployment Guide

## Overview

This guide explains how to deploy the SEO-GEO-AEO API project to Azure using Azure DevOps pipelines and integrate it with Microsoft AI Foundry.

## Prerequisites

1. **Azure Subscription** - Active Azure subscription
2. **Azure DevOps Organization** - Create one at [dev.azure.com](https://dev.azure.com)
3. **Azure CLI** - Install from [docs.microsoft.com/cli/azure/install-azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli)
4. **Docker** - Install Docker Desktop for local testing
5. **Git** - For version control

## Project Structure

```
azuredev-979b/
├── azure-pipelines.yml          # Azure DevOps CI/CD pipeline
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Local development setup
├── azure-deployment.json        # ARM template for Azure resources
├── deploy-azure.sh             # Bash deployment script
├── deploy-azure.ps1            # PowerShell deployment script
├── .dockerignore               # Docker build exclusions
├── requirements.txt            # Python dependencies
├── run_model.py               # Azure AI Foundry integration
├── .env                       # Environment variables (not in git)
└── project/                   # Main application
    ├── main.py               # FastAPI application
    ├── requirements.txt      # Application dependencies
    └── ...
```

## Step 1: Set Up Azure Container Registry (ACR)

```bash
# Create ACR
az acr create \
  --resource-group rg-seo-geo-aeo \
  --name yourregistry \
  --sku Basic \
  --location eastus

# Enable admin access
az acr update --name yourregistry --admin-enabled true

# Get credentials
az acr credential show --name yourregistry
```

## Step 2: Build and Push Docker Image Locally (Optional)

```bash
# Build the image
docker build -t seo-geo-aeo-api:latest .

# Tag for ACR
docker tag seo-geo-aeo-api:latest yourregistry.azurecr.io/seo-geo-aeo-api:latest

# Login to ACR
az acr login --name yourregistry

# Push to ACR
docker push yourregistry.azurecr.io/seo-geo-aeo-api:latest
```

## Step 3: Test Locally with Docker Compose

```bash
# Create .env file with your variables
cp .env.example .env

# Start the application
docker-compose up -d

# Check logs
docker-compose logs -f

# Test the API
curl http://localhost:8001/api/health

# Stop the application
docker-compose down
```

## Step 4: Set Up Azure DevOps Pipeline

### 4.1 Create Azure DevOps Project

1. Go to [dev.azure.com](https://dev.azure.com)
2. Create a new project (e.g., "SEO-GEO-AEO-API")
3. Initialize a Git repository or import from GitHub

### 4.2 Create Service Connections

#### Azure Resource Manager Connection

1. Go to **Project Settings** → **Service connections**
2. Click **New service connection** → **Azure Resource Manager**
3. Select **Service principal (automatic)**
4. Choose your subscription and resource group
5. Name it (e.g., "Azure-Production")

#### Docker Registry Connection

1. Go to **Project Settings** → **Service connections**
2. Click **New service connection** → **Docker Registry**
3. Select **Azure Container Registry**
4. Choose your ACR
5. Name it (e.g., "ACR-Connection")

### 4.3 Configure Pipeline Variables

1. Go to **Pipelines** → **Library**
2. Create a new variable group: "Production-Config"
3. Add variables:
   - `azureSubscription`: Your service connection name
   - `containerRegistry`: Your ACR URL
   - `appServiceName`: Your app service name
   - `resourceGroupName`: Your resource group name

### 4.4 Create the Pipeline

1. Go to **Pipelines** → **Create Pipeline**
2. Select your repository
3. Choose **Existing Azure Pipelines YAML file**
4. Select `/azure-pipelines.yml`
5. Update the variables in the YAML:
   ```yaml
   variables:
     azureSubscription: "Azure-Production" # Your service connection name
     containerRegistry: "yourregistry.azurecr.io"
   ```
6. Save and run

## Step 5: Deploy Using ARM Template

### Using Azure CLI (Bash)

```bash
# Make script executable
chmod +x deploy-azure.sh

# Update the script with your values
nano deploy-azure.sh

# Run deployment
./deploy-azure.sh
```

### Using PowerShell

```powershell
# Update the script with your values
notepad deploy-azure.ps1

# Run deployment
.\deploy-azure.ps1
```

### Using Azure Portal

1. Go to Azure Portal
2. Search for "Deploy a custom template"
3. Click "Build your own template in the editor"
4. Copy content from `azure-deployment.json`
5. Fill in parameters
6. Review and create

## Step 6: Configure Environment Variables in Azure

```bash
# Set application settings
az webapp config appsettings set \
  --name seo-geo-aeo-api \
  --resource-group rg-seo-geo-aeo \
  --settings \
    GSC_CLIENT_ID="your-client-id" \
    GSC_CLIENT_SECRET="your-client-secret" \
    GSC_REFRESH_TOKEN="your-refresh-token" \
    GSC_SITE_URL="https://yoursite.com" \
    SAFE_BROWSING_API_KEY="your-api-key"
```

## Step 7: Microsoft AI Foundry Integration

### Update run_model.py

The `run_model.py` file is already configured to work with Azure OpenAI. Update the `.env` file:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### Integrate with FastAPI Application

You can integrate the AI Foundry model into your analysis pipeline:

```python
# In project/analysis/engines_optimization/aeo/service.py
from run_model import client, deployment_name

def analyze_with_ai(content: str):
    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this content for AEO: {content}"
            }
        ],
        temperature=0.7
    )
    return completion.choices[0].message.content
```

## Step 8: Monitor and Troubleshoot

### View Application Logs

```bash
# Stream logs
az webapp log tail \
  --name seo-geo-aeo-api \
  --resource-group rg-seo-geo-aeo

# Download logs
az webapp log download \
  --name seo-geo-aeo-api \
  --resource-group rg-seo-geo-aeo \
  --log-file app-logs.zip
```

### Check Application Health

```bash
# Health endpoint
curl https://seo-geo-aeo-api.azurewebsites.net/api/health

# Test analysis
curl -X POST https://seo-geo-aeo-api.azurewebsites.net/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Common Issues

1. **Container fails to start**

   - Check container logs in Azure Portal
   - Verify WEBSITES_PORT is set to 8001
   - Ensure Playwright browsers are installed

2. **Pipeline fails to build**

   - Check service connection permissions
   - Verify Docker registry credentials
   - Review build logs in Azure DevOps

3. **API returns 500 errors**
   - Check environment variables
   - Verify Playwright is working
   - Check application logs

## Step 9: Set Up Continuous Deployment

The pipeline is configured to automatically deploy when you push to the `main` branch:

```bash
# Make changes
git add .
git commit -m "Update application"
git push origin main

# Pipeline will automatically:
# 1. Build the application
# 2. Run tests
# 3. Build Docker image
# 4. Push to ACR
# 5. Deploy to Azure App Service
```

## Cost Optimization

**Recommended SKUs:**

- **Development**: B1 ($13/month)
- **Production**: B2 ($30/month) - Recommended for Playwright
- **High Traffic**: P1V2 ($80/month)

**Cost-Saving Tips:**

- Use auto-scaling to scale down during off-hours
- Use Azure Container Instances for sporadic workloads
- Implement caching to reduce API calls

## Security Best Practices

1. **Never commit .env files** - Already in .gitignore
2. **Use Azure Key Vault** for sensitive data
3. **Enable HTTPS only** - Configured in ARM template
4. **Use managed identities** when possible
5. **Implement rate limiting** in FastAPI
6. **Enable Application Insights** for monitoring

## Next Steps

1. **Set up monitoring** with Application Insights
2. **Configure auto-scaling** based on traffic
3. **Implement caching** with Azure Redis Cache
4. **Add authentication** (OAuth 2.0, Azure AD)
5. **Set up staging environment** for testing
6. **Configure custom domain** and SSL certificate

## Support

For issues or questions:

1. Check Azure DevOps pipeline logs
2. Review Application logs in Azure Portal
3. Check the project README in `/project/`
4. Contact your Azure administrator

## References

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure DevOps Pipelines](https://docs.microsoft.com/en-us/azure/devops/pipelines/)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Microsoft AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry/)
