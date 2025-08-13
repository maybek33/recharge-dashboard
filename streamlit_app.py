import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import numpy as np
import re
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="Recharge.com SEO Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS styling
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark theme styling */
    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .dashboard-header {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .dashboard-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
    }
    
    .dashboard-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        color: #cbd5e1;
    }
    
    /* Card styling */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        border-color: #475569;
    }
    
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #f8fafc;
    }
    
    .metric-label {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        color: #cbd5e1;
        font-weight: 500;
    }
    
    .metric-change {
        font-size: 0.9rem;
        margin: 0.25rem 0 0 0;
        font-weight: 600;
    }
    
    .positive { color: #22c55e; }
    .negative { color: #ef4444; }
    .neutral { color: #f59e0b; }
    
    /* Section styling */
    .section-title {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 2rem 0 1rem 0;
        color: #f8fafc;
        font-size: 1.3rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #1e293b !important;
        border-right: 1px solid #334155;
    }
    
    .css-1d391kg .stMarkdown {
        color: #f8fafc !important;
    }
    
    .css-1d391kg .stRadio > label {
        color: #f8fafc !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: #374151;
        color: #f8fafc;
        border: 1px solid #4b5563;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #4b5563;
        border-color: #6b7280;
    }
    
    /* Chart container */
    .chart-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* SERP Result Styling */
    .serp-column {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
    }
    
    .serp-header {
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #334155;
        color: #f8fafc;
    }
    
    .serp-result {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        padding: 1rem;
        background: #0f172a;
        border-radius: 8px;
        border-left: 4px solid #64748b;
        transition: all 0.2s ease;
    }
    
    .serp-result:hover {
        background: #1e293b;
        transform: translateX(3px);
    }
    
    .serp-result.recharge {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .serp-result.improved {
        border-left-color: #22c55e;
        background: rgba(34, 197, 94, 0.1);
    }
    
    .serp-result.declined {
        border-left-color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .serp-result.new {
        border-left-color: #3b82f6;
        background: rgba(59, 130, 246, 0.1);
    }
    
    .position-number {
        min-width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        font-size: 14px;
        color: white;
        background: #64748b;
    }
    
    .result-content {
        flex: 1;
    }
    
    .result-title {
        font-weight: 600;
        margin-bottom: 0.3rem;
        color: #f8fafc;
        font-size: 0.95rem;
        line-height: 1.3;
    }
    
    .result-url {
        font-size: 0.8rem;
        color: #94a3b8;
        word-break: break-all;
        margin-bottom: 0.3rem;
    }
    
    .result-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-top: 0.3rem;
        margin-right: 0.3rem;
    }
    
    .badge-recharge {
        background: #f59e0b;
        color: white;
    }
    
    .badge-improved {
        background: #22c55e;
        color: white;
    }
    
    .badge-declined {
        background: #ef4444;
        color: white;
    }
    
    .badge-new {
        background: #3b82f6;
        color: white;
    }
    
    /* Streamlit specific overrides for dark theme */
    .stSelectbox > div > div > div {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
        color: #f8fafc !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #f8fafc !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
        color: #f8fafc !important;
    }
    
    .stDataFrame {
        background-color: #1e293b !important;
    }
    
    .stDataFrame [data-testid="stDataFrame"] {
        background-color: #1e293b !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background-color: transparent !important;
    }
    
    .stRadio > div > label {
        color: #f8fafc !important;
    }
    
    .stRadio > div > label > div > div {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
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
    return flag_map.get(location_code.lower(), f'{location_code.upper()}')

def get_position_status(position):
    """Get position status and color"""
    if pd.isna(position) or position == '' or str(position).lower() in ['not ranking', 'lost']:
        return 'Not Ranking', '#ef4444'
    try:
        pos = int(position)
        if pos <= 3:
            return f'#{pos}', '#22c55e'
        elif pos <= 10:
            return f'#{pos}', '#f59e0b'
        else:
            return f'#{pos}', '#ef4444'
    except:
        return str(position), '#64748b'

def has_ai_overview(ai_content):
    """Check if AI Overview content exists"""
    if pd.isna(ai_content) or not ai_content or str(ai_content) == '#ERROR!' or str(ai_content).strip() == '':
        return False
    return True

@st.cache_data(ttl=60)
def load_data_from_google_sheets():
    """Load data directly from the specified Google Sheets using GIDs from Main sheet"""
    
    sheet_id = "1hOMEaZ_zfliPxJ7N-9EJ64KvyRl9J-feoR30GB-bI_o"
    main_csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        # Read the main configuration sheet  
        main_df = pd.read_csv(main_csv_url)
        
        # Extract GIDs from column E
        gids_to_try = []
        keywords_info = []
        
        for index, row in main_df.iterrows():
            try:
                if len(row) > 4 and pd.notna(row.iloc[4]):
                    gid_text = str(row.iloc[4]).strip()
                    
                    if gid_text.startswith('GID:') or 'GID' in gid_text.upper():
                        gid_match = re.search(r'(\d+)', gid_text)
                        if gid_match:
                            gid = int(gid_match.group(1))
                            keyword = row.iloc[1] if pd.notna(row.iloc[1]) else f"Keyword_{index}"
                            gids_to_try.append(gid)
                            keywords_info.append({
                                'gid': gid,
                                'keyword': keyword,
                                'url': row.iloc[0] if pd.notna(row.iloc[0]) else '',
                                'language': row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else '',
                                'location': row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ''
                            })
            except Exception as e:
                continue
        
        if not gids_to_try:
            return pd.DataFrame()
        
        # Load keyword sheets
        all_keyword_data = []
        successful_sheets = 0
        
        for keyword_info in keywords_info:
            gid = keyword_info['gid']
            expected_keyword = keyword_info['keyword']
            
            try:
                keyword_csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                keyword_df = pd.read_csv(keyword_csv_url)
                
                if (not keyword_df.empty and 
                    'Date/Time' in keyword_df.columns and 
                    'Recharge Position' in keyword_df.columns):
                    
                    keyword_df['Sheet_Name'] = f"{expected_keyword}_{keyword_info['language']}_{keyword_info['location']}"
                    keyword_df['Sheet_GID'] = gid
                    keyword_df['Expected_Keyword'] = expected_keyword
                    keyword_df['Recharge_URL'] = keyword_info['url']
                    keyword_df['Market'] = get_country_flag(keyword_info['location'])
                    
                    all_keyword_data.append(keyword_df)
                    successful_sheets += 1
                    
            except Exception as e:
                continue
        
        if all_keyword_data:
            combined_df = pd.concat(all_keyword_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_llm_data():
    """Load LLM position tracking data from Excel file or Google Sheets"""
    
    try:
        # Try to load from local Excel file first
        try:
            df = pd.read_excel('a pos3.xlsx')
        except:
            # If local file not found, load from Google Sheets
            sheet_id = "1RMUPPVR02dWXt2a-lK_gAXhU1h7CS7l8GzZCBx-DvPA"
            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            df = pd.read_csv(sheet_url)
        
        # Process the data
        processed_data = []
        current_keyword = None
        current_time = None
        current_date = None
        current_country = None
        
        for idx, row in df.iterrows():
            # Skip empty rows or Start markers without keyword
            if pd.isna(row.get('Results')) or row.get('Results') == 'Start':
                if pd.notna(row.get('Keyword')):
                    current_keyword = row['Keyword']
                    current_time = row.get('Time')
                    current_date = row.get('Date')
                    current_country = row.get('Country')
                continue
            
            # If we have a URL in Results column
            if pd.notna(row.get('Results')) and row.get('Results') != 'Start':
                # Extract keyword, time, date, country for this row or use current values
                keyword = row['Keyword'] if pd.notna(row.get('Keyword')) else current_keyword
                time = row['Time'] if pd.notna(row.get('Time')) else current_time
                date = row['Date'] if pd.notna(row.get('Date')) else current_date
                country = row['Country'] if pd.notna(row.get('Country')) else current_country
                
                # Update current values if present in this row
                if pd.notna(row.get('Keyword')):
                    current_keyword = row['Keyword']
                if pd.notna(row.get('Time')):
                    current_time = row['Time']
                if pd.notna(row.get('Date')):
                    current_date = row['Date']
                if pd.notna(row.get('Country')):
                    current_country = row['Country']
                
                processed_data.append({
                    'Keyword': keyword,
                    'Time': time,
                    'Result_URL': row['Results'],
                    'Position': row.get('Position'),
                    'Date': date,
                    'Country': country
                })
        
        result_df = pd.DataFrame(processed_data)
        
        # Ensure Position is numeric
        if 'Position' in result_df.columns:
            result_df['Position'] = pd.to_numeric(result_df['Position'], errors='coerce')
        
        return result_df
        
    except Exception as e:
        st.error(f"Error loading LLM data: {str(e)}")
        return pd.DataFrame()

def parse_excel_datetime(date_val):
    """Parse datetime from various formats"""
    if pd.isna(date_val):
        return pd.NaT
    
    date_str = str(date_val).strip()
    
    # Try ISO format first
    try:
        result = pd.to_datetime(date_str, format='ISO8601', errors='coerce')
        if pd.notna(result):
            return result
    except:
        pass
    
    # Try standard parsing
    try:
        result = pd.to_datetime(date_str, infer_datetime_format=True, errors='coerce') 
        if pd.notna(result):
            return result
    except:
        pass
    
    # Try specific formats
    formats_to_try = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y, %I:%M:%S %p',
        '%m/%d/%Y %I:%M:%S %p',
    ]
    
    for fmt in formats_to_try:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    
    return pd.NaT

def create_metric_card(title, value, change=None, format_as_percent=False):
    """Create a metric card component"""
    change_class = ""
    change_text = ""
    
    if change is not None:
        if change > 0:
            change_class = "positive"
            change_text = f"↗ +{change}{'%' if format_as_percent else ''}"
        elif change < 0:
            change_class = "negative" 
            change_text = f"↘ {change}{'%' if format_as_percent else ''}"
        else:
            change_class = "neutral"
            change_text = "→ No change"
    
    return f"""
    <div class="metric-card">
        <div class="metric-number">{value}</div>
        <div class="metric-label">{title}</div>
        {f'<div class="metric-change {change_class}">{change_text}</div>' if change_text else ''}
    </div>
    """

def show_executive_dashboard(df_processed):
    """Executive-level dashboard view"""
    
    if df_processed.empty:
        st.error("No data available. Please check Google Sheets connectivity.")
        return
    
    # Process data
    df_processed['DateTime'] = df_processed['Date/Time'].apply(parse_excel_datetime)
    df_processed = df_processed.dropna(subset=['DateTime'])
    
    if df_processed.empty:
        st.error("No valid data found after processing.")
        return
    
    # Get latest data for each keyword
    latest_data = df_processed.sort_values('DateTime').groupby('Keyword').tail(1).reset_index(drop=True)
    
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🔋 Recharge.com SEO Performance</h1>
        <p>Search ranking intelligence for global markets</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_keywords = len(latest_data)
    top_3 = len(latest_data[latest_data['Recharge Position'].apply(
        lambda x: isinstance(x, (int, float)) and 1 <= x <= 3
    )])
    
    first_page = len(latest_data[latest_data['Recharge Position'].apply(
        lambda x: isinstance(x, (int, float)) and 1 <= x <= 10
    )])
    
    ai_coverage = len(latest_data[latest_data['AI Overview'].apply(has_ai_overview)]) if 'AI Overview' in latest_data.columns else 0
    
    with col1:
        st.markdown(create_metric_card("Total Keywords", total_keywords), unsafe_allow_html=True)
    
    with col2:
        top_3_pct = round((top_3/total_keywords*100)) if total_keywords > 0 else 0
        st.markdown(create_metric_card("Top 3 Positions", f"{top_3} ({top_3_pct}%)"), unsafe_allow_html=True)
    
    with col3:
        first_page_pct = round((first_page/total_keywords*100)) if total_keywords > 0 else 0
        st.markdown(create_metric_card("First Page", f"{first_page} ({first_page_pct}%)"), unsafe_allow_html=True)
    
    with col4:
        ai_pct = round((ai_coverage/total_keywords*100)) if total_keywords > 0 else 0
        st.markdown(create_metric_card("AI Overview", f"{ai_coverage} ({ai_pct}%)"), unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-title">📈 Performance Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Position Distribution Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        position_data = {
            'Top 3': len(latest_data[latest_data['Recharge Position'].apply(
                lambda x: isinstance(x, (int, float)) and 1 <= x <= 3
            )]),
            'Positions 4-10': len(latest_data[latest_data['Recharge Position'].apply(
                lambda x: isinstance(x, (int, float)) and 4 <= x <= 10
            )]),
            'Not Ranking': len(latest_data[latest_data['Recharge Position'].apply(
                lambda x: str(x).lower() in ['not ranking', 'lost', ''] or pd.isna(x)
            )])
        }
        
        fig_pie = px.pie(
            values=list(position_data.values()),
            names=list(position_data.keys()),
            title="Search Position Distribution",
            color_discrete_map={
                'Top 3': '#22c55e',
                'Positions 4-10': '#f59e0b', 
                'Not Ranking': '#ef4444'
            }
        )
        
        fig_pie.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#f8fafc',
            title_font_size=16,
            title_font_color='#f8fafc'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Market Performance Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if 'Market' in latest_data.columns:
            market_performance = latest_data.groupby('Market').agg({
                'Recharge Position': lambda x: x[x.apply(lambda y: isinstance(y, (int, float)))].mean()
            }).reset_index()
            market_performance.columns = ['Market', 'Avg_Position']
            market_performance = market_performance.dropna()
            
            if not market_performance.empty:
                fig_bar = px.bar(
                    market_performance,
                    x='Market',
                    y='Avg_Position',
                    title="Average Position by Market",
                    color='Avg_Position',
                    color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
                )
                
                fig_bar.update_layout(
                    height=350,
                    yaxis_title="Average Position (Lower is Better)",
                    yaxis=dict(autorange="reversed"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    title_font_size=16,
                    title_font_color='#f8fafc'
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Keywords Performance Table
    st.markdown('<div class="section-title">🎯 Keyword Performance Summary</div>', unsafe_allow_html=True)
    
    if not latest_data.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create display dataframe
        display_df = latest_data.copy()
        
        # Format columns for display
        display_df['Position'] = display_df['Recharge Position'].apply(
            lambda x: get_position_status(x)[0]
        )
        
        display_df['AI Overview Status'] = display_df['AI Overview'].apply(
            lambda x: '✅ Present' if has_ai_overview(x) else '❌ Missing'
        ) if 'AI Overview' in display_df.columns else '❓ Unknown'
        
        display_df['Change'] = display_df.get('Position Change', 'Unknown')
        
        # Select columns for display
        columns_to_show = ['Keyword', 'Market', 'Position', 'Change', 'AI Overview Status']
        available_columns = [col for col in columns_to_show if col in display_df.columns or col in ['Position', 'AI Overview Status', 'Change']]
        
        if available_columns:
            table_df = display_df[['Keyword', 'Market'] + [col for col in available_columns if col not in ['Keyword', 'Market']]]
            st.dataframe(
                table_df, 
                use_container_width=True, 
                hide_index=True,
                height=400
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_keyword_analysis(df_processed):
    """Detailed keyword analysis view"""
    
    if df_processed.empty:
        st.error("No data available.")
        return
    
    # Process datetime
    df_processed['DateTime'] = df_processed['Date/Time'].apply(parse_excel_datetime)
    df_processed = df_processed.dropna(subset=['DateTime'])
    
    # Header
    st.markdown('<div class="section-title">🔍 Keyword Performance Analysis</div>', unsafe_allow_html=True)
    
    # Keyword selector
    if 'Keyword' in df_processed.columns:
        available_keywords = sorted(df_processed['Keyword'].dropna().unique())
        selected_keyword = st.selectbox(
            "Select keyword to analyze:",
            available_keywords,
            key="keyword_selector"
        )
    else:
        st.error("No keywords found in data")
        return
    
    if selected_keyword:
        # Filter data for selected keyword
        keyword_data = df_processed[df_processed['Keyword'] == selected_keyword].copy()
        keyword_data = keyword_data.sort_values('DateTime')
        
        if keyword_data.empty:
            st.error(f"No data found for keyword: {selected_keyword}")
            return
        
        # Latest metrics
        latest_row = keyword_data.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_pos = latest_row.get('Recharge Position', 'Unknown')
            st.markdown(create_metric_card("Current Position", current_pos), unsafe_allow_html=True)
        
        with col2:
            market = latest_row.get('Market', 'Unknown')
            st.markdown(create_metric_card("Market", market), unsafe_allow_html=True)
        
        with col3:
            change = latest_row.get('Position Change', 'Unknown')
            st.markdown(create_metric_card("Latest Change", change), unsafe_allow_html=True)
        
        with col4:
            ai_status = latest_row.get('AI Overview', '')
            ai_display = '✅ Present' if has_ai_overview(ai_status) else '❌ Missing'
            st.markdown(create_metric_card("AI Overview", ai_display), unsafe_allow_html=True)
        
        # Position trend chart
        st.markdown('<div class="section-title">📈 Position Trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create position trend
        plot_data = keyword_data.copy()
        plot_data['Position_Numeric'] = plot_data['Recharge Position'].apply(
            lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else None
        )
        plot_data = plot_data.dropna(subset=['Position_Numeric'])
        
        if not plot_data.empty:
            fig = px.line(
                plot_data,
                x='DateTime',
                y='Position_Numeric',
                title=f'Position History: {selected_keyword}',
                markers=True,
                line_shape='spline'
            )
            
            fig.update_layout(
                height=400,
                yaxis=dict(autorange="reversed", title="Search Position"),
                xaxis_title="Date",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f8fafc',
                title_font_color='#f8fafc'
            )
            
            # Add reference lines
            fig.add_hline(y=3.5, line_dash="dash", line_color="rgba(34, 197, 94, 0.7)", 
                         annotation_text="Top 3 Threshold")
            fig.add_hline(y=10.5, line_dash="dash", line_color="rgba(245, 158, 11, 0.7)", 
                         annotation_text="Page 1 Threshold")
            
            fig.update_traces(
                line=dict(width=3, color='#22c55e'),
                marker=dict(size=8, color='#22c55e')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric position data available for trend analysis.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_serp_comparison(df_processed):
    """Professional SERP comparison view - Top 5 results only"""
    
    if df_processed.empty:
        st.error("No data available.")
        return
    
    # Process datetime
    df_processed['DateTime'] = df_processed['Date/Time'].apply(parse_excel_datetime)
    df_processed = df_processed.dropna(subset=['DateTime'])
    
    # Header
    st.markdown('<div class="section-title">⚖️ SERP Results Comparison (Top 5)</div>', unsafe_allow_html=True)
    
    # Keyword selector
    if 'Keyword' in df_processed.columns:
        available_keywords = sorted(df_processed['Keyword'].unique())
        selected_keyword = st.selectbox(
            "Select keyword to compare:",
            available_keywords,
            key="serp_comparison_keyword"
        )
    else:
        st.error("No keywords found")
        return
    
    if not selected_keyword:
        return
    
    # Get available datetimes for selected keyword
    keyword_data = df_processed[df_processed['Keyword'] == selected_keyword].copy()
    available_datetimes = sorted(keyword_data['DateTime'].dropna().unique())
    
    if len(available_datetimes) < 2:
        st.warning("Need at least 2 data points for comparison.")
        return
    
    # Date selectors
    datetime_options = [(dt.strftime('%b %d, %Y at %I:%M %p'), dt) for dt in available_datetimes]
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_dt1_display = st.selectbox(
            "📅 Baseline Date:",
            options=[opt[0] for opt in datetime_options],
            index=0,
            key="datetime1"
        )
        selected_dt1 = next(opt[1] for opt in datetime_options if opt[0] == selected_dt1_display)
    
    with col2:
        selected_dt2_display = st.selectbox(
            "📅 Comparison Date:",
            options=[opt[0] for opt in datetime_options],
            index=len(datetime_options)-1,
            key="datetime2"
        )
        selected_dt2 = next(opt[1] for opt in datetime_options if opt[0] == selected_dt2_display)
    
    if selected_dt1 == selected_dt2:
        st.warning("Please select two different times for comparison.")
        return
    
    # Get data for comparison
    data1 = keyword_data[keyword_data['DateTime'] == selected_dt1].iloc[0] if not keyword_data[keyword_data['DateTime'] == selected_dt1].empty else None
    data2 = keyword_data[keyword_data['DateTime'] == selected_dt2].iloc[0] if not keyword_data[keyword_data['DateTime'] == selected_dt2].empty else None
    
    if data1 is None or data2 is None:
        st.error("No data found for selected times.")
        return
    
    # Extract SERP results (Top 5 only)
    def extract_serp_results(data_row):
        if data_row is None:
            return {}
        
        results = {}
        for i in range(1, 6):  # Top 5 positions only
            col_name = f'Position {i}'
            if col_name in data_row and pd.notna(data_row[col_name]) and str(data_row[col_name]).strip():
                url = str(data_row[col_name]).strip()
                # Skip if it's just HTML tags or empty content
                if url.startswith('<') or url in ['</div>', '<div>', '']:
                    continue
                    
                try:
                    domain = urlparse(url).netloc.replace('www.', '')
                    # Extract title from URL or use domain
                    title = domain.split('.')[0].title() if domain else url[:50]
                    if not title:
                        title = f"Result {i}"
                except:
                    domain = url[:50] + "..." if len(url) > 50 else url
                    title = domain
                
                results[i] = {
                    'url': url,
                    'domain': domain,
                    'title': title,
                    'is_recharge': 'recharge.com' in url.lower()
                }
        return results
    
    serp1 = extract_serp_results(data1)
    serp2 = extract_serp_results(data2)
    
    # Track URL movements for arrows
    url_movements = {}
    all_urls = set()
    
    # Collect all URLs
    for pos, result in serp1.items():
        all_urls.add(result['url'])
    for pos, result in serp2.items():
        all_urls.add(result['url'])
    
    # Calculate movements
    for url in all_urls:
        pos1 = None
        pos2 = None
        
        for pos, result in serp1.items():
            if result['url'] == url:
                pos1 = pos
                break
        
        for pos, result in serp2.items():
            if result['url'] == url:
                pos2 = pos
                break
        
        if pos1 is not None or pos2 is not None:
            url_movements[url] = {'pos1': pos1, 'pos2': pos2}
    
    # Recharge position analysis
    recharge_pos1 = data1.get('Recharge Position', None)
    recharge_pos2 = data2.get('Recharge Position', None)
    
    # Overview metrics
    st.markdown(f'<div class="section-title">🔍 SERP Overview: {selected_keyword}</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate changes (only for top 5)
    improved = sum(1 for url, moves in url_movements.items() 
                  if moves['pos1'] and moves['pos2'] and moves['pos1'] > moves['pos2'])
    declined = sum(1 for url, moves in url_movements.items() 
                  if moves['pos1'] and moves['pos2'] and moves['pos1'] < moves['pos2'])
    new_entries = sum(1 for url, moves in url_movements.items() 
                     if moves['pos1'] is None and moves['pos2'] is not None)
    lost_entries = sum(1 for url, moves in url_movements.items() 
                      if moves['pos1'] is not None and moves['pos2'] is None)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #22c55e;">
            <div class="metric-number" style="color: #22c55e;">{improved}</div>
            <div class="metric-label">📈 Improved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #ef4444;">
            <div class="metric-number" style="color: #ef4444;">{declined}</div>
            <div class="metric-label">📉 Declined</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #3b82f6;">
            <div class="metric-number" style="color: #3b82f6;">{new_entries}</div>
            <div class="metric-label">🆕 New</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #f59e0b;">
            <div class="metric-number" style="color: #f59e0b;">{lost_entries}</div>
            <div class="metric-label">❌ Lost</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recharge.com Position Tracking
    st.markdown('<div class="section-title">🔋 Recharge.com Position Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pos1_display = f"#{int(recharge_pos1)}" if isinstance(recharge_pos1, (int, float)) else "Not Ranking"
        st.markdown(create_metric_card("Baseline Position", pos1_display), unsafe_allow_html=True)
    
    with col2:
        pos2_display = f"#{int(recharge_pos2)}" if isinstance(recharge_pos2, (int, float)) else "Not Ranking"
        st.markdown(create_metric_card("Current Position", pos2_display), unsafe_allow_html=True)
    
    with col3:
        if isinstance(recharge_pos1, (int, float)) and isinstance(recharge_pos2, (int, float)):
            change = recharge_pos1 - recharge_pos2
            if change > 0:
                change_text = f"📈 +{change}"
                change_color = "#22c55e"
            elif change < 0:
                change_text = f"📉 {abs(change)}"
                change_color = "#ef4444"
            else:
                change_text = "➡️ No Change"
                change_color = "#f59e0b"
        else:
            change_text = "❓ Unknown"
            change_color = "#64748b"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {change_color};">
            <div class="metric-number" style="color: {change_color};">{change_text}</div>
            <div class="metric-label">Position Change</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Side-by-side SERP comparison (Top 5 only)
    st.markdown('<div class="section-title">🔍 Top 5 SERP Results Comparison</div>', unsafe_allow_html=True)
    
    # Create side-by-side comparison using columns
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"""
        <div class="serp-column">
            <div class="serp-header">📅 {selected_dt1.strftime('%b %d, %Y at %I:%M %p')}</div>
        """, unsafe_allow_html=True)
        
        # Show baseline SERP results (Top 5)
        for position in range(1, 6):
            if position in serp1:
                result = serp1[position]
                result_class = "recharge" if result['is_recharge'] else ""
                position_color = "#f59e0b" if result['is_recharge'] else "#64748b"
                
                st.markdown(f"""
                <div class="serp-result {result_class}">
                    <div class="position-number" style="background: {position_color};">
                        {position}
                    </div>
                    <div class="result-content">
                        <div class="result-title">{result['title']}</div>
                        <div class="result-url">{result['url'][:60]}{'...' if len(result['url']) > 60 else ''}</div>
                        {'<span class="result-badge badge-recharge">🔋 Recharge.com</span>' if result['is_recharge'] else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="serp-result" style="opacity: 0.3;">
                    <div class="position-number" style="background: #64748b;">
                        {position}
                    </div>
                    <div class="result-content">
                        <div class="result-title">No result</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown(f"""
        <div class="serp-column">
            <div class="serp-header">📅 {selected_dt2.strftime('%b %d, %Y at %I:%M %p')}</div>
        """, unsafe_allow_html=True)
        
        # Show comparison SERP results with change indicators (Top 5)
        for position in range(1, 6):
            if position in serp2:
                result = serp2[position]
                url = result['url']
                movement = url_movements.get(url, {})
                pos1 = movement.get('pos1')
                pos2 = movement.get('pos2')
                
                # Determine change type and styling
                if pos1 is None:
                    change_class = "new"
                    change_text = "🆕 NEW"
                    change_color = "#3b82f6"
                elif pos1 and pos2 and pos1 > pos2:
                    change_class = "improved"
                    change_text = f"📈 +{pos1 - pos2}"
                    change_color = "#22c55e"
                elif pos1 and pos2 and pos1 < pos2:
                    change_class = "declined"
                    change_text = f"📉 -{pos2 - pos1}"
                    change_color = "#ef4444"
                else:
                    change_class = "recharge" if result['is_recharge'] else ""
                    change_text = ""
                    change_color = "#f59e0b" if result['is_recharge'] else "#64748b"
                
                st.markdown(f"""
                <div class="serp-result {change_class}">
                    <div class="position-number" style="background: {change_color};">
                        {position}
                    </div>
                    <div class="result-content">
                        <div class="result-title">{result['title']}</div>
                        <div class="result-url">{result['url'][:60]}{'...' if len(result['url']) > 60 else ''}</div>
                        {'<span class="result-badge badge-recharge">🔋 Recharge.com</span>' if result['is_recharge'] else ''}
                        {f'<span class="result-badge badge-{change_class}">{change_text}</span>' if change_text else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="serp-result" style="opacity: 0.3;">
                    <div class="position-number" style="background: #64748b;">
                        {position}
                    </div>
                    <div class="result-content">
                        <div class="result-title">No result</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # AI Overview Comparison
    st.markdown('<div class="section-title">🤖 AI Overview Comparison</div>', unsafe_allow_html=True)
    
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown(f'**📅 {selected_dt1.strftime("%b %d, %Y at %I:%M %p")}**')
        
        ai_content1 = data1.get('AI Overview', '')
        if has_ai_overview(ai_content1):
            st.markdown("**🤖 AI Overview Present**")
            st.text_area(
                "AI Overview Content",
                str(ai_content1),
                height=200,
                key="ai_content_1",
                label_visibility="collapsed"
            )
        else:
            st.markdown("**❌ No AI Overview**")
            st.info("No AI Overview content was present at this time.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_ai2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown(f'**📅 {selected_dt2.strftime("%b %d, %Y at %I:%M %p")}**')
        
        ai_content2 = data2.get('AI Overview', '')
        if has_ai_overview(ai_content2):
            st.markdown("**🤖 AI Overview Present**")
            st.text_area(
                "AI Overview Content",
                str(ai_content2),
                height=200,
                key="ai_content_2",
                label_visibility="collapsed"
            )
        else:
            st.markdown("**❌ No AI Overview**")
            st.info("No AI Overview content was present at this time.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_llm_position_tracking(llm_df):
    """Show LLM/ChatGPT position tracking dashboard"""
    
    if llm_df.empty:
        st.error("No LLM data available.")
        return
    
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🤖 LLM Position Tracking</h1>
        <p>Recharge.com visibility in AI-powered search results</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Parse dates for filtering
    llm_df['DateTime'] = pd.to_datetime(llm_df['Date'], errors='coerce')
    llm_df['DateTime'] = llm_df['DateTime'].fillna(pd.to_datetime(llm_df['Time'], errors='coerce'))
    
    # Filters Section
    st.markdown('<div class="section-title">🔧 Filters</div>', unsafe_allow_html=True)
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Country Filter
        available_countries = ['All'] + sorted(llm_df['Country'].dropna().unique().tolist())
        selected_country = st.selectbox(
            "🌍 Select Country",
            available_countries,
            key="llm_country_filter"
        )
    
    with filter_col2:
        # Date Range Filter
        if not llm_df['DateTime'].isna().all():
            min_date = llm_df['DateTime'].min()
            max_date = llm_df['DateTime'].max()
            
            date_range = st.date_input(
                "📅 Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="llm_date_filter"
            )
            
            # Handle single date selection
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date = end_date = date_range if not isinstance(date_range, tuple) else date_range[0]
        else:
            start_date = end_date = None
    
    with filter_col3:
        # Keyword Search Filter
        keyword_search = st.text_input(
            "🔍 Search Keywords",
            placeholder="Type to search...",
            key="llm_keyword_search"
        )
    
    # Apply filters
    filtered_df = llm_df.copy()
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    if start_date and end_date:
        # Convert dates to datetime for comparison
        start_datetime = pd.Timestamp(start_date)
        end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        mask = (filtered_df['DateTime'] >= start_datetime) & (filtered_df['DateTime'] <= end_datetime)
        filtered_df = filtered_df[mask]
    
    if keyword_search:
        filtered_df = filtered_df[
            filtered_df['Keyword'].str.contains(keyword_search, case=False, na=False)
        ]
    
    # Filter for Recharge.com entries
    recharge_df = filtered_df[filtered_df['Result_URL'].str.contains('recharge.com', na=False, case=False)].copy()
    
    # Get unique keywords
    all_keywords = filtered_df['Keyword'].dropna().unique()
    recharge_keywords = recharge_df['Keyword'].dropna().unique()
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("Total Keywords", len(all_keywords)), unsafe_allow_html=True)
    
    with col2:
        ranking_rate = round((len(recharge_keywords)/len(all_keywords)*100)) if len(all_keywords) > 0 else 0
        st.markdown(create_metric_card("Recharge Visibility", f"{len(recharge_keywords)} ({ranking_rate}%)"), unsafe_allow_html=True)
    
    with col3:
        # Top 3 positions for Recharge
        top_3_keywords = recharge_df[recharge_df['Position'] <= 3]['Keyword'].nunique() if not recharge_df.empty else 0
        st.markdown(create_metric_card("Top 3 Keywords", top_3_keywords), unsafe_allow_html=True)
    
    with col4:
        # Average position
        avg_position = round(recharge_df['Position'].mean(), 1) if not recharge_df.empty else 'N/A'
        st.markdown(create_metric_card("Avg Position", avg_position), unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-title">📊 LLM Performance Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Position Distribution for Recharge
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if not recharge_df.empty:
            position_counts = recharge_df['Position'].value_counts().sort_index()
            
            fig_bar = px.bar(
                x=position_counts.index,
                y=position_counts.values,
                title="Recharge.com Position Distribution in LLM Results",
                labels={'x': 'Position', 'y': 'Frequency'},
                color=position_counts.values,
                color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'][::-1]
            )
            
            fig_bar.update_layout(
                height=350,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f8fafc',
                title_font_size=16,
                title_font_color='#f8fafc'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No Recharge.com entries found in LLM results")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Country Performance
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if not recharge_df.empty and 'Country' in recharge_df.columns:
            country_stats = recharge_df.groupby('Country').agg({
                'Position': 'mean',
                'Keyword': 'nunique'
            }).round(1)
            country_stats.columns = ['Avg Position', 'Keywords']
            
            # Create grouped bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Keywords',
                x=country_stats.index,
                y=country_stats['Keywords'],
                yaxis='y',
                marker_color='#3b82f6',
                text=country_stats['Keywords'],
                textposition='auto',
            ))
            
            fig.add_trace(go.Bar(
                name='Avg Position',
                x=country_stats.index,
                y=country_stats['Avg Position'],
                yaxis='y2',
                marker_color='#f59e0b',
                text=country_stats['Avg Position'],
                textposition='auto',
            ))
            
            fig.update_layout(
                title="LLM Performance by Country",
                height=350,
                yaxis=dict(title='Keywords', side='left'),
                yaxis2=dict(title='Avg Position', overlaying='y', side='right'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f8fafc',
                title_font_size=16,
                title_font_color='#f8fafc',
                showlegend=True,
                legend=dict(x=0, y=1, bgcolor='rgba(0,0,0,0)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No country data available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Individual Keyword Time Analysis
    st.markdown('<div class="section-title">📈 Keyword Position Trends Over Time</div>', unsafe_allow_html=True)
    
    if not filtered_df.empty and not filtered_df['DateTime'].isna().all():
        # Keyword selector for time analysis
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_keyword_for_trend = st.selectbox(
                "Select keyword to analyze position trend:",
                sorted(all_keywords),
                key="llm_keyword_trend_selector"
            )
        
        with col2:
            show_all_results = st.checkbox(
                "Show all results",
                key="llm_show_all_results",
                help="Show all search results, not just Recharge.com"
            )
        
        if selected_keyword_for_trend:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Filter data for selected keyword
            keyword_trend_data = filtered_df[
                filtered_df['Keyword'] == selected_keyword_for_trend
            ].copy()
            
            if not keyword_trend_data['DateTime'].isna().all():
                # Group by datetime and get Recharge position
                keyword_trend_data = keyword_trend_data.sort_values('DateTime')
                
                if show_all_results:
                    # Show all top positions over time
                    trend_data = keyword_trend_data.groupby(['DateTime', 'Result_URL'])['Position'].min().reset_index()
                    
                    # Create line chart for multiple URLs
                    fig_trend = px.line(
                        trend_data,
                        x='DateTime',
                        y='Position',
                        color='Result_URL',
                        title=f'Position Trends: {selected_keyword_for_trend}',
                        markers=True,
                        line_shape='linear'
                    )
                    
                    # Customize traces
                    for trace in fig_trend.data:
                        if 'recharge.com' in trace.name.lower():
                            trace.line.width = 4
                            trace.line.color = '#f59e0b'
                            trace.name = '🔋 Recharge.com'
                        else:
                            trace.line.width = 2
                            trace.showlegend = False
                else:
                    # Show only Recharge.com positions
                    recharge_trend = keyword_trend_data[
                        keyword_trend_data['Result_URL'].str.contains('recharge.com', case=False, na=False)
                    ]
                    
                    if not recharge_trend.empty:
                        trend_summary = recharge_trend.groupby('DateTime')['Position'].min().reset_index()
                        
                        fig_trend = px.line(
                            trend_summary,
                            x='DateTime',
                            y='Position',
                            title=f'Recharge.com Position Trend: {selected_keyword_for_trend}',
                            markers=True,
                            line_shape='spline'
                        )
                        
                        fig_trend.update_traces(
                            line=dict(width=3, color='#f59e0b'),
                            marker=dict(size=10, color='#f59e0b')
                        )
                    else:
                        st.info(f"Recharge.com not found in results for '{selected_keyword_for_trend}'")
                        fig_trend = None
                
                if fig_trend:
                    fig_trend.update_layout(
                        height=400,
                        yaxis=dict(
                            autorange="reversed",
                            title="Search Position",
                            dtick=1,
                            range=[0.5, 10.5]
                        ),
                        xaxis_title="Date/Time",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#f8fafc',
                        title_font_size=16,
                        title_font_color='#f8fafc',
                        hovermode='x unified'
                    )
                    
                    # Add reference lines
                    fig_trend.add_hline(
                        y=3.5, 
                        line_dash="dash", 
                        line_color="rgba(34, 197, 94, 0.5)",
                        annotation_text="Top 3"
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No time data available for this keyword")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Keyword Performance Table
    st.markdown('<div class="section-title">🔍 Keyword-Level LLM Performance</div>', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create summary by keyword
        keyword_summary = []
        
        for keyword in all_keywords:
            keyword_data = filtered_df[filtered_df['Keyword'] == keyword]
            recharge_data = keyword_data[keyword_data['Result_URL'].str.contains('recharge.com', na=False, case=False)]
            
            # Get latest position if multiple entries
            latest_position = recharge_data.sort_values('DateTime', na_position='last')['Position'].iloc[-1] if not recharge_data.empty else None
            
            # Calculate position change if we have time data
            position_change = None
            if not recharge_data.empty and len(recharge_data) > 1:
                sorted_data = recharge_data.sort_values('DateTime', na_position='last')
                if len(sorted_data) >= 2:
                    latest = sorted_data['Position'].iloc[-1]
                    previous = sorted_data['Position'].iloc[-2]
                    position_change = previous - latest
            
            summary = {
                'Keyword': keyword,
                'Country': keyword_data['Country'].iloc[0] if not keyword_data.empty else 'Unknown',
                'Total Results': len(keyword_data['Result_URL'].unique()),
                'Recharge Position': latest_position if latest_position else 'Not Ranking',
                'Change': f"+{position_change}" if position_change and position_change > 0 else f"{position_change}" if position_change else "-",
                'Status': '✅ Ranking' if latest_position else '❌ Not Ranking'
            }
            keyword_summary.append(summary)
        
        summary_df = pd.DataFrame(keyword_summary)
        
        # Sort by Recharge Position (ranking first, then not ranking)
        summary_df['Sort_Key'] = summary_df['Recharge Position'].apply(
            lambda x: x if isinstance(x, (int, float)) else 999
        )
        summary_df = summary_df.sort_values('Sort_Key').drop('Sort_Key', axis=1)
        
        # Format the position column
        summary_df['Recharge Position'] = summary_df['Recharge Position'].apply(
            lambda x: f"#{int(x)}" if isinstance(x, (int, float)) else x
        )
        
        # Apply country flags
        summary_df['Country'] = summary_df['Country'].apply(
            lambda x: get_country_flag(x) if x != 'Unknown' else x
        )
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Export button
        csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"llm_position_tracking_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Top Performing Keywords
    st.markdown('<div class="section-title">🏆 Top Performing Keywords in LLM Results</div>', unsafe_allow_html=True)
    
    if not recharge_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**🥇 Best Positions**")
            
            # Get keywords where Recharge ranks in top 3
            top_performers = recharge_df[recharge_df['Position'] <= 3].groupby('Keyword')['Position'].min().sort_values()
            
            if not top_performers.empty:
                for keyword, position in top_performers.head(10).items():
                    country = recharge_df[recharge_df['Keyword'] == keyword]['Country'].iloc[0]
                    country_flag = get_country_flag(country)
                    st.markdown(f"• **{keyword}** ({country_flag}): Position #{int(position)}")
            else:
                st.info("No keywords ranking in top 3")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**📈 Keywords Needing Improvement**")
            
            # Get keywords where Recharge ranks but not in top 3
            needs_improvement = recharge_df[recharge_df['Position'] > 3].groupby('Keyword')['Position'].min().sort_values(ascending=False)
            
            if not needs_improvement.empty:
                for keyword, position in needs_improvement.head(10).items():
                    country = recharge_df[recharge_df['Keyword'] == keyword]['Country'].iloc[0]
                    country_flag = get_country_flag(country)
                    st.markdown(f"• **{keyword}** ({country_flag}): Position #{int(position)}")
            else:
                st.info("All keywords ranking in top 3!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Compact Position Matrix View
    st.markdown('<div class="section-title">📋 All Keywords Position Matrix (Top 5)</div>', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Create matrix data for all keywords
        matrix_data = []
        
        for keyword in sorted(all_keywords):
            keyword_data = filtered_df[filtered_df['Keyword'] == keyword]
            
            # Get latest data if datetime available
            if not keyword_data['DateTime'].isna().all():
                latest_time = keyword_data['DateTime'].max()
                keyword_data = keyword_data[keyword_data['DateTime'] == latest_time]
            
            # Get top 5 positions
            top_5 = keyword_data[keyword_data['Position'] <= 5].sort_values('Position')
            
            # Create row data
            row_data = {
                'Keyword': keyword,
                'Country': get_country_flag(keyword_data['Country'].iloc[0]) if not keyword_data.empty else 'Unknown'
            }
            
            # Add position columns
            for pos in range(1, 6):
                pos_data = top_5[top_5['Position'] == pos]
                if not pos_data.empty:
                    url = pos_data['Result_URL'].iloc[0]
                    try:
                        domain = urlparse(url).netloc.replace('www.', '')
                        if 'recharge.com' in url.lower():
                            row_data[f'Pos {pos}'] = f"🔋 {domain}"
                        else:
                            row_data[f'Pos {pos}'] = domain[:20]
                    except:
                        row_data[f'Pos {pos}'] = url[:20]
                else:
                    row_data[f'Pos {pos}'] = "-"
            
            # Add Recharge position
            recharge_pos = keyword_data[
                keyword_data['Result_URL'].str.contains('recharge.com', case=False, na=False)
            ]['Position'].min()
            
            if pd.notna(recharge_pos):
                row_data['Recharge Pos'] = f"#{int(recharge_pos)}"
            else:
                row_data['Recharge Pos'] = "Not Ranking"
            
            matrix_data.append(row_data)
        
        # Create DataFrame
        matrix_df = pd.DataFrame(matrix_data)
        
        # Sort by Recharge position
        matrix_df['Sort_Key'] = matrix_df['Recharge Pos'].apply(
            lambda x: int(x.replace('#', '')) if x.startswith('#') else 999
        )
        matrix_df = matrix_df.sort_values('Sort_Key').drop('Sort_Key', axis=1)
        
        # Display the matrix
        st.dataframe(
            matrix_df,
            use_container_width=True,
            hide_index=True,
            height=min(600, 40 * len(matrix_df) + 50)
        )
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ranking_count = len([x for x in matrix_df['Recharge Pos'] if x != 'Not Ranking'])
            st.metric("Keywords with Recharge", f"{ranking_count}/{len(matrix_df)}")
        
        with col2:
            top_3_count = len([x for x in matrix_df['Recharge Pos'] if x.startswith('#') and int(x[1:]) <= 3])
            st.metric("In Top 3", top_3_count)
        
        with col3:
            pos_1_count = len([x for x in matrix_df['Recharge Pos'] if x == '#1'])
            st.metric("Position #1", pos_1_count)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Complete Position Rankings by Keyword
    st.markdown('<div class="section-title">🎯 Complete Position Rankings by Keyword</div>', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # Keyword selector for detailed SERP view
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_keyword_detail = st.selectbox(
                "Select keyword to see all positions:",
                sorted(all_keywords),
                key="llm_keyword_detail_selector"
            )
        
        with col2:
            max_positions = st.slider(
                "Show top N positions:",
                min_value=5,
                max_value=30,
                value=10,
                step=5,
                key="llm_max_positions"
            )
        
        with col3:
            show_latest_only = st.checkbox(
                "Latest results only",
                value=True,
                key="llm_latest_only",
                help="Show only the most recent results for this keyword"
            )
        
        if selected_keyword_detail:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Filter data for selected keyword
            keyword_detail_data = filtered_df[
                filtered_df['Keyword'] == selected_keyword_detail
            ].copy()
            
            if not keyword_detail_data.empty:
                # Get latest or all timestamps
                if show_latest_only and not keyword_detail_data['DateTime'].isna().all():
                    latest_time = keyword_detail_data['DateTime'].max()
                    keyword_detail_data = keyword_detail_data[
                        keyword_detail_data['DateTime'] == latest_time
                    ]
                    display_time = latest_time.strftime('%B %d, %Y at %I:%M %p') if pd.notna(latest_time) else "Unknown"
                else:
                    display_time = "All available data"
                
                # Get country for this keyword
                keyword_country = keyword_detail_data['Country'].iloc[0] if 'Country' in keyword_detail_data.columns else 'Unknown'
                
                # Create position summary
                st.markdown(f"**📍 Keyword:** `{selected_keyword_detail}` | **🌍 Country:** {get_country_flag(keyword_country)} | **🕐 Data:** {display_time}")
                
                # Group by position and get URLs
                position_data = keyword_detail_data[
                    keyword_detail_data['Position'] <= max_positions
                ].sort_values('Position')
                
                if not position_data.empty:
                    # Create two-column layout for positions
                    col_left, col_right = st.columns(2)
                    
                    # Split positions into two columns
                    positions = sorted(position_data['Position'].unique())
                    mid_point = (len(positions) + 1) // 2
                    
                    with col_left:
                        for pos in positions[:mid_point]:
                            pos_urls = position_data[position_data['Position'] == pos]['Result_URL'].values
                            
                            for url in pos_urls:
                                # Determine if it's Recharge
                                is_recharge = 'recharge.com' in url.lower()
                                
                                # Extract domain for display
                                try:
                                    domain = urlparse(url).netloc.replace('www.', '')
                                    display_url = domain if domain else url[:50]
                                except:
                                    display_url = url[:50] + "..." if len(url) > 50 else url
                                
                                # Style based on whether it's Recharge
                                if is_recharge:
                                    position_color = "#f59e0b"
                                    badge = "🔋 Recharge"
                                    result_class = "recharge"
                                else:
                                    position_color = "#64748b"
                                    badge = ""
                                    result_class = ""
                                
                                st.markdown(f"""
                                <div class="serp-result {result_class}">
                                    <div class="position-number" style="background: {position_color};">
                                        {int(pos)}
                                    </div>
                                    <div class="result-content">
                                        <div class="result-url">{display_url}</div>
                                        {f'<span class="result-badge badge-recharge">{badge}</span>' if badge else ''}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with col_right:
                        for pos in positions[mid_point:]:
                            pos_urls = position_data[position_data['Position'] == pos]['Result_URL'].values
                            
                            for url in pos_urls:
                                # Determine if it's Recharge
                                is_recharge = 'recharge.com' in url.lower()
                                
                                # Extract domain for display
                                try:
                                    domain = urlparse(url).netloc.replace('www.', '')
                                    display_url = domain if domain else url[:50]
                                except:
                                    display_url = url[:50] + "..." if len(url) > 50 else url
                                
                                # Style based on whether it's Recharge
                                if is_recharge:
                                    position_color = "#f59e0b"
                                    badge = "🔋 Recharge"
                                    result_class = "recharge"
                                else:
                                    position_color = "#64748b"
                                    badge = ""
                                    result_class = ""
                                
                                st.markdown(f"""
                                <div class="serp-result {result_class}">
                                    <div class="position-number" style="background: {position_color};">
                                        {int(pos)}
                                    </div>
                                    <div class="result-content">
                                        <div class="result-url">{display_url}</div>
                                        {f'<span class="result-badge badge-recharge">{badge}</span>' if badge else ''}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Summary statistics
                    st.markdown("---")
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    
                    with col_stat1:
                        recharge_pos = position_data[
                            position_data['Result_URL'].str.contains('recharge.com', case=False, na=False)
                        ]['Position'].min()
                        
                        if pd.notna(recharge_pos):
                            st.metric("Recharge Position", f"#{int(recharge_pos)}")
                        else:
                            st.metric("Recharge Position", "Not Ranking")
                    
                    with col_stat2:
                        total_results = len(position_data['Position'].unique())
                        st.metric("Positions Shown", f"{total_results}/{max_positions}")
                    
                    with col_stat3:
                        unique_domains = position_data['Result_URL'].apply(
                            lambda x: urlparse(x).netloc.replace('www.', '') if x else ''
                        ).nunique()
                        st.metric("Unique Domains", unique_domains)
                
                else:
                    st.info(f"No results found in top {max_positions} positions")
            else:
                st.warning(f"No data available for keyword: {selected_keyword_detail}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Historical Performance Summary
    if not filtered_df['DateTime'].isna().all() and not recharge_df.empty:
        st.markdown('<div class="section-title">📊 Historical Performance Summary</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Position trend over time (aggregated)
            daily_avg = recharge_df.set_index('DateTime').resample('D')['Position'].mean().dropna()
            
            if not daily_avg.empty:
                fig_daily = px.line(
                    x=daily_avg.index,
                    y=daily_avg.values,
                    title="Average Daily Position Trend",
                    labels={'x': 'Date', 'y': 'Average Position'}
                )
                
                fig_daily.update_traces(
                    line=dict(width=3, color='#22c55e'),
                    mode='lines+markers',
                    marker=dict(size=8)
                )
                
                fig_daily.update_layout(
                    height=300,
                    yaxis=dict(autorange="reversed", title="Average Position"),
                    xaxis_title="Date",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    showlegend=False
                )
                
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("Not enough historical data")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Visibility trend over time
            daily_visibility = filtered_df.set_index('DateTime').resample('D').apply(
                lambda x: (x['Result_URL'].str.contains('recharge.com', case=False, na=False).sum() / len(x) * 100) if len(x) > 0 else 0
            ).dropna()
            
            if not daily_visibility.empty:
                fig_visibility = px.area(
                    x=daily_visibility.index,
                    y=daily_visibility.values,
                    title="Daily Visibility Rate (%)",
                    labels={'x': 'Date', 'y': 'Visibility (%)'}
                )
                
                fig_visibility.update_traces(
                    fill='tozeroy',
                    line=dict(width=2, color='#3b82f6'),
                    fillcolor='rgba(59, 130, 246, 0.3)'
                )
                
                fig_visibility.update_layout(
                    height=300,
                    yaxis=dict(title="Visibility (%)", range=[0, 100]),
                    xaxis_title="Date",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    showlegend=False
                )
                
                st.plotly_chart(fig_visibility, use_container_width=True)
            else:
                st.info("Not enough historical data")
            
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Load data
    with st.spinner('Loading data...'):
        df = load_data_from_google_sheets()
        llm_df = load_llm_data()
    
    if df.empty and llm_df.empty:
        st.markdown("""
        <div class="dashboard-header">
            <h1>🔋 Recharge.com SEO Dashboard</h1>
            <p>Unable to connect to data source</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.error("No data could be loaded. Please check Google Sheets connectivity.")
        st.info("Make sure the Google Sheet is shared publicly (Anyone with the link can view)")
        return
    
    # Sidebar navigation - Updated with new option
    st.sidebar.markdown("### 📊 Navigation")
    
    page = st.sidebar.radio(
        "Select View:",
        ["🏠 Executive Dashboard", "🎯 Keyword Analysis", "⚖️ SERP Comparison", "🤖 LLM Position Tracking"],
        key="main_nav"
    )
    
    # Show data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📈 Data Summary**")
    
    if not df.empty:
        st.sidebar.markdown(f"**Traditional SEO:**")
        st.sidebar.markdown(f"Total Records: {len(df)}")
        if 'Keyword' in df.columns:
            st.sidebar.markdown(f"Keywords: {df['Keyword'].nunique()}")
    
    if not llm_df.empty:
        st.sidebar.markdown(f"**LLM/AI Search:**")
        st.sidebar.markdown(f"Total Results: {len(llm_df)}")
        st.sidebar.markdown(f"Keywords: {llm_df['Keyword'].nunique()}")
    
    # Route to appropriate page
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard(df)
    elif page == "🎯 Keyword Analysis":
        show_keyword_analysis(df)
    elif page == "⚖️ SERP Comparison":
        show_serp_comparison(df)
    elif page == "🤖 LLM Position Tracking":
        show_llm_position_tracking(llm_df)

if __name__ == "__main__":
    main()
