# SEO-GEO-AEO API - Azure DevOps & Microsoft AI Foundry Integration

This project integrates the SEO-GEO-AEO API with Azure DevOps for CI/CD deployment and Microsoft AI Foundry for AI-powered analysis.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Azure subscription (for deployment)
- Azure DevOps organization (for CI/CD)
- Docker Desktop (for local containerization)

### Local Development

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd azuredev-979b
   ```

2. **Set up environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate (Windows)
   .\venv\Scripts\activate

   # Activate (Linux/Mac)
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   cd project
   pip install -r requirements.txt
   playwright install chromium
   cd scripts
   npm install
   cd ../..
   ```

4. **Configure environment variables**

   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env and add your Azure OpenAI credentials
   notepad .env  # Windows
   # or
   nano .env     # Linux/Mac
   ```

5. **Test Azure AI Foundry integration**

   ```bash
   python run_model.py
   ```

6. **Run the API locally**

   ```bash
   cd project
   python main.py
   ```

   The API will be available at `http://localhost:8001`

### Docker Development

1. **Build and run with Docker Compose**

   ```bash
   docker-compose up -d
   ```

2. **View logs**

   ```bash
   docker-compose logs -f
   ```

3. **Stop containers**
   ```bash
   docker-compose down
   ```

## 📁 Project Structure

```
azuredev-979b/
├── .azure/                      # Azure DevOps configurations (if needed)
├── project/                     # Main SEO-GEO-AEO API application
│   ├── main.py                 # FastAPI entry point
│   ├── analysis/               # Analysis modules (SEO, GEO, AEO)
│   ├── pipeline/               # Processing pipeline
│   ├── routers/                # API route handlers
│   ├── scripts/                # Unlighthouse Node.js scripts
│   └── requirements.txt        # Python dependencies
├── azure-pipelines.yml         # Azure DevOps CI/CD pipeline
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Local Docker setup
├── azure-deployment.json       # Azure ARM template
├── deploy-azure.sh            # Bash deployment script
├── deploy-azure.ps1           # PowerShell deployment script
├── run_model.py               # Azure AI Foundry integration
├── requirements.txt           # Root Python dependencies
├── .env.example              # Environment variables template
└── AZURE_DEPLOYMENT.md       # Comprehensive deployment guide
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example` and configure:

- **Azure OpenAI/AI Foundry**: Required for AI-powered analysis

  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_DEPLOYMENT`

- **Google APIs** (Optional): For enhanced SEO checks
  - `GSC_CLIENT_ID`, `GSC_CLIENT_SECRET`, `GSC_REFRESH_TOKEN`
  - `SAFE_BROWSING_API_KEY`

## 🚢 Deployment

### Option 1: Azure DevOps Pipeline (Recommended)

1. Push code to Azure DevOps repository
2. Configure service connections in Azure DevOps
3. Update variables in `azure-pipelines.yml`
4. Create and run the pipeline

See [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md) for detailed instructions.

### Option 2: Manual Deployment

**Using PowerShell** (Windows):

```powershell
.\deploy-azure.ps1
```

**Using Bash** (Linux/Mac/WSL):

```bash
chmod +x deploy-azure.sh
./deploy-azure.sh
```

### Option 3: Docker Hub/Container Registry

```bash
# Build
docker build -t seo-geo-aeo-api:latest .

# Tag
docker tag seo-geo-aeo-api:latest yourregistry.azurecr.io/seo-geo-aeo-api:latest

# Push
docker push yourregistry.azurecr.io/seo-geo-aeo-api:latest
```

## 🧪 API Testing

### Health Check

```bash
curl http://localhost:8001/api/health
```

### Analyze URL

```bash
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### AI-Powered Analysis

The `run_model.py` module provides functions to enhance analysis with Azure OpenAI:

```python
from run_model import analyze_content_with_ai

# Analyze content
result = analyze_content_with_ai(
    content="Your web page content here",
    analysis_type="SEO"  # or "GEO" or "AEO"
)
```

## 🔒 Security

- Never commit `.env` files
- Use Azure Key Vault for production secrets
- Enable HTTPS only in production
- Implement rate limiting
- Use managed identities where possible

## 📊 Features

### SEO Analysis

- Google Search Console integration
- Safe Browsing verification
- Spam protection
- Meta tag analysis
- AI-powered content optimization

### GEO (Generative Engine Optimization)

- Factual accuracy verification
- Transparent intent detection
- AI spam detection
- Cloaking detection

### AEO (Answer Engine Optimization)

- Factual accuracy checking
- EEAT compliance validation
- AI-enhanced content recommendations

## 🤖 Microsoft AI Foundry Integration

The project integrates with Microsoft AI Foundry (Azure OpenAI) to provide:

- **Intelligent Content Analysis**: AI-powered insights for SEO/GEO/AEO
- **Automated Recommendations**: Smart suggestions for content optimization
- **Natural Language Processing**: Understanding content context and quality
- **Scalable AI Services**: Enterprise-grade AI capabilities

See `run_model.py` for integration examples.

## 📚 Documentation

- [Azure Deployment Guide](./AZURE_DEPLOYMENT.md) - Complete deployment instructions
- [Project README](./project/README.md) - Main application documentation
- [API Documentation](http://localhost:8001/docs) - Interactive API docs (when running)

## 🛠️ Development Tools

- **FastAPI**: Modern Python web framework
- **Playwright**: Browser automation
- **Unlighthouse**: Performance analysis
- **OpenAI SDK**: Azure OpenAI integration
- **Docker**: Containerization
- **Azure DevOps**: CI/CD pipelines

## 📝 License

Internal use only.

## 🆘 Troubleshooting

### Common Issues

1. **Module not found errors**

   ```bash
   pip install -r requirements.txt
   pip install -r project/requirements.txt
   ```

2. **Playwright browser not found**

   ```bash
   playwright install chromium
   ```

3. **Docker build fails**

   - Check Docker is running
   - Verify Dockerfile syntax
   - Review build logs

4. **Azure deployment fails**
   - Check service connection permissions
   - Verify Azure credentials
   - Review deployment logs

### Getting Help

1. Check the [Azure Deployment Guide](./AZURE_DEPLOYMENT.md)
2. Review application logs
3. Check Azure DevOps pipeline logs
4. Consult the project documentation

## 🎯 Next Steps

1. ✅ Configure `.env` file
2. ✅ Test locally with `python run_model.py`
3. ✅ Run API server and test endpoints
4. ✅ Set up Azure DevOps project
5. ✅ Configure service connections
6. ✅ Run first deployment
7. ✅ Configure monitoring
8. ✅ Set up production environment

---

**Built with ❤️ for Microsoft AI Foundry**
