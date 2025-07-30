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
    initial_sidebar_state="expanded"  # Sidebar open by default
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
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.75rem;
    }
    
    .streamlit-expanderContent {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    
    .status-top3 {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-mid {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-poor {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .status-ai {
        background: #dbeafe;
        color: #1d4ed8;
    }
    
    /* Navigation */
    .nav-pills {
        background: #f1f5f9;
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    /* Charts */
    .plotly-graph-div {
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
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
</style>
""", unsafe_allow_html=True)

# Google Sheets connection
@st.cache_data(ttl=300)
def load_data_from_sheets():
    """Load data from Google Sheets"""
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        
        gc = gspread.authorize(credentials)
        sheet_url = "https://docs.google.com/spreadsheets/d/1hOMEaZ_zfliPxJ7N-9EJ64KvyRl9J-feoR30GB-bI_o/edit"
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
                st.error(f"Error reading sheet {sheet.title}: {e}")
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return get_sample_data()

def get_sample_data():
    """Sample data for demo purposes"""
    dates = pd.date_range('2024-01-01', periods=30, freq='8H')
    sample_data = []
    
    keywords = [
        ('recarga digi', 'es', 'es'),
        ('ricarica iliad', 'it', 'it'),
        ('recharge transcash', 'fr', 'fr'),
        ('buy robux', 'en', 'ph'),
        ('neosurf voucher', 'en', 'au')
    ]
    
    for date in dates:
        for keyword, lang, loc in keywords:
            pos = np.random.randint(1, 15)
            sample_data.append({
                'Date/Time': date.strftime('%Y-%m-%d %H:%M'),
                'Keyword': keyword,
                'Position 1': f'https://example1.com/{keyword.replace(" ", "-")}',
                'Position 2': f'https://example2.com/{keyword.replace(" ", "-")}',
                'Position 3': f'https://example3.com/{keyword.replace(" ", "-")}',
                'Position 4': f'https://example4.com/{keyword.replace(" ", "-")}',
                'Position 5': f'https://example5.com/{keyword.replace(" ", "-")}',
                'Recharge URL': 'https://www.recharge.com/es/es/digimobil' if pos <= 10 else '',
                'Recharge Position': pos if pos <= 10 else 'Not Ranking',
                'Position Change': np.random.choice(['Improved (+1)', 'Declined (-1)', 'Stable', 'New']),
                'AI Overview': np.random.choice(['Yes', 'No'], p=[0.3, 0.7]),
                'AIO Links': 'https://example.com/ai1\nhttps://example.com/ai2' if np.random.choice([True, False], p=[0.3, 0.7]) else '',
                'Full Results Data': f'Complete search results for {keyword} including all metadata and competitor analysis...',
                'Sheet_Name': f'{keyword.replace(" ", "_")}_{lang}_{loc}'
            })
    
    return pd.DataFrame(sample_data)

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
        st.error("❌ No data found. Please check your Google Sheets connection.")
        st.info("🔧 Troubleshooting steps:")
        st.write("1. Verify your Google Sheets API credentials are correct")
        st.write("2. Check that your service account has access to the spreadsheet")
        st.write("3. Ensure your keyword sheets have data")
        st.write("4. Confirm your automation script is running and adding data")
        return
    
    # Process data
    df_processed = df.copy()
    
    # Extract keyword, language, location from sheet names
    df_processed[['Keyword_Clean', 'Language', 'Location']] = df_processed['Sheet_Name'].apply(
        lambda x: pd.Series(parse_sheet_info(x))
    )
    df_processed['Market'] = df_processed['Location'].apply(get_country_flag)
    
    # Show data processing info
    st.info(f"📊 Data Processing Summary:")
    st.write(f"• Total records: {len(df_processed)}")
    st.write(f"• Unique keywords: {df_processed['Keyword_Clean'].nunique()}")
    st.write(f"• Unique markets: {df_processed['Market'].nunique()}")
    st.write(f"• Keywords found: {sorted(df_processed['Keyword_Clean'].unique().tolist())}")
    
    # Convert datetime
    if 'Date/Time' in df_processed.columns:
        df_processed['DateTime'] = pd.to_datetime(df_processed['Date/Time'], errors='coerce')
        # Get latest data for each keyword (most recent timestamp)
        latest_data = df_processed.sort_values('DateTime').groupby(['Keyword_Clean', 'Market']).tail(1).reset_index(drop=True)
        st.write(f"• Latest data points: {len(latest_data)}")
    else:
        # If no datetime, get the last row for each keyword
        latest_data = df_processed.groupby(['Keyword_Clean', 'Market']).tail(1).reset_index(drop=True)
        st.write(f"• Data points (no datetime): {len(latest_data)}")
    
    # Show which keywords we have in latest data
    st.write(f"• Keywords in latest data: {sorted(latest_data['Keyword_Clean'].unique().tolist())}")
    
    # Debug info about sheet names
    if st.checkbox("🔍 Show debug info about sheet processing"):
        sheet_debug = df_processed[['Sheet_Name', 'Keyword_Clean', 'Language', 'Location', 'Market']].drop_duplicates()
        st.dataframe(sheet_debug, use_container_width=True)
    
    st.markdown("---")
    
    # Sidebar Navigation
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; color: white;'>
        <h2 style='color: white; margin: 0;'>🎛️ Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard Overview", "📈 Keyword Tracking", "🤖 AI Overview Analysis", "🔍 Detailed Reports"],
        key="main_nav"
    )
    
    # Filters (always visible)
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
    
    # Time filter
    if 'DateTime' in df_processed.columns:
        date_range = st.sidebar.selectbox(
            "📅 Time Period",
            ['Last 7 days', 'Last 30 days', 'Last 90 days', 'All time']
        )
    
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
    
    # Page routing
    if page == "📊 Dashboard Overview":
        show_dashboard_overview(latest_data, filtered_data)
    elif page == "📈 Keyword Tracking":
        show_keyword_tracking(df_processed, filtered_data)
    elif page == "🤖 AI Overview Analysis":
        show_ai_overview_analysis(df_processed, filtered_data)
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
    
    # Show all available keywords from the full dataset, not just filtered
    all_keywords = sorted(df_processed['Keyword_Clean'].unique()) if 'Keyword_Clean' in df_processed.columns else []
    
    if len(all_keywords) == 0:
        st.warning("❌ No keywords found in the data.")
        st.info("📋 Make sure your Google Sheets have data and the script is running.")
        return
    
    st.success(f"📊 Found {len(all_keywords)} keywords total")
    
    # Keyword selector - show ALL keywords
    selected_keyword = st.selectbox(
        "🔍 Select keyword to analyze:",
        all_keywords,
        key="keyword_selector_tracking"
    )
    
    if selected_keyword:
        # Filter data for selected keyword from full dataset
        keyword_data = df_processed[df_processed['Keyword_Clean'] == selected_keyword].copy()
        
        if keyword_data.empty:
            st.error(f"❌ No data found for keyword: {selected_keyword}")
            return
        
        st.info(f"📈 Found {len(keyword_data)} records for '{selected_keyword}'")
        
        if 'DateTime' in keyword_data.columns:
            keyword_data = keyword_data.sort_values('DateTime')
            
        # Show latest data point info
        if not keyword_data.empty:
            latest_row = keyword_data.iloc[-1]
            
            # Key metrics for this keyword
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_pos = latest_row.get('Recharge Position', 'Unknown')
                st.metric("📍 Current Position", current_pos)
            
            with col2:
                change = latest_row.get('Position Change', 'Unknown')
                st.metric("📊 Latest Change", change)
            
            with col3:
                market = latest_row.get('Market', 'Unknown')
                st.metric("🌍 Market", market)
            
            with col4:
                ai_status = latest_row.get('AI Overview', 'Unknown')
                ai_display = '🤖 Yes' if str(ai_status).lower() in ['yes', 'y', 'true'] else '❌ No'
                st.metric("🤖 AI Overview", ai_display)
        
        # Position tracking chart
        st.markdown('<h3 class="section-header">📊 Position History</h3>', unsafe_allow_html=True)
        
        if 'DateTime' in keyword_data.columns and 'Recharge Position' in keyword_data.columns:
            # Prepare data for plotting
            plot_data = keyword_data.copy()
            plot_data['Position_Numeric'] = plot_data['Recharge Position'].apply(
                lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) and str(x).isdigit() else None
            )
            
            # Remove rows where position is not numeric
            plot_data_clean = plot_data.dropna(subset=['Position_Numeric'])
            
            if not plot_data_clean.empty:
                fig = px.line(
                    plot_data_clean,
                    x='DateTime',
                    y='Position_Numeric',
                    title=f'Position Tracking for "{selected_keyword}"',
                    markers=True,
                    line_shape='linear'
                )
                
                # Invert y-axis (position 1 should be at top)
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=400,
                    font_family="Inter",
                    yaxis_title="Search Position",
                    xaxis_title="Date & Time"
                )
                
                # Add horizontal lines for key thresholds
                fig.add_hline(y=3.5, line_dash="dash", line_color="green", 
                             annotation_text="Top 3 Threshold")
                fig.add_hline(y=10.5, line_dash="dash", line_color="orange", 
                             annotation_text="First Page Threshold")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show position data summary
                st.info(f"📊 Position data points: {len(plot_data_clean)} out of {len(plot_data)} total records")
                
            else:
                st.warning("⚠️ No numeric position data available for this keyword.")
                
                # Show what data we do have
                if 'Recharge Position' in keyword_data.columns:
                    position_values = keyword_data['Recharge Position'].value_counts()
                    st.write("📋 Position values found:")
                    st.dataframe(position_values.to_frame('Count'))
        
        # AI Overview tracking
        st.markdown('<h3 class="section-header">🤖 AI Overview History</h3>', unsafe_allow_html=True)
        
        if 'AI Overview' in keyword_data.columns:
            ai_columns = ['AI Overview']
            if 'DateTime' in keyword_data.columns:
                ai_columns.insert(0, 'DateTime')
            if 'AIO Links' in keyword_data.columns:
                ai_columns.append('AIO Links')
                
            ai_data = keyword_data[ai_columns].copy()
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
                
                # AI Overview summary
                ai_count = ai_data['AI_Status'].sum()
                total_checks = len(ai_data)
                ai_percentage = (ai_count / total_checks * 100) if total_checks > 0 else 0
                st.info(f"🤖 AI Overview detected in {ai_count} out of {total_checks} checks ({ai_percentage:.1f}%)")
        
        # Detailed history table
        st.markdown('<h3 class="section-header">📜 Complete History</h3>', unsafe_allow_html=True)
        
        with st.expander("📊 View Complete Tracking History", expanded=False):
            if not keyword_data.empty:
                # Show relevant columns
                display_columns = []
                column_mapping = {}
                
                if 'DateTime' in keyword_data.columns:
                    display_columns.append('DateTime')
                    column_mapping['DateTime'] = 'Date & Time'
                
                important_cols = ['Recharge Position', 'Position Change', 'AI Overview', 'Market']
                for col in important_cols:
                    if col in keyword_data.columns:
                        display_columns.append(col)
                        
                if display_columns:
                    history_df = keyword_data[display_columns].copy()
                    if 'DateTime' in history_df.columns:
                        history_df = history_df.sort_values('DateTime', ascending=False)
                    
                    st.dataframe(
                        history_df.rename(columns=column_mapping),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Export option
                    csv_data = history_df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {selected_keyword} history as CSV",
                        data=csv_data,
                        file_name=f"{selected_keyword}_history_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

def show_ai_overview_analysis(df_processed, filtered_data):
    """AI Overview Analysis Page"""
    st.markdown('<h2 class="section-header">🤖 AI Overview Analysis</h2>', unsafe_allow_html=True)
    
    # Use full dataset for AI analysis
    full_ai_data = df_processed.copy() if not df_processed.empty else filtered_data.copy()
    
    # AI Overview metrics
    if 'AI Overview' in full_ai_data.columns:
        total_searches = len(full_ai_data)
        ai_present = len(full_ai_data[full_ai_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])])
        ai_coverage = (ai_present / total_searches * 100) if total_searches > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total Searches", total_searches)
        
        with col2:
            st.metric("🤖 AI Overviews Detected", ai_present)
        
        with col3:
            st.metric("📈 AI Coverage Rate", f"{ai_coverage:.1f}%")
    
    # AI Overview by keyword (use full dataset)
    st.markdown('<h3 class="section-header">📊 AI Overview by Keyword</h3>', unsafe_allow_html=True)
    
    if 'AI Overview' in full_ai_data.columns and 'Keyword_Clean' in full_ai_data.columns:
        ai_by_keyword = full_ai_data.groupby('Keyword_Clean')['AI Overview'].apply(
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
        
        # Show the data table too
        st.dataframe(ai_by_keyword, use_container_width=True, hide_index=True)
    
    # AI Overview content viewer (use filtered data for user selection)
    st.markdown('<h3 class="section-header">🔍 AI Overview Content</h3>', unsafe_allow_html=True)
    
    # Get all keywords with AI Overview from full dataset
    all_ai_keywords = full_ai_data[
        full_ai_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])
    ] if 'AI Overview' in full_ai_data.columns else pd.DataFrame()
    
    if not all_ai_keywords.empty:
        unique_ai_keywords = sorted(all_ai_keywords['Keyword_Clean'].unique())
        
        selected_ai_keyword = st.selectbox(
            "🔍 Select keyword to view AI Overview content:",
            unique_ai_keywords,
            key="ai_keyword_selector"
        )
        
        if selected_ai_keyword:
            # Get the most recent AI data for this keyword
            keyword_ai_data = all_ai_keywords[
                all_ai_keywords['Keyword_Clean'] == selected_ai_keyword
            ]
            
            if 'DateTime' in keyword_ai_data.columns:
                keyword_ai_data = keyword_ai_data.sort_values('DateTime', ascending=False)
            
            if not keyword_ai_data.empty:
                latest_ai_data = keyword_ai_data.iloc[0]  # Most recent
                
                # Show basic info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🌍 Market", latest_ai_data.get('Market', 'Unknown'))
                with col2:
                    st.metric("📍 Position", latest_ai_data.get('Recharge Position', 'Unknown'))
                with col3:
                    st.metric("📅 Last Check", 
                             latest_ai_data.get('DateTime', 'Unknown').strftime('%Y-%m-%d %H:%M') 
                             if pd.notna(latest_ai_data.get('DateTime')) else 'Unknown')
                
                # Show AIO Links
                if 'AIO Links' in latest_ai_data and pd.notna(latest_ai_data['AIO Links']) and latest_ai_data['AIO Links']:
                    st.markdown("#### 🔗 AI Overview Source Links")
                    
                    aio_links = str(latest_ai_data['AIO Links']).split('\n')
                    for i, link in enumerate(aio_links, 1):
                        if link.strip():
                            if link.startswith('http'):
                                st.markdown(f"**{i}.** [{link}]({link})")
                            else:
                                st.markdown(f"**{i}.** {link}")
                
                # Show Full Results Data with AI content
                if 'Full Results Data' in latest_ai_data and pd.notna(latest_ai_data['Full Results Data']):
                    with st.expander(f"📄 Complete AI Overview Data for '{selected_ai_keyword}'", expanded=True):
                        st.text_area(
                            "Full AI Overview Results",
                            str(latest_ai_data['Full Results Data']),
                            height=400,
                            key=f"ai_content_{selected_ai_keyword}"
                        )
                
                # Show historical AI data for this keyword
                if len(keyword_ai_data) > 1:
                    st.markdown("#### 📈 AI Overview History")
                    
                    history_cols = ['DateTime', 'AI Overview', 'Recharge Position']
                    available_cols = [col for col in history_cols if col in keyword_ai_data.columns]
                    
                    if available_cols:
                        st.dataframe(
                            keyword_ai_data[available_cols],
                            use_container_width=True,
                            hide_index=True
                        )
    else:
        st.info("❌ No AI Overviews found in the current data.")
        st.write("💡 AI Overviews may appear when:")
        st.write("• The query triggers Google's AI response")
        st.write("• The search is informational rather than navigational")
        st.write("• Google has sufficient information to generate an overview")
    
    # AI Overview trends over time
    st.markdown('<h3 class="section-header">📈 AI Overview Trends</h3>', unsafe_allow_html=True)
    
    if 'DateTime' in full_ai_data.columns and 'AI Overview' in full_ai_data.columns:
        # Group by date and calculate AI percentage
        full_ai_data['Date'] = pd.to_datetime(full_ai_data['DateTime']).dt.date
        ai_trends = full_ai_data.groupby('Date').agg({
            'AI Overview': lambda x: (x.str.lower().isin(['yes', 'y', 'true']).sum() / len(x) * 100)
        }).reset_index()
        ai_trends.columns = ['Date', 'AI_Percentage']
        
        if not ai_trends.empty and len(ai_trends) > 1:
            fig_ai_trends = px.line(
                ai_trends,
                x='Date',
                y='AI_Percentage',
                title='AI Overview Detection Rate Over Time',
                markers=True
            )
            fig_ai_trends.update_layout(height=400, font_family="Inter", yaxis_title="AI Detection Rate (%)")
            st.plotly_chart(fig_ai_trends, use_container_width=True)
        else:
            st.info("📊 Not enough data points to show trends over time.")

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
