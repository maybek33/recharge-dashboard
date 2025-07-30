#!/bin/bash

# Recharge.com Dashboard Setup Script
echo "🔋 Setting up Recharge.com Ranking Dashboard..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python -m venv dashboard_env

# Activate virtual environment
echo "⚡ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    source dashboard_env/Scripts/activate
else
    # Linux/Mac
    source dashboard_env/bin/activate
fi

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Copy secrets template if secrets.toml doesn't exist
if [ ! -f ".streamlit/secrets.toml" ]; then
    if [ -f ".streamlit/secrets.toml.template" ]; then
        echo "⚙️ Creating secrets template..."
        cp .streamlit/secrets.toml.template .streamlit/secrets.toml
        echo "📝 Please edit .streamlit/secrets.toml with your Google credentials"
    else
        echo "⚠️ secrets.toml.template not found. Creating basic template..."
        cat > .streamlit/secrets.toml << 'EOF'
# Add your Google service account credentials here
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
EOF
    fi
fi

# Check if main app file exists
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ streamlit_app.py not found!"
    echo "   Please ensure the main dashboard file is in the current directory."
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. 🔑 Configure Google Sheets API:"
echo "   - Create Google Cloud project"
echo "   - Enable Google Sheets API and Google Drive API"
echo "   - Create service account and download JSON key"
echo "   - Share your Google Sheet with the service account email"
echo ""
echo "2. ⚙️ Configure secrets:"
echo "   - Edit .streamlit/secrets.toml with your Google credentials"
echo "   - Copy values from your service account JSON file"
echo ""
echo "3. 🚀 Run the dashboard:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "🌐 Your dashboard will be available at: http://localhost:8501"
echo ""
echo "📚 For detailed setup instructions, see README.md"

# Make the script executable on Unix systems
if [[ "$OSTYPE" != "msys" ]] && [[ "$OSTYPE" != "win32" ]]; then
    chmod +x setup.sh
fi
