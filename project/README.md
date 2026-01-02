# SEO-GEO-AEO API

A standalone API for SEO, GEO, and AEO website analysis. This project is extracted from the Site360 main project and works independently.

## Features

- **SEO Analysis**: Google Search Console checks, Safe Browsing verification, Spam protection
- **GEO Analysis**: Factual accuracy, Transparent intent, AI spam detection, Cloaking detection
- **AEO Analysis**: Factual accuracy verification, EEAT compliance checking

## Prerequisites

1. **Node.js** (v18 or higher) - Required for Unlighthouse crawler
2. **Python** (3.10 or higher)
3. **Chromium browser** - Installed via Playwright

## Installation

### 1. Install Python dependencies

```bash
cd SEO-GEO-AEO-API
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

### 3. Install Node.js dependencies (for Unlighthouse)

```bash
cd project/scripts
npm install
cd ../..
```

### 4. Configure environment variables

```bash
# Copy the example env file
cp .env.example project/.env

# Edit project/.env and add your API keys (optional)
```

## Running the API

```bash
cd project
python main.py
```

Or using uvicorn directly:

```bash
cd project
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`

## API Endpoints

### POST /api/analyze

Analyze a URL for SEO, GEO, and AEO metrics.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "data": {
    "results": {
      "seo": [...],
      "geo": [...],
      "aeo": [...]
    },
    "page_type": "other"
  }
}
```

### GET /api/health

Health check endpoint.

### GET /

Root endpoint with service information.

## Project Structure

```
SEO-GEO-AEO-API/
├── project/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Configuration loader
│   ├── analysis/
│   │   ├── views.py               # BaseAnalyser class
│   │   ├── constants.py           # ANALYSERS enum
│   │   ├── unlighthouse_routes.py # Unlighthouse runner
│   │   └── engines_optimization/
│   │       ├── common.py          # Shared utilities
│   │       ├── views.py           # EOCheckResult, EOPageResult
│   │       ├── seo/service.py     # SEO analyzer
│   │       ├── geo/service.py     # GEO analyzer
│   │       └── aeo/service.py     # AEO analyzer
│   ├── pipeline/
│   │   ├── views.py               # PreContext, DiscoveredPage
│   │   ├── constants.py           # PageCategories
│   │   └── service.py             # Main pipeline
│   ├── infra/
│   │   └── files.py               # Path configuration
│   ├── routers/
│   │   └── analyze.py             # API endpoints
│   └── scripts/                   # Unlighthouse Node.js scripts
├── config.yml                     # Project configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Environment Variables (Optional)

| Variable | Description |
|----------|-------------|
| `GSC_CLIENT_ID` | Google Search Console OAuth Client ID |
| `GSC_CLIENT_SECRET` | Google Search Console OAuth Client Secret |
| `GSC_REFRESH_TOKEN` | Google Search Console OAuth Refresh Token |
| `GSC_SITE_URL` | Site URL registered in GSC |
| `SAFE_BROWSING_API_KEY` | Google Safe Browsing API Key |

If these are not configured, the corresponding checks will show as "warn" with a message indicating they couldn't be verified.

## License

Internal use only.
