import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Recharge.com Ranking Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme with white fonts
st.markdown("""
<style>
    /* Dark theme styling */
    .stApp {
        background-color: #0f1419;
        color: #ffffff;
    }
    
    .main .block-container {
        background-color: #0f1419;
        color: #ffffff;
    }
    
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
        font-weight: 700;
        font-size: 3rem;
        margin: 0;
        color: white !important;
    }
    
    .main-header h3 {
        font-weight: 300;
        font-size: 1.5rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: white !important;
    }
    
    .section-header {
        font-weight: 600;
        font-size: 1.8rem;
        color: #ffffff !important;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* All text should be white */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span, .stText {
        color: #ffffff !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff !important;
    }
    
    /* Metric styling - dark cards with white text */
    .stMetric {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        border-left: 4px solid #667eea;
        color: #ffffff !important;
    }
    
    .stMetric label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    .stMetric [data-testid="metric-delta"] {
        color: #a0a9c0 !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed #667eea;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: #1a1a2e;
        border-radius: 12px;
        border: 1px solid #667eea;
    }
    
    /* Selectbox and other inputs */
    .stSelectbox label, .stRadio label, .stCheckbox label, .stDateInput label {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .css-1d391kg .stMarkdown {
        color: #ffffff !important;
    }
    
    .css-1d391kg .stSelectbox label, 
    .css-1d391kg .stRadio label, 
    .css-1d391kg .stCheckbox label, 
    .css-1d391kg .stDateInput label {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Warning and info boxes */
    .stWarning {
        background: #2d1b4e;
        color: #ffffff;
        border: 1px solid #667eea;
    }
    
    .stInfo {
        background: #1a2332;
        color: #ffffff;
        border: 1px solid #3b82f6;
    }
    
    .stSuccess {
        background: #1a3329;
        color: #ffffff;
        border: 1px solid #10b981;
    }
    
    .stError {
        background: #3d1a1a;
        color: #ffffff;
        border: 1px solid #ef4444;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Spinner styling */
    .stSpinner {
        color: #667eea !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Simple data loading function
@st.cache_data(ttl=300)
def load_data_from_excel(uploaded_file):
    """Load data from uploaded Excel file"""
    try:
        xl_file = pd.ExcelFile(uploaded_file)
        
        # Get keyword sheets (exclude Main, Admin sheets)
        keyword_sheets = [sheet for sheet in xl_file.sheet_names 
                         if sheet not in ['Main', 'ADMIN', '⚙️ ADMIN']]
        
        all_data = []
        
        for sheet_name in keyword_sheets:
            try:
                df_sheet = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                
                if df_sheet.empty or len(df_sheet.columns) < 5:
                    continue
                
                df_sheet['Sheet_Name'] = sheet_name
                
                if 'Keyword' in df_sheet.columns:
                    all_data.append(df_sheet)
                    
            except Exception as e:
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return get_sample_data()
            
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return get_sample_data()

def get_sample_data():
    """Simple sample data for demo"""
    dates = pd.date_range('2025-07-25', periods=6, freq='D')
    
    keywords_data = [
        ('recarga digi', 'es', 'es', '🇪🇸 Spain'),
        ('ricarica iliad', 'it', 'it', '🇮🇹 Italy'),
        ('recharge transcash', 'fr', 'fr', '🇫🇷 France'),
        ('buy robux', 'en', 'ph', '🇵🇭 Philippines'),
        ('neosurf voucher', 'en', 'au', '🇦🇺 Australia'),
        ('t-mobile prepaid refill', 'en', 'us', '🇺🇸 United States')
    ]
    
    sample_data = []
    
    for date in dates:
        for keyword, lang, loc, market in keywords_data:
            position = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15])
            ai_present = np.random.choice([True, False], p=[0.3, 0.7])
            
            change_options = ['Stable', 'Improved (+1)', 'Improved (+2)', 'Declined (-1)', 'Declined (-2)', 'New']
            change = np.random.choice(change_options, p=[0.4, 0.15, 0.1, 0.15, 0.1, 0.1])
            
            sample_data.append({
                'Date/Time': date.strftime('%Y-%m-%d %H:%M'),
                'Keyword': keyword,
                'Recharge Position': position,
                'Position Change': change,
                'AI Overview': 'Yes' if ai_present else 'No',
                'Sheet_Name': f'{keyword.replace(" ", "_")}_{lang}_{loc}',
                'Market': market
            })
    
    return pd.DataFrame(sample_data)

def parse_sheet_info(sheet_name):
    """Extract keyword, language, and location from sheet name"""
    clean_name = sheet_name.rstrip('_')
    parts = clean_name.split('_')
    
    if len(parts) >= 3:
        keyword = ' '.join(parts[:-2])
        language = parts[-2]
        location = parts[-1]
        return keyword, language, location
    else:
        return sheet_name, 'en', 'us'

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

def calculate_position_change(pos1, pos2):
    """Calculate position change between two positions"""
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
    
    if pos1_val is None and pos2_val is None:
        return 0, "No change (both not ranking)"
    elif pos1_val is None and pos2_val is not None:
        return float('inf'), f"New ranking at #{pos2_val}"
    elif pos1_val is not None and pos2_val is None:
        return float('-inf'), f"Lost ranking (was #{pos1_val})"
    else:
        change = pos1_val - pos2_val
        if change > 0:
            return change, f"Improved by {change} positions (#{pos1_val} → #{pos2_val})"
        elif change < 0:
            return change, f"Declined by {abs(change)} positions (#{pos1_val} → #{pos2_val})"
        else:
            return 0, f"No change (#{pos1_val})"

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
            display_data['Change_Display'] = display_data['Position Change'].fillna('Unknown')
        
        if 'AI Overview' in display_data.columns:
            display_data['AI_Display'] = display_data['AI Overview'].apply(
                lambda x: '🤖 Yes' if str(x).lower() in ['yes', 'y', 'true'] else '❌ No'
            )
        
        # Select columns for display
        display_columns = ['Keyword', 'Market', 'Position_Display', 'Change_Display', 'AI_Display']
        column_mapping = {
            'Position_Display': 'Position',
            'Change_Display': 'Change',
            'AI_Display': 'AI Overview'
        }
        
        available_cols = [col for col in display_columns if col in display_data.columns]
        if available_cols:
            table_data = display_data[available_cols].rename(columns=column_mapping)
            st.dataframe(table_data, use_container_width=True, hide_index=True)
    
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
                    'Top 3 (1-3)': '#10b981',
                    'Positions 4-10': '#f59e0b',
                    'Not Ranking': '#ef4444'
                }
            )
            fig_pie.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white'
            )
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
                    color_continuous_scale=['#10b981', '#f59e0b', '#ef4444']
                )
                fig_bar.update_layout(
                    height=400, 
                    yaxis_title="Average Position",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white',
                    xaxis=dict(color='white'),
                    yaxis=dict(color='white')
                )
                st.plotly_chart(fig_bar, use_container_width=True)

def show_keyword_tracking(df_processed, filtered_data):
    """Individual Keyword Tracking Page"""
    st.markdown('<h2 class="section-header">📈 Individual Keyword Performance</h2>', unsafe_allow_html=True)
    
    # Keyword selector
    if 'Keyword' in df_processed.columns:
        available_keywords = df_processed['Keyword'].dropna().unique()
    else:
        st.markdown('<div class="stError">❌ No "Keyword" column found in data</div>', unsafe_allow_html=True)
        return
    
    if len(available_keywords) == 0:
        st.markdown('<div class="stWarning">⚠️ No keywords found in the data.</div>', unsafe_allow_html=True)
        return
    
    selected_keyword = st.selectbox(
        "🔍 Select keyword to analyze:",
        available_keywords,
        key="keyword_selector"
    )
    
    if selected_keyword:
        # Filter data for selected keyword
        keyword_data = df_processed[df_processed['Keyword'] == selected_keyword].copy()
        
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
                    title=f'Position Tracking for "{selected_keyword}"',
                    markers=True,
                    color_discrete_sequence=['#667eea']
                )
                
                fig.update_layout(
                    yaxis=dict(autorange="reversed", color='white'),
                    height=400,
                    yaxis_title="Search Position",
                    xaxis_title="Date",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    title_font_color='white',
                    xaxis=dict(color='white')
                )
                
                fig.add_hline(y=3.5, line_dash="dash", line_color="#10b981", 
                             annotation_text="Top 3 Threshold", annotation_font_color='white')
                fig.add_hline(y=10.5, line_dash="dash", line_color="#f59e0b", 
                             annotation_text="First Page Threshold", annotation_font_color='white')
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown('<div class="stInfo">No numeric position data available for this keyword.</div>', unsafe_allow_html=True)

def show_date_comparison(df_processed):
    """Date Comparison Page with full SERP results comparison"""
    st.markdown('<h2 class="section-header">📅 SERP Results Comparison</h2>', unsafe_allow_html=True)
    
    # Get available dates
    if 'DateTime' in df_processed.columns:
        df_processed['Date'] = df_processed['DateTime'].dt.date
        available_dates = sorted(df_processed['Date'].unique())
        
        if len(available_dates) < 2:
            st.markdown('<div class="stWarning">⚠️ Need at least 2 different dates for comparison.</div>', unsafe_allow_html=True)
            st.markdown('<div class="stInfo">💡 This feature will be most useful when you have historical data spanning multiple days/weeks.</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="stWarning">⚠️ Please select two different dates for comparison.</div>', unsafe_allow_html=True)
            return
        
        # Filter data for selected dates
        data1 = df_processed[df_processed['Date'] == date1].copy()
        data2 = df_processed[df_processed['Date'] == date2].copy()
        
        if data1.empty or data2.empty:
            st.markdown('<div class="stError">❌ No data found for one or both selected dates.</div>', unsafe_allow_html=True)
            return
        
        # Keyword selector for SERP comparison
        available_keywords = list(set(data1['Keyword'].unique()) | set(data2['Keyword'].unique()))
        selected_keyword = st.selectbox(
            "🔍 Select keyword to compare SERP results:",
            available_keywords,
            key="serp_comparison_keyword"
        )
        
        if not selected_keyword:
            return
        
        # Get data for selected keyword - FIXED: Proper boolean evaluation
        kw_data1_filtered = data1[data1['Keyword'] == selected_keyword]
        kw_data2_filtered = data2[data2['Keyword'] == selected_keyword]
        
        kw_data1 = kw_data1_filtered.iloc[0] if not kw_data1_filtered.empty else None
        kw_data2 = kw_data2_filtered.iloc[0] if not kw_data2_filtered.empty else None
        
        # FIXED: Use proper None checks instead of pandas boolean evaluation
        if kw_data1 is None and kw_data2 is None:
            st.markdown('<div class="stError">❌ No data found for selected keyword on either date.</div>', unsafe_allow_html=True)
            return
        
        st.markdown(f'<h3 class="section-header">🔍 SERP Comparison for "{selected_keyword}"</h3>', unsafe_allow_html=True)
        
        # Extract SERP results for both dates
        def extract_serp_results(data_row):
            if data_row is None:
                return {}
            
            results = {}
            position_columns = ['Position 1', 'Position 2', 'Position 3', 'Position 4', 'Position 5']
            
            for i, col in enumerate(position_columns, 1):
                if col in data_row and pd.notna(data_row[col]) and data_row[col]:
                    url = str(data_row[col])
                    # Extract domain from URL for display
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        domain = domain.replace('www.', '') if domain.startswith('www.') else domain
                    except:
                        domain = url[:30] + "..." if len(url) > 30 else url
                    
                    results[i] = {
                        'url': url,
                        'domain': domain,
                        'is_recharge': 'recharge.com' in url.lower()
                    }
            
            return results
        
        serp1 = extract_serp_results(kw_data1)
        serp2 = extract_serp_results(kw_data2)
        
        # Calculate changes
        all_urls = set()
        if serp1:
            all_urls.update(result['url'] for result in serp1.values())
        if serp2:
            all_urls.update(result['url'] for result in serp2.values())
        
        # Track URL movements
        url_changes = {}
        improved_count = 0
        declined_count = 0
        new_count = 0
        lost_count = 0
        
        for url in all_urls:
            pos1 = None
            pos2 = None
            
            # Find positions
            for pos, result in serp1.items():
                if result['url'] == url:
                    pos1 = pos
                    break
            
            for pos, result in serp2.items():
                if result['url'] == url:
                    pos2 = pos
                    break
            
            # Determine change type
            if pos1 is None and pos2 is not None:
                change_type = "new"
                new_count += 1
            elif pos1 is not None and pos2 is None:
                change_type = "lost"
                lost_count += 1
            elif pos1 is not None and pos2 is not None:
                if pos1 > pos2:  # Lower position number = better ranking
                    change_type = "improved"
                    improved_count += 1
                elif pos1 < pos2:
                    change_type = "declined"
                    declined_count += 1
                else:
                    change_type = "stable"
            else:
                change_type = "stable"
            
            url_changes[url] = {
                'pos1': pos1,
                'pos2': pos2,
                'change_type': change_type
            }
        
        # Summary badges
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: #10b981; color: white; padding: 0.8rem; border-radius: 12px; text-align: center; font-weight: bold;">
                📈 Improved: {improved_count}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #ef4444; color: white; padding: 0.8rem; border-radius: 12px; text-align: center; font-weight: bold;">
                📉 Declined: {declined_count}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: #3b82f6; color: white; padding: 0.8rem; border-radius: 12px; text-align: center; font-weight: bold;">
                🆕 New: {new_count}
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: #f59e0b; color: white; padding: 0.8rem; border-radius: 12px; text-align: center; font-weight: bold;">
                ❌ Lost: {lost_count}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Side-by-side SERP comparison
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f"""
            <div style="background: #1a1a2e; border-radius: 12px; padding: 1.5rem; border: 1px solid #667eea;">
                <h3 style="text-align: center; color: #ffffff; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #667eea;">
                    📅 {date1}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Show SERP results for date1
            if serp1:
                for position in range(1, 6):
                    if position in serp1:
                        result = serp1[position]
                        border_color = "#f59e0b" if result['is_recharge'] else "#667eea"
                        
                        st.markdown(f"""
                        <div style="background: #16213e; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid {border_color}; display: flex; align-items: center;">
                            <div style="background: {border_color}; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 1rem; font-size: 14px;">
                                {position}
                            </div>
                            <div style="flex: 1;">
                                <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.9rem;">{result['domain']}</div>
                                <div style="color: #a0a9c0; font-size: 0.8rem; word-break: break-all;">{result['url'][:60]}{"..." if len(result['url']) > 60 else ""}</div>
                                {'<div style="color: #f59e0b; font-size: 0.8rem; font-weight: bold;">🔋 Recharge.com</div>' if result['is_recharge'] else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #16213e; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #6b7280; opacity: 0.5;">
                            <div style="color: #6b7280; text-align: center;">Position {position} - No data</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #6b7280; text-align: center; padding: 2rem;">No SERP data available</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown(f"""
            <div style="background: #1a1a2e; border-radius: 12px; padding: 1.5rem; border: 1px solid #667eea;">
                <h3 style="text-align: center; color: #ffffff; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #667eea;">
                    📅 {date2}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Show SERP results for date2
            if serp2:
                for position in range(1, 6):
                    if position in serp2:
                        result = serp2[position]
                        url = result['url']
                        change_info = url_changes.get(url, {})
                        change_type = change_info.get('change_type', 'stable')
                        
                        # Determine colors and change indicator
                        if change_type == "improved":
                            border_color = "#10b981"
                            change_text = f"📈 +{change_info['pos1'] - position}" if change_info.get('pos1') else "📈 UP"
                        elif change_type == "declined":
                            border_color = "#ef4444"
                            change_text = f"📉 -{position - change_info['pos1']}" if change_info.get('pos1') else "📉 DOWN"
                        elif change_type == "new":
                            border_color = "#3b82f6"
                            change_text = "🆕 NEW"
                        elif change_type == "lost":
                            border_color = "#f59e0b"
                            change_text = "❌ LOST"
                        else:
                            border_color = "#f59e0b" if result['is_recharge'] else "#667eea"
                            change_text = ""
                        
                        st.markdown(f"""
                        <div style="background: #16213e; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid {border_color}; display: flex; align-items: center;">
                            <div style="background: {border_color}; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 1rem; font-size: 14px;">
                                {position}
                            </div>
                            <div style="flex: 1;">
                                <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.9rem;">{result['domain']}</div>
                                <div style="color: #a0a9c0; font-size: 0.8rem; word-break: break-all;">{result['url'][:60]}{"..." if len(result['url']) > 60 else ""}</div>
                                {'<div style="color: #f59e0b; font-size: 0.8rem; font-weight: bold;">🔋 Recharge.com</div>' if result['is_recharge'] else ''}
                            </div>
                            {f'<div style="background: {border_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 12px; font-size: 0.8rem; font-weight: bold; margin-left: 0.5rem;">{change_text}</div>' if change_text else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #16213e; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #6b7280; opacity: 0.5;">
                            <div style="color: #6b7280; text-align: center;">Position {position} - No data</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #6b7280; text-align: center; padding: 2rem;">No SERP data available</div>', unsafe_allow_html=True)
        
        # Recharge.com Position Analysis
        st.markdown('<h3 class="section-header">🔋 Recharge.com Position Analysis</h3>', unsafe_allow_html=True)
        
        recharge_pos1 = kw_data1['Recharge Position'] if kw_data1 is not None and 'Recharge Position' in kw_data1 else None
        recharge_pos2 = kw_data2['Recharge Position'] if kw_data2 is not None and 'Recharge Position' in kw_data2 else None
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pos1_display = str(int(recharge_pos1)) if isinstance(recharge_pos1, (int, float)) else "Not Ranking"
            st.metric(f"Position on {date1}", pos1_display)
        
        with col2:
            pos2_display = str(int(recharge_pos2)) if isinstance(recharge_pos2, (int, float)) else "Not Ranking"
            st.metric(f"Position on {date2}", pos2_display)
        
        with col3:
            if isinstance(recharge_pos1, (int, float)) and isinstance(recharge_pos2, (int, float)):
                change = recharge_pos1 - recharge_pos2  # Positive = improvement
                if change > 0:
                    st.metric("Change", f"📈 +{change}", delta=f"Improved by {change} positions")
                elif change < 0:
                    st.metric("Change", f"📉 {change}", delta=f"Declined by {abs(change)} positions")
                else:
                    st.metric("Change", "➡️ No Change", delta="Position maintained")
            else:
                st.metric("Change", "❓ Unknown", delta="Missing data")
        
        # AI Overview and Full Results Data Section
        st.markdown('<h3 class="section-header">🔍 Detailed Content Analysis</h3>', unsafe_allow_html=True)
        
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            st.markdown(f'<h4 style="color: #ffffff;">📅 {date1}</h4>', unsafe_allow_html=True)
            
            if kw_data1 is not None:
                ai_status1 = "🤖 Yes" if str(kw_data1.get('AI Overview', 'No')).lower() in ['yes', 'y', 'true'] else "❌ No"
                st.markdown(f'<p style="color: #a0a9c0;">AI Overview: {ai_status1}</p>', unsafe_allow_html=True)
                
                # FIXED: Use 'AIO Links' column which contains the actual AI Overview content
                if str(kw_data1.get('AI Overview', 'No')).lower() in ['yes', 'y', 'true'] and 'AIO Links' in kw_data1:
                    with st.expander(f"🤖 AI Overview Content - {date1}", expanded=False):
                        aio_content = kw_data1.get('AIO Links', '')
                        if pd.notna(aio_content) and aio_content and str(aio_content) != '#ERROR!':
                            st.text_area(
                                f"AI Overview content for {date1}",
                                aio_content,
                                height=200,
                                key=f"aio_content_{date1}_{selected_keyword}"
                            )
                        else:
                            st.write("No AI Overview content available")
                
                if 'Full Results Data' in kw_data1:
                    with st.expander(f"📄 Full Results Data - {date1}", expanded=False):
                        full_results = kw_data1.get('Full Results Data', '')
                        if pd.notna(full_results) and full_results and str(full_results) != '#ERROR!':
                            st.text_area(
                                f"Complete search results for {date1}",
                                full_results,
                                height=300,
                                key=f"full_results_{date1}_{selected_keyword}"
                            )
                        else:
                            st.write("No full results data available")
            else:
                st.write("No data available for this date")
        
        with col_ai2:
            st.markdown(f'<h4 style="color: #ffffff;">📅 {date2}</h4>', unsafe_allow_html=True)
            
            if kw_data2 is not None:
                ai_status2 = "🤖 Yes" if str(kw_data2.get('AI Overview', 'No')).lower() in ['yes', 'y', 'true'] else "❌ No"
                st.markdown(f'<p style="color: #a0a9c0;">AI Overview: {ai_status2}</p>', unsafe_allow_html=True)
                
                # FIXED: Use 'AIO Links' column which contains the actual AI Overview content
                if str(kw_data2.get('AI Overview', 'No')).lower() in ['yes', 'y', 'true'] and 'AIO Links' in kw_data2:
                    with st.expander(f"🤖 AI Overview Content - {date2}", expanded=False):
                        aio_content = kw_data2.get('AIO Links', '')
                        if pd.notna(aio_content) and aio_content and str(aio_content) != '#ERROR!':
                            st.text_area(
                                f"AI Overview content for {date2}",
                                aio_content,
                                height=200,
                                key=f"aio_content_{date2}_{selected_keyword}"
                            )
                        else:
                            st.write("No AI Overview content available")
                
                if 'Full Results Data' in kw_data2:
                    with st.expander(f"📄 Full Results Data - {date2}", expanded=False):
                        full_results = kw_data2.get('Full Results Data', '')
                        if pd.notna(full_results) and full_results and str(full_results) != '#ERROR!':
                            st.text_area(
                                f"Complete search results for {date2}",
                                full_results,
                                height=300,
                                key=f"full_results_{date2}_{selected_keyword}"
                            )
                        else:
                            st.write("No full results data available")
            else:
                st.write("No data available for this date")
        
        # Export functionality
        st.markdown('<h3 class="section-header">📥 Export SERP Comparison</h3>', unsafe_allow_html=True)
        
        # Create detailed export data
        export_data = []
        
        # Export SERP positions
        for position in range(1, 6):
            row = {'Position': position}
            
            if position in serp1:
                row[f'URL_{date1}'] = serp1[position]['url']
                row[f'Domain_{date1}'] = serp1[position]['domain']
            else:
                row[f'URL_{date1}'] = ""
                row[f'Domain_{date1}'] = ""
            
            if position in serp2:
                row[f'URL_{date2}'] = serp2[position]['url']
                row[f'Domain_{date2}'] = serp2[position]['domain']
            else:
                row[f'URL_{date2}'] = ""
                row[f'Domain_{date2}'] = ""
            
            export_data.append(row)
        
        # Add Recharge position data
        export_data.append({
            'Position': 'Recharge.com',
            f'URL_{date1}': f'Position {recharge_pos1}' if recharge_pos1 else 'Not Ranking',
            f'Domain_{date1}': 'recharge.com',
            f'URL_{date2}': f'Position {recharge_pos2}' if recharge_pos2 else 'Not Ranking',
            f'Domain_{date2}': 'recharge.com'
        })
        
        export_df = pd.DataFrame(export_data)
        csv_data = export_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download SERP Comparison as CSV",
            data=csv_data,
            file_name=f"serp_comparison_{selected_keyword.replace(' ', '_')}_{date1}_vs_{date2}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.markdown('<div class="stError">❌ No date information found in the data.</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>🔋 RECHARGE.COM</h1>
        <h3>Advanced Ranking Tracker Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown('<h3 style="color: #ffffff;">📁 Upload Your Position Tracking Data</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose your Position tracking Excel file",
        type=['xlsx', 'xls'],
        help="Upload your Position tracking.xlsx file containing keyword ranking data"
    )
    
    if uploaded_file is not None:
        # Load data from uploaded Excel file
        with st.spinner('🔄 Loading data from Excel file...'):
            df = load_data_from_excel(uploaded_file)
    else:
        # Use sample data
        st.markdown('<p style="color: #a0a9c0;">💡 Upload your Excel file above, or use the sample data below</p>', unsafe_allow_html=True)
        df = get_sample_data()
    
    if df.empty:
        st.markdown('<div class="stError">⚠️ No data found. Please upload your Excel file.</div>', unsafe_allow_html=True)
        return
    
    # Process data
    df_processed = df.copy()
    
    # Use actual keyword from data
    if 'Keyword' in df_processed.columns:
        df_processed['Keyword_Clean'] = df_processed['Keyword']
    else:
        st.markdown('<div class="stError">❌ No "Keyword" column found in data</div>', unsafe_allow_html=True)
        return
    
    # Extract language and location from sheet names
    if 'Sheet_Name' in df_processed.columns:
        df_processed[['Keyword_From_Sheet', 'Language', 'Location']] = df_processed['Sheet_Name'].apply(
            lambda x: pd.Series(parse_sheet_info(x))
        )
        # If no Market column, create from location
        if 'Market' not in df_processed.columns:
            df_processed['Market'] = df_processed['Location'].apply(get_country_flag)
    
    # Convert datetime
    if 'Date/Time' in df_processed.columns:
        df_processed['DateTime'] = pd.to_datetime(df_processed['Date/Time'], errors='coerce')
        latest_data = df_processed.sort_values('DateTime').groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    else:
        latest_data = df_processed.groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    
    # Sidebar Navigation
    st.sidebar.markdown('<h2 style="color: #ffffff;">🎛️ Navigation</h2>', unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard Overview", "📈 Keyword Tracking", "📅 Date Comparison"],
        key="main_nav"
    )
    
    # Filters (not for Date Comparison page)
    if page != "📅 Date Comparison":
        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3 style="color: #ffffff;">🎯 Filters</h3>', unsafe_allow_html=True)
        
        # Market filter
        if 'Market' in latest_data.columns:
            markets = ['All Markets'] + sorted(latest_data['Market'].unique().tolist())
            selected_market = st.sidebar.selectbox("🌍 Market", markets)
        else:
            selected_market = 'All Markets'
        
        # Position filter
        position_options = ['All Positions', 'Top 3 (1-3)', 'Positions 4-10', 'Not Ranking']
        selected_position = st.sidebar.selectbox("📍 Position Range", position_options)
        
        # Apply filters
        filtered_data = latest_data.copy()
        
        if selected_market != 'All Markets' and 'Market' in filtered_data.columns:
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
    else:
        filtered_data = latest_data.copy()
    
    # Show some debug info
    st.sidebar.markdown("---")
    st.sidebar.markdown('<h3 style="color: #ffffff;">📊 Data Info</h3>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<p style="color: #ffffff;">Total rows: {len(df)}</p>', unsafe_allow_html=True)
    if 'Keyword' in df.columns:
        st.sidebar.markdown(f'<p style="color: #ffffff;">Unique keywords: {df["Keyword"].nunique()}</p>', unsafe_allow_html=True)
    
    # Page routing
    if page == "📊 Dashboard Overview":
        show_dashboard_overview(latest_data, filtered_data)
    elif page == "📈 Keyword Tracking":
        show_keyword_tracking(df_processed, filtered_data)
    elif page == "📅 Date Comparison":
        show_date_comparison(df_processed)

if __name__ == "__main__":
    main()
