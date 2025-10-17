#!/bin/bash

# Deployment script for the API
# This script helps deploy the API to various environments

set -e  # Exit on error

echo "=========================================="
echo "Deployment API - Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo "Please create a .env file based on env.template"
    echo "Run: cp env.template .env"
    exit 1
fi

print_success ".env file found"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

print_success "Python 3 is installed"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python version $PYTHON_VERSION is less than required $REQUIRED_VERSION"
    exit 1
fi

print_success "Python version $PYTHON_VERSION is compatible"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found, creating..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment exists"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate 2>/dev/null

# Upgrade pip
pip install --upgrade pip --quiet

# Install dependencies
print_warning "Installing dependencies..."
pip install -r requirements.txt --quiet
print_success "Dependencies installed"

# Load environment variables
set -a
source .env
set +a

# Verify required environment variables
REQUIRED_VARS=("SECRET_CODE" "GITHUB_TOKEN" "GITHUB_USERNAME" "OPENAI_API_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

print_success "All required environment variables are set"

# Ask deployment mode
echo ""
echo "Select deployment mode:"
echo "1) Development (with auto-reload)"
echo "2) Production (single worker)"
echo "3) Production (multiple workers)"
echo "4) Docker"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        print_success "Starting in development mode..."
        uvicorn app:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        print_success "Starting in production mode (single worker)..."
        uvicorn app:app --host 0.0.0.0 --port 8000
        ;;
    3)
        if ! command -v gunicorn &> /dev/null; then
            print_warning "Gunicorn not installed, installing..."
            pip install gunicorn --quiet
        fi
        print_success "Starting in production mode (4 workers)..."
        gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
        ;;
    4)
        if ! command -v docker &> /dev/null; then
            print_error "Docker is not installed"
            exit 1
        fi
        print_success "Starting with Docker..."
        docker-compose up --build
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

