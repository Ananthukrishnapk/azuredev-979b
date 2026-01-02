#!/bin/bash

# Quick Setup Script for SEO-GEO-AEO API with Azure AI Foundry
# This script automates the initial project setup

set -e

echo "🚀 SEO-GEO-AEO API - Quick Setup"
echo "================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python
else
    echo -e "${RED}✗ Python not found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

# Check Node.js
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Found Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install root dependencies
echo ""
echo -e "${YELLOW}Installing root dependencies...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Root dependencies installed${NC}"

# Install project dependencies
echo ""
echo -e "${YELLOW}Installing project dependencies...${NC}"
pip install -r project/requirements.txt --quiet
echo -e "${GREEN}✓ Project dependencies installed${NC}"

# Install Playwright browsers
echo ""
echo -e "${YELLOW}Installing Playwright browsers (this may take a while)...${NC}"
playwright install chromium
echo -e "${GREEN}✓ Playwright browsers installed${NC}"

# Install Node.js dependencies
echo ""
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
cd project/scripts
npm install --silent
cd ../..
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

# Create .env file if it doesn't exist
echo ""
echo -e "${YELLOW}Setting up environment variables...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file already exists${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
    echo -e "${YELLOW}⚠ IMPORTANT: Edit .env file and add your Azure OpenAI credentials!${NC}"
fi

# Create necessary directories
echo ""
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p project/temp project/unlighthouse project/artifacts
echo -e "${GREEN}✓ Directories created${NC}"

# Summary
echo ""
echo "================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================="
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "${NC}1. Edit .env file with your Azure OpenAI credentials${NC}"
echo -e "   ${CYAN}nano .env${NC}"
echo ""
echo -e "${NC}2. Test Azure AI Foundry integration:${NC}"
echo -e "   ${CYAN}python run_model.py${NC}"
echo ""
echo -e "${NC}3. Run the API server:${NC}"
echo -e "   ${CYAN}cd project${NC}"
echo -e "   ${CYAN}python main.py${NC}"
echo ""
echo -e "${NC}4. Access the API at:${NC}"
echo -e "   ${CYAN}http://localhost:8001${NC}"
echo -e "   ${CYAN}http://localhost:8001/docs${NC} (API documentation)"
echo ""
echo -e "${YELLOW}For deployment to Azure, see AZURE_DEPLOYMENT.md${NC}"
echo ""
