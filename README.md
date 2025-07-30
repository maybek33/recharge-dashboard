# 🔋 Recharge.com Ranking Dashboard

Real-time SEO ranking tracker with beautiful visualizations and AI Overview monitoring.

## 🚀 Live Dashboard
[View Dashboard](https://your-app-name.streamlit.app) *(Update with your actual URL)*

## 📊 Features

- ✅ **Real-time data** from Google Sheets
- ✅ **Interactive filters** by market, position, AI status
- ✅ **Beautiful charts** and visualizations
- ✅ **Mobile-responsive** design
- ✅ **Auto-refresh** every 5 minutes
- ✅ **Market performance** analytics
- ✅ **AI Overview tracking** with source links
- ✅ **Position change monitoring** (Improved/Declined/Lost/New)

## 🎯 Key Metrics Tracked

- **🟢 Top 3 Positions** - Keywords ranking in positions 1-3
- **🟡 Positions 4-10** - Keywords ranking in positions 4-10  
- **🔴 Not Ranking** - Keywords not found in search results
- **🤖 AI Overviews** - Keywords triggering Google AI responses

## 🌍 Markets Monitored

- 🇪🇸 Spain
- 🇮🇹 Italy
- 🇫🇷 France
- 🇵🇭 Philippines
- 🇩🇿 Algeria
- 🇦🇺 Australia
- *And more...*

## 🔧 Local Development Setup

### Prerequisites
- Python 3.8+
- Google Cloud Project with Sheets API enabled
- Service account with access to your Google Sheet

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/recharge-ranking-dashboard.git
cd recharge-ranking-dashboard

# Create virtual environment
python -m venv dashboard_env
source dashboard_env/bin/activate  # On Windows: dashboard_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets (see setup guide below)
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml with your Google credentials

# Run dashboard
streamlit run streamlit_app.py
```

### Google Sheets API Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to APIs & Services → Credentials
   - Create Credentials → Service account
   - Download JSON key file

4. **Share Google Sheet**
   - Add service account email to your Google Sheet with Viewer access
   - Sheet URL: `https://docs.google.com/spreadsheets/d/1hOMEaZ_zfliPxJ7N-9EJ64KvyRl9J-feoR30GB-bI_o/edit`

5. **Configure Secrets**
   - Copy values from service account JSON to `.streamlit/secrets.toml`
   - Never commit this file to Git (it's in .gitignore)

## 🌐 Deployment (Streamlit Cloud)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial dashboard setup"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file path: `streamlit_app.py`

3. **Add Secrets in Cloud**
   - In Streamlit Cloud app settings
   - Add secrets from your local `.streamlit/secrets.toml`
   - Save and redeploy

## 📱 Usage

The dashboard automatically updates with fresh data from your Google Sheet. Use the sidebar filters to explore:

- **Market Filter**: View specific countries/regions
- **Position Range**: Focus on top performers or problem areas  
- **AI Overview**: See which keywords trigger AI responses

## 🎨 Dashboard Sections

### Key Metrics Cards
Overview of ranking performance with percentages and counts.

### Keywords Overview Table  
Detailed table showing:
- Keyword and target market
- Current position with color coding
- Trend arrows (📈📉➡️) 
- AI Overview status (🤖)
- Last check timestamp

### Analytics Charts
- **Position Distribution**: Pie chart of ranking ranges
- **Market Performance**: Bar chart by country

### Market Performance Cards
Individual country statistics with keyword counts, average positions, and AI coverage.

## 🔄 Data Sources

The dashboard connects to your Google Sheet containing keyword tracking data from your Oxylabs automation script. Data includes:

- Keyword rankings and position changes
- AI Overview detection and source links
- Market-specific performance data
- Historical tracking timestamps

## 🛠️ Customization

### Update Sheet URL
In `streamlit_app.py`, line 49:
```python
sheet_url = "YOUR_GOOGLE_SHEET_URL"
```

### Add New Markets
In `get_country_flag()` function:
```python
flag_map = {
    'br': '🇧🇷 Brazil',
    'mx': '🇲🇽 Mexico',
    # Add new country codes
}
```

### Change Refresh Rate
Line 27:
```python
@st.cache_data(ttl=300)  # 300 = 5 minutes
```

## 🚨 Security

- ✅ Credentials stored securely in Streamlit Cloud secrets
- ✅ No sensitive data committed to repository
- ✅ Google Sheets access via service account
- ✅ Read-only access to data sources

## 📞 Support

For issues or questions:
1. Check the troubleshooting section in setup guide
2. Verify Google Sheets API setup
3. Confirm service account permissions
4. Check Streamlit Cloud deployment logs

## 📈 Future Enhancements

- 📧 Email alerts for ranking changes
- 📊 Historical trend analysis
- 📋 CSV export functionality
- 🔍 Competitor analysis
- 📱 Mobile app notifications

---

Built with ❤️ using [Streamlit](https://streamlit.io) and powered by real-time Google Sheets data.
