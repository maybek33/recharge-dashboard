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

# Modern, clean CSS styling
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .dashboard-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .dashboard-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: #ffffff;
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: #ffffff;
    }
    
    .metric-change {
        font-size: 0.9rem;
        margin: 0.25rem 0 0 0;
        font-weight: 500;
    }
    
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .neutral { color: #f59e0b; }
    
    /* Section styling */
    .section-title {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 2rem 0 1rem 0;
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .css-1d391kg .stMarkdown {
        color: #ffffff;
    }
    
    /* Button styling */
    .stButton > button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
    }
    
    /* Chart container */
    .chart-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Hide technical elements */
    .technical-details {
        display: none;
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
            return f'#{pos}', '#10b981'
        elif pos <= 10:
            return f'#{pos}', '#f59e0b'
        else:
            return f'#{pos}', '#ef4444'
    except:
        return str(position), '#6b7280'

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
            except:
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
                    
            except:
                continue
        
        if all_keyword_data:
            combined_df = pd.concat(all_keyword_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
        
    except:
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
        <p>Real-time search ranking intelligence for global markets</p>
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
                'Top 3': '#10b981',
                'Positions 4-10': '#f59e0b', 
                'Not Ranking': '#ef4444'
            }
        )
        
        fig_pie.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            title_font_color='white'
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
                    color_continuous_scale=['#10b981', '#f59e0b', '#ef4444']
                )
                
                fig_bar.update_layout(
                    height=350,
                    yaxis_title="Average Position (Lower is Better)",
                    yaxis=dict(autorange="reversed"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_size=16,
                    title_font_color='white'
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
                font_color='white',
                title_font_color='white'
            )
            
            # Add reference lines
            fig.add_hline(y=3.5, line_dash="dash", line_color="rgba(16, 185, 129, 0.7)", 
                         annotation_text="Top 3 Threshold")
            fig.add_hline(y=10.5, line_dash="dash", line_color="rgba(245, 158, 11, 0.7)", 
                         annotation_text="Page 1 Threshold")
            
            fig.update_traces(
                line=dict(width=3, color='#ffffff'),
                marker=dict(size=8, color='#10b981')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric position data available for trend analysis.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_serp_comparison(df_processed):
    """Professional SERP comparison view like Ahrefs"""
    
    if df_processed.empty:
        st.error("No data available.")
        return
    
    # Process datetime
    df_processed['DateTime'] = df_processed['Date/Time'].apply(parse_excel_datetime)
    df_processed = df_processed.dropna(subset=['DateTime'])
    
    # Header
    st.markdown('<div class="section-title">⚖️ SERP Results Comparison</div>', unsafe_allow_html=True)
    
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
    
    # Extract SERP results
    def extract_serp_results(data_row):
        if data_row is None:
            return {}
        
        results = {}
        for i in range(1, 11):  # Top 10 positions
            col_name = f'Position {i}'
            if col_name in data_row and pd.notna(data_row[col_name]) and data_row[col_name]:
                url = str(data_row[col_name])
                try:
                    domain = urlparse(url).netloc.replace('www.', '')
                    # Extract title from URL or use domain
                    title = domain.split('.')[0].title() if domain else url[:50]
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
    
    # Calculate changes
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
        <div class="metric-card" style="border-left: 4px solid #10b981;">
            <div class="metric-number" style="color: #10b981;">{improved}</div>
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
                change_color = "#10b981"
            elif change < 0:
                change_text = f"📉 {abs(change)}"
                change_color = "#ef4444"
            else:
                change_text = "➡️ No Change"
                change_color = "#f59e0b"
        else:
            change_text = "❓ Unknown"
            change_color = "#6b7280"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {change_color};">
            <div class="metric-number" style="color: {change_color};">{change_text}</div>
            <div class="metric-label">Position Change</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Side-by-side SERP comparison (Ahrefs style)
    st.markdown('<div class="section-title">🔍 Detailed SERP Comparison</div>', unsafe_allow_html=True)
    
    # Create the comparison visualization
    st.markdown("""
    <style>
    .serp-container {
        display: flex;
        gap: 2rem;
        margin: 1rem 0;
    }
    
    .serp-column {
        flex: 1;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
    }
    
    .serp-header {
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
    }
    
    .serp-result {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
    }
    
    .serp-result:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(5px);
    }
    
    .serp-result.recharge {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .serp-result.improved {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
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
        min-width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        font-size: 14px;
        color: white;
    }
    
    .result-content {
        flex: 1;
    }
    
    .result-title {
        font-weight: 600;
        margin-bottom: 0.3rem;
        color: #ffffff;
        font-size: 0.95rem;
        line-height: 1.3;
    }
    
    .result-url {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.7);
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
    }
    
    .badge-recharge {
        background: #f59e0b;
        color: white;
    }
    
    .badge-improved {
        background: #10b981;
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
    
    .badge-lost {
        background: #f59e0b;
        color: white;
    }
    
    .change-indicator {
        min-width: 60px;
        text-align: center;
        font-size: 0.8rem;
        font-weight: bold;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        margin-left: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create side-by-side comparison
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"""
        <div class="serp-column">
            <div class="serp-header">📅 {selected_dt1.strftime('%b %d, %Y at %I:%M %p')}</div>
        """, unsafe_allow_html=True)
        
        # Show baseline SERP results
        for position in range(1, 11):
            if position in serp1:
                result = serp1[position]
                result_class = "recharge" if result['is_recharge'] else ""
                position_color = "#f59e0b" if result['is_recharge'] else "#667eea"
                
                st.markdown(f"""
                <div class="serp-result {result_class}">
                    <div class="position-number" style="background: {position_color};">
                        {position}
                    </div>
                    <div class="result-content">
                        <div class="result-title">{result['title']}</div>
                        <div class="result-url">{result['url'][:80]}{'...' if len(result['url']) > 80 else ''}</div>
                        {f'<span class="result-badge badge-recharge">🔋 Recharge.com</span>' if result['is_recharge'] else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="serp-result" style="opacity: 0.3;">
                    <div class="position-number" style="background: #6b7280;">
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
        
        # Show comparison SERP results with change indicators
        for position in range(1, 11):
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
                    change_color = "#10b981"
                elif pos1 and pos2 and pos1 < pos2:
                    change_class = "declined"
                    change_text = f"📉 -{pos2 - pos1}"
                    change_color = "#ef4444"
                else:
                    change_class = "recharge" if result['is_recharge'] else ""
                    change_text = ""
                    change_color = "#f59e0b" if result['is_recharge'] else "#667eea"
                
                st.markdown(f"""
                <div class="serp-result {change_class}">
                    <div class="position-number" style="background: {change_color};">
                        {position}
                    </div>
                    <div class="result-content">
                        <div class="result-title">{result['title']}</div>
                        <div class="result-url">{result['url'][:80]}{'...' if len(result['url']) > 80 else ''}</div>
                        {f'<span class="result-badge badge-recharge">🔋 Recharge.com</span>' if result['is_recharge'] else ''}
                        {f'<span class="result-badge badge-{change_class}">{change_text}</span>' if change_text else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="serp-result" style="opacity: 0.3;">
                    <div class="position-number" style="background: #6b7280;">
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
                ai_content1,
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
                ai_content2,
                height=200,
                key="ai_content_2",
                label_visibility="collapsed"
            )
        else:
            st.markdown("**❌ No AI Overview**")
            st.info("No AI Overview content was present at this time.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Load data
    with st.spinner('Loading data...'):
        df = load_data_from_google_sheets()
    
    if df.empty:
        st.markdown("""
        <div class="dashboard-header">
            <h1>🔋 Recharge.com SEO Dashboard</h1>
            <p>Unable to connect to data source</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.error("No data could be loaded. Please check Google Sheets connectivity.")
        st.info("Make sure the Google Sheet is shared publicly (Anyone with the link can view)")
        return
    
    # Sidebar navigation
    st.sidebar.markdown("""
    <div style="padding: 1rem 0;">
        <h2 style="color: white; margin-bottom: 1rem;">📊 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select View:",
        ["🏠 Executive Dashboard", "🎯 Keyword Analysis", "⚖️ SERP Comparison"],
        key="main_nav"
    )
    
    # Show data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📈 Data Summary**")
    st.sidebar.markdown(f"Total Records: {len(df)}")
    if 'Keyword' in df.columns:
        st.sidebar.markdown(f"Keywords: {df['Keyword'].nunique()}")
    
    # Route to appropriate page
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard(df)
    elif page == "🎯 Keyword Analysis":
        show_keyword_analysis(df)
    elif page == "⚖️ SERP Comparison":
        show_serp_comparison(df)

if __name__ == "__main__":
    main()
