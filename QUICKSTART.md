# 🚀 Quick Start Guide

Get your dashboard running in 15 minutes!

## 📋 Checklist

- [ ] Python 3.8+ installed
- [ ] Google Cloud account
- [ ] Access to your Google Sheet
- [ ] GitHub account (for deployment)

## ⚡ Step 1: Google Cloud Setup (5 minutes)

### 1.1 Create Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project: **"recharge-dashboard"**

### 1.2 Enable APIs
1. **APIs & Services** → **Library**
2. Search and enable:
   - **Google Sheets API**
   - **Google Drive API**

### 1.3 Create Service Account
1. **APIs & Services** → **Credentials**
2. **Create Credentials** → **Service account**
3. Name: **"streamlit-dashboard"**
4. Role: **"Viewer"**
5. **Create and download JSON key**

### 1.4 Share Your Google Sheet
1. Open your Google Sheet
2. **Share** → Add the service account email
3. Permission: **Viewer**

## ⚡ Step 2: Local Setup (5 minutes)

### 2.1 Download Files
Save all the provided files in a folder:
```
recharge-dashboard/
├── streamlit_app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── secrets.toml.template
├── README.md
└── setup.sh
```

### 2.2 Run Setup
```bash
# Navigate to your folder
cd recharge-dashboard

# Run setup script
bash setup.sh

# OR manual setup:
python -m venv dashboard_env
source dashboard_env/bin/activate  # Windows: dashboard_env\Scripts\activate
pip install -r requirements.txt
```

### 2.3 Configure Secrets
1. **Copy** `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml`
2. **Edit** `secrets.toml` with your Google credentials:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-actual-project-id"
   private_key_id = "your-actual-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR-ACTUAL-PRIVATE-KEY\n-----END PRIVATE KEY-----\n"
   client_email = "your-actual-service-account@your-project.iam.gserviceaccount.com"
   # ... copy all values from your JSON file
   ```

### 2.4 Test Locally
```bash
streamlit run streamlit_app.py
```
Open: [http://localhost:8501](http://localhost:8501)

## ⚡ Step 3: Deploy Online (5 minutes)

### 3.1 Push to GitHub
```bash
git init
git add .
git commit -m "Initial dashboard setup"
git remote add origin https://github.com/YOUR_USERNAME/recharge-dashboard.git
git push -u origin main
```

### 3.2 Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. **New app** → Connect GitHub repo
3. **Main file**: `streamlit_app.py`
4. **Deploy**

### 3.3 Add Secrets in Cloud
1. **App settings** → **Secrets**
2. Copy content from your local `.streamlit/secrets.toml`
3. **Save**

## 🎉 Done!

Your dashboard is now live! Share the URL with your team.

## 🚨 Troubleshooting

### "Permission denied" error
- Check service account email is added to Google Sheet
- Verify APIs are enabled

### "Module not found" error
- Run: `pip install -r requirements.txt`
- Make sure virtual environment is activated

### "No data found" error
- Check Google Sheet URL in `streamlit_app.py` line 49
- Verify sheet has data and correct column names

### Dashboard not updating
- Check if your automation script is running
- Verify new data is being added to Google Sheets

## 📞 Need Help?

1. Check the full README.md for detailed instructions
2. Verify all steps in this quickstart guide
3. Check Google Cloud Console for API quotas
4. Ensure Google Sheet permissions are correct

## 🎯 What You Get

- **📊 Real-time dashboard** updating every 5 minutes
- **🌍 Multi-market tracking** with country flags
- **📈 Visual analytics** with charts and metrics
- **🤖 AI Overview monitoring** 
- **📱 Mobile-friendly** responsive design
- **🔒 Secure** with no credentials in code

Your dashboard will show:
- Top 3 positions count
- Positions 4-10 tracking
- Not ranking alerts
- AI Overview coverage
- Market performance cards
- Interactive filtering

**Total setup time: ~15 minutes**
**Result: Professional dashboard accessible anywhere!**
