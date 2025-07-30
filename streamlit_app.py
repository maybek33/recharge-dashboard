import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials
import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Recharge.com Ranking Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main > div {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .stSelectbox label {
        color: white !important;
        font-weight: 500;
    }
    
    .css-1d391kg .stRadio label {
        color: white !important;
        font-weight: 500;
    }
    
    .css-1d391kg .stCheckbox label {
        color: white !important;
        font-weight: 500;
    }
    
    .css-1d391kg .stDateInput label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 1.5rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Metric Cards */
    .stMetric {
        background: white;
        border: none;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }
    
    .stMetric label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        color: #374151 !important;
    }
    
    .stMetric .metric-value {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        color: #1f2937;
    }
    
    /* Section Headers */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
        color: #1f2937;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Data Tables */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
        border: none !important;
    }
    
    .stDataFrame > div {
        border-radius: 12px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Date Comparison Cards */
    .comparison-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .comparison-improved {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    }
    
    .comparison-declined {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fefcfc 100%);
    }
    
    .comparison-new {
        border-left: 4px solid #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    }
    
    .comparison-lost {
        border-left: 4px solid #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fefcf0 100%);
    }
    
    /* Alert Boxes */
    .alert-success {
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        color: #166534;
        font-family: 'Inter', sans-serif;
    }
    
    .alert-warning {
        background: #fef3c7;
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 1rem;
        color: #92400e;
        font-family: 'Inter', sans-serif;
    }
    
    .alert-danger {
        background: #fee2e2;
        border: 1px solid #fca5a5;
        border-radius: 8px;
        padding: 1rem;
        color: #dc2626;
        font-family: 'Inter', sans-serif;
    }
    
    .alert-info {
        background: #dbeafe;
        border: 1px solid #93c5fd;
        border-radius: 8px;
        padding: 1rem;
        color: #1d4ed8;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Data loading functions
@st.cache_data(ttl=300)
def load_data_from_sheets():
    """Load data from PUBLIC Google Sheets"""
    try:
        sheet_id = "1hOMEaZ_zfliPxJ7N-9EJ64KvyRl9J-feoR30GB-bI_o"
        
        try:
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                credentials_dict = st.secrets["gcp_service_account"]
                credentials = Credentials.from_service_account_info(credentials_dict, scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
                gc = gspread.authorize(credentials)
            else:
                return load_public_sheet_data(sheet_id)
        except:
            return load_public_sheet_data(sheet_id)
        
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
        spreadsheet = gc.open_by_url(sheet_url)
        worksheets = spreadsheet.worksheets()
        
        keyword_sheets = [ws for ws in worksheets if ws.title not in ['Main', 'ADMIN', '⚙️ ADMIN']]
        
        all_data = []
        for sheet in keyword_sheets:
            try:
                data = sheet.get_all_records()
                if data:
                    df = pd.DataFrame(data)
                    df['Sheet_Name'] = sheet.title
                    all_data.append(df)
            except Exception as e:
                st.warning(f"Could not read sheet {sheet.title}: {e}")
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return load_public_sheet_data(sheet_id)
            
    except Exception as e:
        st.warning(f"Using public access method due to: {e}")
        return load_public_sheet_data("1hOMEaZ_zfliPxJ7N-9EJ64KvyRl9J-feoR30GB-bI_o")

def load_public_sheet_data(sheet_id):
    """Load data from public Google Sheet using CSV export"""
    try:
        potential_gids = [0, 1933593504, 1, 2, 3, 4, 5]
        all_data = []
        successful_sheets = 0
        
        for gid in potential_gids:
            try:
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                df = pd.read_csv(csv_url)
                
                if df.empty or len(df.columns) < 5:
                    continue
                
                df['Sheet_Name'] = f'sheet_gid_{gid}'
                
                if 'Keyword' in df.columns or 'Date/Time' in df.columns:
                    all_data.append(df)
                    successful_sheets += 1
                
                if successful_sheets >= 10:
                    break
                    
            except Exception as e:
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            st.success(f"✅ Successfully loaded data from {successful_sheets} sheets")
            return combined_df
        else:
            st.info("📊 Using sample data for demonstration")
            return get_enhanced_sample_data()
            
    except Exception as e:
        st.error(f"Could not load public sheet data: {e}")
        st.info("📊 Using sample data for demonstration")
        return get_enhanced_sample_data()

def get_enhanced_sample_data():
    """Enhanced sample data with multiple dates for comparison"""
    np.random.seed(42)
    
    # Create data for multiple dates
    dates = pd.date_range('2025-07-25', periods=6, freq='D')  # 6 days of data
    
    keywords_data = [
        ('recarga digi', 'es', 'es', '🇪🇸 Spain'),
        ('ricarica iliad', 'it', 'it', '🇮🇹 Italy'),
        ('recharge transcash', 'fr', 'fr', '🇫🇷 France'),
        ('buy robux', 'en', 'ph', '🇵🇭 Philippines'),
        ('neosurf voucher', 'en', 'au', '🇦🇺 Australia'),
        ('flexy mobilis', 'fr', 'dz', '🇩🇿 Algeria'),
        ('digimobil recarga', 'es', 'es', '🇪🇸 Spain'),
        ('iliad ricarica online', 'it', 'it', '🇮🇹 Italy')
    ]
    
    sample_data = []
    
    for date in dates:
        for keyword, lang, loc, market in keywords_data:
            # Simulate position evolution over time
            base_position = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20], p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05])
            
            # Add some position drift over time
            date_index = list(dates).index(date)
            position_drift = np.random.choice([-2, -1, 0, 1, 2], p=[0.1, 0.2, 0.4, 0.2, 0.1])
            position = max(1, min(20, base_position + (date_index * 0.5) + position_drift))
            
            # Simulate position changes
            if date_index == 0:
                change_type = 'New'
            else:
                change_options = ['Stable', 'Improved (+1)', 'Improved (+2)', 'Declined (-1)', 'Declined (-2)']
                change_probs = [0.5, 0.15, 0.1, 0.15, 0.1]
                change_type = np.random.choice(change_options, p=change_probs)
            
            # Position can become "Not Ranking" sometimes
            if position > 15 and np.random.random() > 0.7:
                position = 'Not Ranking'
                change_type = 'Lost' if date_index > 0 else 'New'
            
            # AI Overview simulation with evolution
            ai_probability = 0.2 + (date_index * 0.05)  # Increasing AI presence over time
            ai_present = np.random.choice([True, False], p=[ai_probability, 1-ai_probability])
            
            ai_links = ""
            if ai_present:
                ai_links = f"https://example1.com/ai-source-{keyword.replace(' ', '-')}\nhttps://example2.com/reference-{keyword.replace(' ', '-')}"
            
            # Generate realistic competitor URLs
            competitors = [
                f"https://competitor1.com/{keyword.replace(' ', '-')}",
                f"https://competitor2.com/{keyword.replace(' ', '-')}",
                f"https://competitor3.com/{keyword.replace(' ', '-')}",
                f"https://site4.com/{keyword.replace(' ', '-')}",
                f"https://platform5.com/{keyword.replace(' ', '-')}"
            ]
            
            recharge_url = ""
            if isinstance(position, int) and position <= 10:
                recharge_url = f"https://www.recharge.com/{lang}/{loc}/{keyword.replace(' ', '')}"
            
            full_results = f"""--- AI OVERVIEW SECTION ---
CONTENT:
{'Comprehensive guide for ' + keyword + '. Step-by-step instructions and best practices for ' + keyword + ' in ' + market + '. This includes detailed information about the process and recommended approaches.' if ai_present else 'No AI Overview detected for this search.'}
SOURCE LINKS (from source_panel):
{ai_links if ai_present else 'No source links available'}
--- END AI OVERVIEW ---
--- ORGANIC SEARCH RESULTS ---
POSITION 1:
  Title: {keyword.title()} - Complete Guide | {competitors[0].split('/')[2].title()}
  URL: {competitors[0]}
  Description: Everything you need to know about {keyword}. Comprehensive guide with step-by-step instructions.
"""
            
            sample_data.append({
                'Date/Time': date.strftime('%Y-%m-%d %H:%M'),
                'Keyword': keyword,
                'Position 1': competitors[0],
                'Position 2': competitors[1],
                'Position 3': competitors[2],
                'Position 4': competitors[3],
                'Position 5': competitors[4],
                'Recharge URL': recharge_url,
                'Recharge Position': position,
                'Position Change': change_type,
                'AI Overview': 'Yes' if ai_present else 'No',
                'AIO Links': ai_links,
                'Full Results Data': full_results,
                'Sheet_Name': f'{keyword.replace(" ", "_")}_{lang}_{loc}',
                'Market': market
            })
    
    return pd.DataFrame(sample_data)

# Utility functions
def parse_sheet_info(sheet_name):
    """Extract keyword, language, and location from sheet name"""
    parts = sheet_name.split('_')
    if len(parts) >= 3:
        keyword = ' '.join(parts[:-2])
        language = parts[-2] if len(parts) >= 2 else 'Unknown'
        location = parts[-1] if len(parts) >= 1 else 'Unknown'
        return keyword, language, location
    return sheet_name, 'Unknown', 'Unknown'

def get_country_flag(location_code):
    """Get country flag emoji from location code"""
    flag_map = {
        'es': '🇪🇸 Spain',
        'it': '🇮🇹 Italy', 
        'fr': '🇫🇷 France',
        'ph': '🇵🇭 Philippines',
        'dz': '🇩🇿 Algeria',
        'au': '🇦🇺 Australia',
        'us': '🇺🇸 United States',
        'uk': '🇬🇧 United Kingdom',
        'de': '🇩🇪 Germany',
        'nl': '🇳🇱 Netherlands'
    }
    return flag_map.get(location_code.lower(), f'🌍 {location_code.upper()}')

def get_position_status(position):
    """Get position status and color"""
    if pd.isna(position) or position == '' or str(position).lower() in ['not ranking', 'lost']:
        return 'Not Ranking', '#dc2626'
    try:
        pos = int(position)
        if pos <= 3:
            return f'#{pos}', '#166534'
        elif pos <= 10:
            return f'#{pos}', '#92400e'
        else:
            return f'#{pos}', '#dc2626'
    except:
        return str(position), '#6b7280'

def get_trend_emoji(change):
    """Get trend emoji based on change"""
    if pd.isna(change) or change == '':
        return '➡️'
    change_str = str(change).lower()
    if 'improved' in change_str or 'new' in change_str:
        return '📈'
    elif 'declined' in change_str or 'lost' in change_str:
        return '📉'
    else:
        return '➡️'

def calculate_position_change(pos1, pos2):
    """Calculate position change between two positions"""
    # Handle 'Not Ranking' cases
    if str(pos1).lower() in ['not ranking', 'lost', ''] or pd.isna(pos1):
        pos1_val = None
    else:
        try:
            pos1_val = int(pos1)
        except:
            pos1_val = None
    
    if str(pos2).lower() in ['not ranking', 'lost', ''] or pd.isna(pos2):
        pos2_val = None
    else:
        try:
            pos2_val = int(pos2)
        except:
            pos2_val = None
    
    # Calculate change
    if pos1_val is None and pos2_val is None:
        return 0, "No change (both not ranking)"
    elif pos1_val is None and pos2_val is not None:
        return float('inf'), f"New ranking at #{pos2_val}"
    elif pos1_val is not None and pos2_val is None:
        return float('-inf'), f"Lost ranking (was #{pos1_val})"
    else:
        change = pos1_val - pos2_val  # Positive = improvement (lower position number)
        if change > 0:
            return change, f"Improved by {change} positions (#{pos1_val} → #{pos2_val})"
        elif change < 0:
            return change, f"Declined by {abs(change)} positions (#{pos1_val} → #{pos2_val})"
        else:
            return 0, f"No change (#{pos1_val})"

# Date comparison functionality
def show_date_comparison(df_processed):
    """Enhanced Date Comparison Page"""
    st.markdown('<h2 class="section-header">📅 Date Comparison Analysis</h2>', unsafe_allow_html=True)
    
    # Get available dates
    if 'DateTime' in df_processed.columns:
        df_processed['Date'] = df_processed['DateTime'].dt.date
        available_dates = sorted(df_processed['Date'].unique())
        
        if len(available_dates) < 2:
            st.warning("⚠️ Need at least 2 different dates for comparison. Current data only contains dates from a single day.")
            st.info("💡 This feature will be most useful when you have historical data spanning multiple days/weeks.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            date1 = st.date_input(
                "📅 Select First Date (Baseline)",
                value=available_dates[0],
                min_value=available_dates[0],
                max_value=available_dates[-1],
                key="date1"
            )
        
        with col2:
            date2 = st.date_input(
                "📅 Select Second Date (Comparison)",
                value=available_dates[-1],
                min_value=available_dates[0],
                max_value=available_dates[-1],
                key="date2"
            )
        
        if date1 == date2:
            st.warning("⚠️ Please select two different dates for comparison.")
            return
        
        # Filter data for selected dates
        data1 = df_processed[df_processed['Date'] == date1].copy()
        data2 = df_processed[df_processed['Date'] == date2].copy()
        
        if data1.empty or data2.empty:
            st.error("❌ No data found for one or both selected dates.")
            return
        
        # Perform comparison
        st.markdown(f'<h3 class="section-header">📊 Comparison Results: {date1} vs {date2}</h3>', unsafe_allow_html=True)
        
        # Merge data for comparison
        comparison_data = []
        
        # Get all unique keywords from both dates
        all_keywords = set(data1['Keyword_Clean'].unique()) | set(data2['Keyword_Clean'].unique())
        
        for keyword in all_keywords:
            kw_data1 = data1[data1['Keyword_Clean'] == keyword]
            kw_data2 = data2[data2['Keyword_Clean'] == keyword]
            
            pos1 = kw_data1['Recharge Position'].iloc[0] if not kw_data1.empty else 'Not Ranking'
            pos2 = kw_data2['Recharge Position'].iloc[0] if not kw_data2.empty else 'Not Ranking'
            
            ai1 = kw_data1['AI Overview'].iloc[0] if not kw_data1.empty else 'No'
            ai2 = kw_data2['AI Overview'].iloc[0] if not kw_data2.empty else 'No'
            
            market = kw_data1['Market'].iloc[0] if not kw_data1.empty else (kw_data2['Market'].iloc[0] if not kw_data2.empty else 'Unknown')
            
            change_val, change_desc = calculate_position_change(pos1, pos2)
            
            # AI Overview change
            ai_change = ""
            if str(ai1).lower() in ['yes', 'y', 'true'] and str(ai2).lower() not in ['yes', 'y', 'true']:
                ai_change = "Lost AI Overview"
            elif str(ai1).lower() not in ['yes', 'y', 'true'] and str(ai2).lower() in ['yes', 'y', 'true']:
                ai_change = "Gained AI Overview"
            elif str(ai1).lower() in ['yes', 'y', 'true'] and str(ai2).lower() in ['yes', 'y', 'true']:
                ai_change = "AI Overview maintained"
            else:
                ai_change = "No AI Overview"
            
            comparison_data.append({
                'Keyword': keyword,
                'Market': market,
                'Position_Date1': pos1,
                'Position_Date2': pos2,
                'Change_Value': change_val,
                'Change_Description': change_desc,
                'AI_Date1': ai1,
                'AI_Date2': ai2,
                'AI_Change': ai_change
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            improved = len(comparison_df[comparison_df['Change_Value'] > 0])
            st.metric("📈 Improved Rankings", improved, f"{improved/len(comparison_df)*100:.1f}% of keywords")
        
        with col2:
            declined = len(comparison_df[comparison_df['Change_Value'] < 0])
            st.metric("📉 Declined Rankings", declined, f"{declined/len(comparison_df)*100:.1f}% of keywords")
        
        with col3:
            new_rankings = len(comparison_df[comparison_df['Change_Value'] == float('inf')])
            st.metric("🆕 New Rankings", new_rankings)
        
        with col4:
            lost_rankings = len(comparison_df[comparison_df['Change_Value'] == float('-inf')])
            st.metric("❌ Lost Rankings", lost_rankings)
        
        # AI Overview changes
        st.markdown('<h3 class="section-header">🤖 AI Overview Changes</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            gained_ai = len(comparison_df[comparison_df['AI_Change'] == 'Gained AI Overview'])
            st.metric("🤖 Gained AI Overview", gained_ai)
        
        with col2:
            lost_ai = len(comparison_df[comparison_df['AI_Change'] == 'Lost AI Overview'])
            st.metric("🚫 Lost AI Overview", lost_ai)
        
        # Detailed comparison table
        st.markdown('<h3 class="section-header">📋 Detailed Comparison Table</h3>', unsafe_allow_html=True)
        
        # Sort by change value (most improved first)
        comparison_df_sorted = comparison_df.sort_values('Change_Value', ascending=False)
        
        # Color-code the changes
        def style_changes(row):
            if row['Change_Value'] == float('inf'):
                return ['background-color: #ecfdf5'] * len(row)
            elif row['Change_Value'] == float('-inf'):
                return ['background-color: #fef2f2'] * len(row)
            elif row['Change_Value'] > 0:
                return ['background-color: #f0fdf4'] * len(row)
            elif row['Change_Value'] < 0:
                return ['background-color: #fefcfc'] * len(row)
            else:
                return ['background-color: white'] * len(row)
        
        # Display styled dataframe
        display_df = comparison_df_sorted[['Keyword', 'Market', 'Position_Date1', 'Position_Date2', 'Change_Description', 'AI_Change']].copy()
        display_df.columns = ['Keyword', 'Market', f'Position {date1}', f'Position {date2}', 'Change', 'AI Overview Change']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Visualization
        st.markdown('<h3 class="section-header">📊 Position Changes Visualization</h3>', unsafe_allow_html=True)
        
        # Filter out infinite values for visualization
        viz_data = comparison_df[
            (comparison_df['Change_Value'] != float('inf')) & 
            (comparison_df['Change_Value'] != float('-inf'))
        ].copy()
        
        if not viz_data.empty:
            fig = px.bar(
                viz_data.sort_values('Change_Value'),
                x='Change_Value',
                y='Keyword',
                orientation='h',
                title=f'Position Changes: {date1} → {date2}',
                labels={'Change_Value': 'Position Change (Positive = Improvement)', 'Keyword': 'Keywords'},
                color='Change_Value',
                color_continuous_scale=['red', 'white', 'green'],
                color_continuous_midpoint=0
            )
            
            fig.update_layout(
                height=max(400, len(viz_data) * 25),
                font_family="Inter",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export comparison results
        st.markdown('<h3 class="section-header">📥 Export Results</h3>', unsafe_allow_html=True)
        
        csv_data = comparison_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Comparison Results as CSV",
            data=csv_data,
            file_name=f"ranking_comparison_{date1}_vs_{date2}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.error("❌ No date information found in the data.")

# Main navigation and pages
def main():
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>🔋 RECHARGE.COM</h1>
        <h3>Advanced Ranking Tracker Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('🔄 Loading data from Google Sheets...'):
        df = load_data_from_sheets()
    
    if df.empty:
        st.warning("⚠️ No data found. Please check your Google Sheets connection.")
        return
    
    # Process data
    df_processed = df.copy()
    df_processed[['Keyword_Clean', 'Language', 'Location']] = df_processed['Sheet_Name'].apply(
        lambda x: pd.Series(parse_sheet_info(x))
    )
    df_processed['Market'] = df_processed['Location'].apply(get_country_flag)
    
    # Convert datetime
    if 'Date/Time' in df_processed.columns:
        df_processed['DateTime'] = pd.to_datetime(df_processed['Date/Time'], errors='coerce')
        latest_data = df_processed.sort_values('DateTime').groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    else:
        latest_data = df_processed.groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    
    # Sidebar Navigation
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; color: white;'>
        <h2 style='color: white; margin: 0;'>🎛️ Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard Overview", "📈 Keyword Tracking", "🤖 AI Overview Analysis", "📅 Date Comparison", "🔍 Detailed Reports"],
        key="main_nav"
    )
    
    # Filters (always visible except for Date Comparison page)
    if page != "📅 Date Comparison":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Filters")
        
        # Market filter
        markets = ['All Markets'] + sorted(latest_data['Market'].unique().tolist())
        selected_market = st.sidebar.selectbox("🌍 Market", markets)
        
        # Position filter
        position_options = ['All Positions', 'Top 3 (1-3)', 'Positions 4-10', 'Not Ranking']
        selected_position = st.sidebar.selectbox("📍 Position Range", position_options)
        
        # AI Overview filter
        ai_options = ['All', 'With AI Overview', 'Without AI Overview']
        selected_ai = st.sidebar.selectbox("🤖 AI Overview Status", ai_options)
        
        # Apply filters
        filtered_data = latest_data.copy()
        
        if selected_market != 'All Markets':
            filtered_data = filtered_data[filtered_data['Market'] == selected_market]
        
        if 'Recharge Position' in filtered_data.columns:
            if selected_position == 'Top 3 (1-3)':
                filtered_data = filtered_data[
                    filtered_data['Recharge Position'].apply(
                        lambda x: isinstance(x, (int, float)) and 1 <= x <= 3
                    )
                ]
            elif selected_position == 'Positions 4-10':
                filtered_data = filtered_data[
                    filtered_data['Recharge Position'].apply(
                        lambda x: isinstance(x, (int, float)) and 4 <= x <= 10
                    )
                ]
            elif selected_position == 'Not Ranking':
                filtered_data = filtered_data[
                    filtered_data['Recharge Position'].apply(
                        lambda x: str(x).lower() in ['not ranking', 'lost', ''] or pd.isna(x)
                    )
                ]
        
        if 'AI Overview' in filtered_data.columns:
            if selected_ai == 'With AI Overview':
                filtered_data = filtered_data[filtered_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])]
            elif selected_ai == 'Without AI Overview':
                filtered_data = filtered_data[~filtered_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])]
    else:
        filtered_data = latest_data.copy()
    
    # Page routing
    if page == "📊 Dashboard Overview":
        show_dashboard_overview(latest_data, filtered_data)
    elif page == "📈 Keyword Tracking":
        show_keyword_tracking(df_processed, filtered_data)
    elif page == "🤖 AI Overview Analysis":
        show_ai_overview_analysis(df_processed, filtered_data)
    elif page == "📅 Date Comparison":
        show_date_comparison(df_processed)
    elif page == "🔍 Detailed Reports":
        show_detailed_reports(df_processed, filtered_data)

def show_dashboard_overview(latest_data, filtered_data):
    """Dashboard Overview Page"""
    st.markdown('<h2 class="section-header">📊 Key Performance Metrics</h2>', unsafe_allow_html=True)
    
    if 'Recharge Position' in latest_data.columns:
        total_keywords = len(latest_data)
        
        top_3 = len(latest_data[
            latest_data['Recharge Position'].apply(
                lambda x: isinstance(x, (int, float)) and 1 <= x <= 3
            )
        ])
        
        pos_4_10 = len(latest_data[
            latest_data['Recharge Position'].apply(
                lambda x: isinstance(x, (int, float)) and 4 <= x <= 10
            )
        ])
        
        not_ranking = len(latest_data[
            latest_data['Recharge Position'].apply(
                lambda x: str(x).lower() in ['not ranking', 'lost', ''] or pd.isna(x)
            )
        ])
        
        ai_count = len(latest_data[
            latest_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])
        ]) if 'AI Overview' in latest_data.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🟢 Top 3 Positions",
                value=top_3,
                delta=f"{(top_3/total_keywords*100):.1f}% of total" if total_keywords > 0 else None
            )
        
        with col2:
            st.metric(
                label="🟡 Positions 4-10",
                value=pos_4_10,
                delta=f"{(pos_4_10/total_keywords*100):.1f}% of total" if total_keywords > 0 else None
            )
        
        with col3:
            st.metric(
                label="🔴 Not Ranking",
                value=not_ranking,
                delta=f"{(not_ranking/total_keywords*100):.1f}% of total" if total_keywords > 0 else None
            )
        
        with col4:
            st.metric(
                label="🤖 AI Overviews",
                value=ai_count,
                delta=f"{(ai_count/total_keywords*100):.1f}% coverage" if total_keywords > 0 else None
            )
    
    # Quick Alerts
    st.markdown('<h2 class="section-header">🚨 Quick Alerts</h2>', unsafe_allow_html=True)
    
    # Lost rankings
    lost_keywords = filtered_data[
        filtered_data['Position Change'].str.contains('Lost', case=False, na=False)
    ] if 'Position Change' in filtered_data.columns else pd.DataFrame()
    
    if not lost_keywords.empty:
        st.markdown(
            f'<div class="alert-danger">⚠️ <strong>{len(lost_keywords)} keywords lost ranking!</strong> '
            f'{", ".join(lost_keywords["Keyword_Clean"].tolist()[:3])}{"..." if len(lost_keywords) > 3 else ""}</div>',
            unsafe_allow_html=True
        )
    
    # New AI Overviews
    new_ai = filtered_data[
        (filtered_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])) &
        (filtered_data['Position Change'].str.contains('New', case=False, na=False))
    ] if 'AI Overview' in filtered_data.columns else pd.DataFrame()
    
    if not new_ai.empty:
        st.markdown(
            f'<div class="alert-success">🤖 <strong>{len(new_ai)} new AI Overviews detected!</strong> '
            f'{", ".join(new_ai["Keyword_Clean"].tolist()[:3])}{"..." if len(new_ai) > 3 else ""}</div>',
            unsafe_allow_html=True
        )
    
    # Keywords Overview Table
    st.markdown('<h2 class="section-header">🔍 Keywords Overview</h2>', unsafe_allow_html=True)
    
    if not filtered_data.empty:
        display_data = filtered_data.copy()
        
        # Format data for display
        if 'Recharge Position' in display_data.columns:
            display_data['Position_Display'] = display_data['Recharge Position'].apply(
                lambda x: get_position_status(x)[0]
            )
        
        if 'Position Change' in display_data.columns:
            display_data['Trend'] = display_data['Position Change'].apply(get_trend_emoji)
            display_data['Change_Display'] = display_data['Trend'] + ' ' + display_data['Position Change'].fillna('')
        
        if 'AI Overview' in display_data.columns:
            display_data['AI_Display'] = display_data['AI Overview'].apply(
                lambda x: '🤖 Yes' if str(x).lower() in ['yes', 'y', 'true'] else '❌ No'
            )
        
        # Select columns for display
        display_columns = ['Keyword_Clean', 'Market', 'Position_Display', 'Change_Display', 'AI_Display']
        column_mapping = {
            'Keyword_Clean': 'Keyword',
            'Position_Display': 'Position',
            'Change_Display': 'Change',
            'AI_Display': 'AI Overview'
        }
        
        if all(col in display_data.columns for col in display_columns):
            table_data = display_data[display_columns].rename(columns=column_mapping)
            st.dataframe(table_data, use_container_width=True, hide_index=True)
        
        # Show Full Results Data for selected keywords
        st.markdown('<h3 class="section-header">📄 Full Results Data</h3>', unsafe_allow_html=True)
        
        if 'Full Results Data' in display_data.columns:
            selected_keyword = st.selectbox(
                "Select keyword to view full results:",
                display_data['Keyword_Clean'].unique()
            )
            
            if selected_keyword:
                keyword_data = display_data[display_data['Keyword_Clean'] == selected_keyword]
                if not keyword_data.empty:
                    full_results = keyword_data['Full Results Data'].iloc[0]
                    
                    with st.expander(f"📊 Full Results for '{selected_keyword}'", expanded=False):
                        st.text_area("Complete Search Results Data", full_results, height=300)
    
    # Charts
    st.markdown('<h2 class="section-header">📈 Analytics Overview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Position Distribution
        if 'Recharge Position' in latest_data.columns:
            position_counts = {
                'Top 3 (1-3)': len(latest_data[
                    latest_data['Recharge Position'].apply(
                        lambda x: isinstance(x, (int, float)) and 1 <= x <= 3
                    )
                ]),
                'Positions 4-10': len(latest_data[
                    latest_data['Recharge Position'].apply(
                        lambda x: isinstance(x, (int, float)) and 4 <= x <= 10
                    )
                ]),
                'Not Ranking': len(latest_data[
                    latest_data['Recharge Position'].apply(
                        lambda x: str(x).lower() in ['not ranking', 'lost', ''] or pd.isna(x)
                    )
                ])
            }
            
            fig_pie = px.pie(
                values=list(position_counts.values()),
                names=list(position_counts.keys()),
                title="Position Distribution",
                color_discrete_map={
                    'Top 3 (1-3)': '#166534',
                    'Positions 4-10': '#92400e',
                    'Not Ranking': '#dc2626'
                }
            )
            fig_pie.update_layout(height=400, font_family="Inter")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Market Performance
        if 'Market' in latest_data.columns and 'Recharge Position' in latest_data.columns:
            market_avg = latest_data.groupby('Market')['Recharge Position'].apply(
                lambda x: x[x.apply(lambda y: isinstance(y, (int, float)))].mean()
            ).reset_index()
            market_avg.columns = ['Market', 'Avg_Position']
            market_avg = market_avg.dropna()
            
            if not market_avg.empty:
                fig_bar = px.bar(
                    market_avg,
                    x='Market',
                    y='Avg_Position',
                    title="Average Position by Market",
                    color='Avg_Position',
                    color_continuous_scale=['#166534', '#92400e', '#dc2626']
                )
                fig_bar.update_layout(height=400, yaxis_title="Average Position", font_family="Inter")
                st.plotly_chart(fig_bar, use_container_width=True)

def show_keyword_tracking(df_processed, filtered_data):
    """Individual Keyword Tracking Page"""
    st.markdown('<h2 class="section-header">📈 Individual Keyword Performance</h2>', unsafe_allow_html=True)
    
    # Keyword selector
    available_keywords = df_processed['Keyword_Clean'].unique() if 'Keyword_Clean' in df_processed.columns else []
    
    if len(available_keywords) == 0:
        st.warning("No keywords found in the data.")
        return
    
    selected_keyword = st.selectbox(
        "🔍 Select keyword to analyze:",
        available_keywords,
        key="keyword_selector"
    )
    
    if selected_keyword:
        # Filter data for selected keyword
        keyword_data = df_processed[df_processed['Keyword_Clean'] == selected_keyword].copy()
        
        if 'DateTime' in keyword_data.columns:
            keyword_data = keyword_data.sort_values('DateTime')
        
        # Key metrics for this keyword
        col1, col2, col3, col4 = st.columns(4)
        
        if not keyword_data.empty:
            latest_row = keyword_data.iloc[-1]
            
            with col1:
                current_pos = latest_row.get('Recharge Position', 'Unknown')
                st.metric("Current Position", current_pos)
            
            with col2:
                change = latest_row.get('Position Change', 'Unknown')
                st.metric("Latest Change", change)
            
            with col3:
                market = latest_row.get('Market', 'Unknown')
                st.metric("Market", market)
            
            with col4:
                ai_status = latest_row.get('AI Overview', 'Unknown')
                ai_display = '🤖 Yes' if str(ai_status).lower() in ['yes', 'y', 'true'] else '❌ No'
                st.metric("AI Overview", ai_display)
        
        # Position tracking chart
        st.markdown('<h3 class="section-header">📊 Position History</h3>', unsafe_allow_html=True)
        
        if 'DateTime' in keyword_data.columns and 'Recharge Position' in keyword_data.columns:
            # Prepare data for plotting
            plot_data = keyword_data.copy()
            plot_data['Position_Numeric'] = plot_data['Recharge Position'].apply(
                lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else None
            )
            
            # Remove rows where position is not numeric
            plot_data = plot_data.dropna(subset=['Position_Numeric'])
            
            if not plot_data.empty:
                fig = px.line(
                    plot_data,
                    x='DateTime',
                    y='Position_Numeric',
                    title=f'Position Tracking for "{selected_keyword}"',
                    markers=True
                )
                
                # Invert y-axis (position 1 should be at top)
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=400,
                    font_family="Inter",
                    yaxis_title="Search Position",
                    xaxis_title="Date"
                )
                
                # Add horizontal lines for key thresholds
                fig.add_hline(y=3.5, line_dash="dash", line_color="green", 
                             annotation_text="Top 3 Threshold")
                fig.add_hline(y=10.5, line_dash="dash", line_color="orange", 
                             annotation_text="First Page Threshold")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric position data available for this keyword.")
        
        # AI Overview tracking
        st.markdown('<h3 class="section-header">🤖 AI Overview History</h3>', unsafe_allow_html=True)
        
        if 'AI Overview' in keyword_data.columns:
            ai_data = keyword_data[['DateTime', 'AI Overview', 'AIO Links']].copy() if 'DateTime' in keyword_data.columns else keyword_data[['AI Overview', 'AIO Links']].copy()
            ai_data['AI_Status'] = ai_data['AI Overview'].apply(
                lambda x: 1 if str(x).lower() in ['yes', 'y', 'true'] else 0
            )
            
            if 'DateTime' in ai_data.columns and not ai_data.empty:
                fig_ai = px.scatter(
                    ai_data,
                    x='DateTime',
                    y='AI_Status',
                    title=f'AI Overview Presence for "{selected_keyword}"',
                    color='AI_Status',
                    color_discrete_map={0: '#dc2626', 1: '#166534'}
                )
                
                fig_ai.update_layout(
                    height=300,
                    font_family="Inter",
                    yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No AI', 'AI Present']),
                    showlegend=False
                )
                
                st.plotly_chart(fig_ai, use_container_width=True)
        
        # Detailed history table
        st.markdown('<h3 class="section-header">📜 Complete History</h3>', unsafe_allow_html=True)
        
        with st.expander("View Complete Tracking History", expanded=False):
            if not keyword_data.empty:
                history_columns = ['DateTime', 'Recharge Position', 'Position Change', 'AI Overview']
                available_history_cols = [col for col in history_columns if col in keyword_data.columns]
                
                if available_history_cols:
                    st.dataframe(
                        keyword_data[available_history_cols].sort_values('DateTime', ascending=False) if 'DateTime' in available_history_cols else keyword_data[available_history_cols],
                        use_container_width=True,
                        hide_index=True
                    )

def show_ai_overview_analysis(df_processed, filtered_data):
    """AI Overview Analysis Page"""
    st.markdown('<h2 class="section-header">🤖 AI Overview Analysis</h2>', unsafe_allow_html=True)
    
    # AI Overview metrics
    if 'AI Overview' in df_processed.columns:
        total_searches = len(df_processed)
        ai_present = len(df_processed[df_processed['AI Overview'].str.lower().isin(['yes', 'y', 'true'])])
        ai_coverage = (ai_present / total_searches * 100) if total_searches > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Searches", total_searches)
        
        with col2:
            st.metric("AI Overviews Detected", ai_present)
        
        with col3:
            st.metric("AI Coverage Rate", f"{ai_coverage:.1f}%")
    
    # AI Overview by keyword
    st.markdown('<h3 class="section-header">📊 AI Overview by Keyword</h3>', unsafe_allow_html=True)
    
    if 'AI Overview' in df_processed.columns and 'Keyword_Clean' in df_processed.columns:
        ai_by_keyword = df_processed.groupby('Keyword_Clean')['AI Overview'].apply(
            lambda x: (x.str.lower().isin(['yes', 'y', 'true']).sum() / len(x) * 100)
        ).reset_index()
        ai_by_keyword.columns = ['Keyword', 'AI_Coverage_Percentage']
        ai_by_keyword = ai_by_keyword.sort_values('AI_Coverage_Percentage', ascending=False)
        
        fig_ai_keywords = px.bar(
            ai_by_keyword,
            x='Keyword',
            y='AI_Coverage_Percentage',
            title='AI Overview Coverage by Keyword',
            color='AI_Coverage_Percentage',
            color_continuous_scale=['#dc2626', '#166534']
        )
        fig_ai_keywords.update_layout(height=400, font_family="Inter", yaxis_title="Coverage %")
        st.plotly_chart(fig_ai_keywords, use_container_width=True)
    
    # AI Overview content viewer
    st.markdown('<h3 class="section-header">🔍 AI Overview Content</h3>', unsafe_allow_html=True)
    
    # Filter for keywords with AI Overview
    ai_keywords = filtered_data[
        filtered_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])
    ] if 'AI Overview' in filtered_data.columns else pd.DataFrame()
    
    if not ai_keywords.empty:
        selected_ai_keyword = st.selectbox(
            "Select keyword to view AI Overview content:",
            ai_keywords['Keyword_Clean'].unique(),
            key="ai_keyword_selector"
        )
        
        if selected_ai_keyword:
            ai_keyword_data = ai_keywords[ai_keywords['Keyword_Clean'] == selected_ai_keyword]
            
            if not ai_keyword_data.empty:
                latest_ai_data = ai_keyword_data.iloc[-1]
                
                # Show AIO Links
                if 'AIO Links' in latest_ai_data and pd.notna(latest_ai_data['AIO Links']) and latest_ai_data['AIO Links']:
                    st.markdown("#### 🔗 AI Overview Source Links")
                    
                    aio_links = str(latest_ai_data['AIO Links']).split('\n')
                    for i, link in enumerate(aio_links, 1):
                        if link.strip():
                            st.markdown(f"**{i}.** [{link}]({link})")
                
                # Show Full Results Data with AI content
                if 'Full Results Data' in latest_ai_data and pd.notna(latest_ai_data['Full Results Data']):
                    with st.expander(f"📄 Complete AI Overview Data for '{selected_ai_keyword}'", expanded=True):
                        st.text_area(
                            "Full AI Overview Results",
                            latest_ai_data['Full Results Data'],
                            height=400,
                            key=f"ai_content_{selected_ai_keyword}"
                        )
    else:
        st.info("No AI Overviews found with current filters.")
    
    # AI Overview trends over time
    st.markdown('<h3 class="section-header">📈 AI Overview Trends</h3>', unsafe_allow_html=True)
    
    if 'DateTime' in df_processed.columns and 'AI Overview' in df_processed.columns:
        # Group by date and calculate AI percentage
        df_processed['Date'] = df_processed['DateTime'].dt.date
        ai_trends = df_processed.groupby('Date').agg({
            'AI Overview': lambda x: (x.str.lower().isin(['yes', 'y', 'true']).sum() / len(x) * 100)
        }).reset_index()
        ai_trends.columns = ['Date', 'AI_Percentage']
        
        if not ai_trends.empty:
            fig_ai_trends = px.line(
                ai_trends,
                x='Date',
                y='AI_Percentage',
                title='AI Overview Detection Rate Over Time',
                markers=True
            )
            fig_ai_trends.update_layout(height=400, font_family="Inter", yaxis_title="AI Detection Rate (%)")
            st.plotly_chart(fig_ai_trends, use_container_width=True)

def show_detailed_reports(df_processed, filtered_data):
    """Detailed Reports Page"""
    st.markdown('<h2 class="section-header">🔍 Detailed Analysis Reports</h2>', unsafe_allow_html=True)
    
    # Report type selector
    report_type = st.selectbox(
        "📊 Select Report Type:",
        ["📈 Position Movement Report", "🤖 AI Overview Report", "🌍 Market Analysis", "📋 Full Data Export"],
        key="report_selector"
    )
    
    if report_type == "📈 Position Movement Report":
        st.markdown('<h3 class="section-header">Position Movement Analysis</h3>', unsafe_allow_html=True)
        
        # Position changes summary
        if 'Position Change' in filtered_data.columns:
            change_summary = filtered_data['Position Change'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_changes = px.pie(
                    values=change_summary.values,
                    names=change_summary.index,
                    title="Position Changes Distribution"
                )
                st.plotly_chart(fig_changes, use_container_width=True)
            
            with col2:
                st.markdown("#### Recent Position Changes")
                st.dataframe(change_summary.to_frame('Count'), use_container_width=True)
        
        # Keywords with significant changes
        significant_changes = filtered_data[
            filtered_data['Position Change'].str.contains('Improved|Declined', case=False, na=False)
        ] if 'Position Change' in filtered_data.columns else pd.DataFrame()
        
        if not significant_changes.empty:
            st.markdown("#### Keywords with Significant Changes")
            st.dataframe(
                significant_changes[['Keyword_Clean', 'Market', 'Recharge Position', 'Position Change']],
                use_container_width=True,
                hide_index=True
            )
    
    elif report_type == "🤖 AI Overview Report":
        st.markdown('<h3 class="section-header">AI Overview Detailed Report</h3>', unsafe_allow_html=True)
        
        # AI Overview summary table
        if 'AI Overview' in filtered_data.columns:
            ai_summary = filtered_data.groupby(['Keyword_Clean', 'Market']).agg({
                'AI Overview': lambda x: 'Yes' if any(x.str.lower().isin(['yes', 'y', 'true'])) else 'No',
                'AIO Links': 'last',
                'Recharge Position': 'last'
            }).reset_index()
            
            st.dataframe(ai_summary, use_container_width=True, hide_index=True)
            
            # AI content for each keyword
            st.markdown("#### AI Overview Content Details")
            
            for keyword in ai_summary[ai_summary['AI Overview'] == 'Yes']['Keyword_Clean'].unique():
                keyword_ai_data = filtered_data[
                    (filtered_data['Keyword_Clean'] == keyword) & 
                    (filtered_data['AI Overview'].str.lower().isin(['yes', 'y', 'true']))
                ]
                
                if not keyword_ai_data.empty:
                    with st.expander(f"🤖 AI Content for '{keyword}'"):
                        latest_data = keyword_ai_data.iloc[-1]
                        
                        if 'AIO Links' in latest_data and pd.notna(latest_data['AIO Links']):
                            st.markdown("**Source Links:**")
                            for link in str(latest_data['AIO Links']).split('\n'):
                                if link.strip():
                                    st.markdown(f"- {link}")
                        
                        if 'Full Results Data' in latest_data and pd.notna(latest_data['Full Results Data']):
                            st.text_area(
                                "Full AI Overview Data",
                                latest_data['Full Results Data'],
                                height=200,
                                key=f"detailed_ai_{keyword}"
                            )
    
    elif report_type == "🌍 Market Analysis":
        st.markdown('<h3 class="section-header">Market Performance Analysis</h3>', unsafe_allow_html=True)
        
        if 'Market' in filtered_data.columns:
            for market in filtered_data['Market'].unique():
                market_data = filtered_data[filtered_data['Market'] == market]
                
                with st.expander(f"📊 {market} Analysis"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_keywords = len(market_data)
                        st.metric("Total Keywords", total_keywords)
                    
                    with col2:
                        if 'Recharge Position' in market_data.columns:
                            avg_pos = market_data['Recharge Position'].apply(
                                lambda x: x if isinstance(x, (int, float)) else None
                            ).mean()
                            st.metric("Avg Position", f"{avg_pos:.1f}" if pd.notna(avg_pos) else "N/A")
                    
                    with col3:
                        if 'AI Overview' in market_data.columns:
                            ai_count = len(market_data[market_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])])
                            st.metric("AI Coverage", f"{(ai_count/total_keywords*100):.1f}%")
                    
                    # Market-specific keyword table
                    st.dataframe(
                        market_data[['Keyword_Clean', 'Recharge Position', 'Position Change', 'AI Overview']],
                        use_container_width=True,
                        hide_index=True
                    )
    
    elif report_type == "📋 Full Data Export":
        st.markdown('<h3 class="section-header">Complete Data Export</h3>', unsafe_allow_html=True)
        
        st.info("📥 Use the options below to view and export complete data")
        
        # Full data viewer
        with st.expander("📊 View Complete Dataset", expanded=False):
            st.dataframe(filtered_data, use_container_width=True, hide_index=True)
        
        # Export options
        if not filtered_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"recharge_ranking_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Summary statistics
                st.markdown("#### 📈 Data Summary")
                st.write(f"Total Records: {len(filtered_data)}")
                st.write(f"Date Range: {filtered_data['DateTime'].min()} to {filtered_data['DateTime'].max()}" if 'DateTime' in filtered_data.columns else "Date info not available")
                st.write(f"Unique Keywords: {filtered_data['Keyword_Clean'].nunique()}" if 'Keyword_Clean' in filtered_data.columns else "Keyword info not available")

if __name__ == "__main__":
    main()
