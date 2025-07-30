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
                
                # Don't filter by Keyword column existence, just add all sheets
                all_data.append(df_sheet)
                    
            except Exception as e:
                st.warning(f"Error reading sheet {sheet_name}: {e}")
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
        ('t-mobile prepaid refill number', 'en', 'us', '🇺🇸 United States'),
        ('recarga digi', 'es', 'es', '🇪🇸 Spain'),
        ('recarga digi online', 'es', 'es', '🇪🇸 Spain'),
        ('ricarica iliad', 'it', 'it', '🇮🇹 Italy'),
        ('ricarica iliad online', 'it', 'it', '🇮🇹 Italy'),
        ('recharge transcash', 'fr', 'fr', '🇫🇷 France'),
        ('transcash en ligne', 'fr', 'fr', '🇫🇷 France'),
        ('buy robux', 'en', 'ph', '🇵🇭 Philippines'),
        ('robux top up', 'en', 'ph', '🇵🇭 Philippines'),
        ('flexy mobilis', 'fr', 'dz', '🇩🇿 Algeria'),
        ('flexy mobilis en ligne', 'fr', 'dz', '🇩🇿 Algeria'),
        ('neosurf', 'en', 'au', '🇦🇺 Australia'),
        ('neosurf voucher', 'en', 'au', '🇦🇺 Australia'),
        ('buy neosurf online', 'en', 'au', '🇦🇺 Australia')
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
                'AI Overview': f"Sample AI Overview content for {keyword}" if ai_present else None,
                'AIO Links': f"Sample AI Overview links for {keyword}" if ai_present else None,
                'Full Results Data': f"Sample SERP data for {keyword}",
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

def has_ai_overview(ai_content):
    """Check if AI Overview content exists"""
    if pd.isna(ai_content) or not ai_content or str(ai_content) == '#ERROR!' or str(ai_content).strip() == '':
        return False
    return True

def extract_aio_links(aio_links_content):
    """Extract links from AIO Links content"""
    if pd.isna(aio_links_content) or not aio_links_content or str(aio_links_content) == '#ERROR!':
        return []
    
    content = str(aio_links_content)
    links = []
    
    # Look for numbered links (1. https://...)
    # Pattern for numbered links like "1. https://... - Title"
    numbered_pattern = r'\d+\.\s+(https?://[^\s]+)'
    found_urls = re.findall(numbered_pattern, content)
    
    for url in found_urls:
        # Clean up URL (remove trailing punctuation and fragments)
        clean_url = url.split('#')[0].rstrip('.,;:)')
        if clean_url not in links:
            links.append(clean_url)
    
    return links

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
        
        # FIXED: Check for AI Overview content existence instead of Yes/No
        ai_count = len(latest_data[
            latest_data['AI Overview'].apply(has_ai_overview)
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
    
    # Keywords Overview Table with AI Overview Content
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
        
        # FIXED: Check AI Overview content instead of Yes/No
        if 'AI Overview' in display_data.columns:
            display_data['AI_Display'] = display_data['AI Overview'].apply(
                lambda x: '🤖 Yes' if has_ai_overview(x) else '❌ No'
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
        
        # AI Overview Content Display
        if 'AI Overview' in display_data.columns:
            ai_keywords = display_data[display_data['AI Overview'].apply(has_ai_overview)]
            
            if not ai_keywords.empty:
                st.markdown('<h3 class="section-header">🤖 AI Overview Content</h3>', unsafe_allow_html=True)
                
                # Show AI Overview content for keywords that have it
                for idx, row in ai_keywords.iterrows():
                    keyword = row.get('Keyword', 'Unknown')
                    position = row.get('Recharge Position', 'Unknown')
                    ai_content = row.get('AI Overview', '')
                    
                    if has_ai_overview(ai_content):
                        with st.expander(f"🔍 {keyword} (Position: {position})", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown("**🤖 AI Overview Content:**")
                                st.text_area(
                                    "AI Overview",
                                    ai_content,
                                    height=150,
                                    key=f"ai_overview_{idx}",
                                    label_visibility="collapsed"
                                )
                            
                            with col2:
                                st.markdown("**📊 Details:**")
                                st.write(f"**Keyword:** {keyword}")
                                st.write(f"**Position:** {position}")
                                st.write(f"**Market:** {row.get('Market', 'Unknown')}")
                                
                                # Show AI Overview links if available
                                if 'AIO Links' in row:
                                    links = extract_aio_links(row['AIO Links'])
                                    if links:
                                        st.markdown("**🔗 Links:**")
                                        for i, link in enumerate(links[:3], 1):
                                            try:
                                                domain = urlparse(link).netloc.replace('www.', '')
                                            except:
                                                domain = link[:20] + "..."
                                            st.markdown(f"{i}. [{domain}]({link})")
                                    else:
                                        st.write("**🔗 Links:** None found")
    
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
        available_keywords = sorted(df_processed['Keyword'].dropna().unique())
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
                ai_status = latest_row.get('AI Overview', '')
                ai_display = '🤖 Yes' if has_ai_overview(ai_status) else '❌ No'
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

def show_ai_overview_tracking(df_processed):
    """AI Overview Tracking Page"""
    st.markdown('<h2 class="section-header">🤖 AI Overview Tracking</h2>', unsafe_allow_html=True)
    
    # Filter data to only show records with AI Overview content
    if 'AI Overview' in df_processed.columns:
        ai_data = df_processed[
            df_processed['AI Overview'].apply(has_ai_overview)
        ].copy()
    else:
        st.markdown('<div class="stError">❌ No "AI Overview" column found in data</div>', unsafe_allow_html=True)
        return
    
    if ai_data.empty:
        st.markdown('<div class="stWarning">⚠️ No AI Overview data found in the dataset.</div>', unsafe_allow_html=True)
        return
    
    # Summary metrics
    st.markdown('<h3 class="section-header">📊 AI Overview Summary</h3>', unsafe_allow_html=True)
    
    if 'DateTime' in ai_data.columns:
        ai_data['Date'] = ai_data['DateTime'].dt.date
        latest_ai_data = ai_data.sort_values('DateTime').groupby('Keyword').tail(1).reset_index(drop=True)
    else:
        latest_ai_data = ai_data.groupby('Keyword').tail(1).reset_index(drop=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_keywords_with_ai = latest_ai_data['Keyword'].nunique()
        st.metric("Keywords with AI Overview", total_keywords_with_ai)
    
    with col2:
        total_ai_records = len(ai_data)
        st.metric("Total AI Overview Records", total_ai_records)
    
    with col3:
        if 'DateTime' in ai_data.columns:
            unique_dates = ai_data['Date'].nunique()
            st.metric("Days with AI Overview Data", unique_dates)
    
    with col4:
        avg_position = latest_ai_data['Recharge Position'].apply(
            lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else None
        ).mean()
        if not pd.isna(avg_position):
            st.metric("Avg Position (AI Keywords)", f"{avg_position:.1f}")
    
    # Keywords with AI Overview table
    st.markdown('<h3 class="section-header">🔍 Keywords with AI Overview</h3>', unsafe_allow_html=True)
    
    if not latest_ai_data.empty:
        display_data = latest_ai_data.copy()
        
        # Format data for display
        if 'Recharge Position' in display_data.columns:
            display_data['Position_Display'] = display_data['Recharge Position'].apply(
                lambda x: get_position_status(x)[0]
            )
        
        if 'Position Change' in display_data.columns:
            display_data['Change_Display'] = display_data['Position Change'].fillna('Unknown')
        
        # Select columns for display
        display_columns = ['Keyword', 'Market', 'Position_Display', 'Change_Display']
        column_mapping = {
            'Position_Display': 'Position',
            'Change_Display': 'Latest Change'
        }
        
        available_cols = [col for col in display_columns if col in display_data.columns]
        if available_cols:
            table_data = display_data[available_cols].rename(columns=column_mapping)
            st.dataframe(table_data, use_container_width=True, hide_index=True)
    
    # Keyword selector for detailed AI analysis
    st.markdown('<h3 class="section-header">📋 Detailed AI Overview Analysis</h3>', unsafe_allow_html=True)
    
    available_ai_keywords = sorted(ai_data['Keyword'].unique())
    selected_ai_keyword = st.selectbox(
        "🔍 Select keyword for AI Overview analysis:",
        available_ai_keywords,
        key="ai_keyword_selector"
    )
    
    if selected_ai_keyword:
        keyword_ai_data = ai_data[ai_data['Keyword'] == selected_ai_keyword].copy()
        
        if 'DateTime' in keyword_ai_data.columns:
            keyword_ai_data = keyword_ai_data.sort_values('DateTime')
        
        # Show AI Overview content for each date
        st.markdown(f'<h4 style="color: #ffffff;">🤖 AI Overview Content History for "{selected_ai_keyword}"</h4>', unsafe_allow_html=True)
        
        for idx, row in keyword_ai_data.iterrows():
            date_str = row.get('DateTime', 'Unknown Date')
            if hasattr(date_str, 'strftime'):
                date_display = date_str.strftime('%b %d, %Y at %I:%M:%S %p')
            else:
                date_display = str(date_str)
            
            position = row.get('Recharge Position', 'Unknown')
            
            with st.expander(f"📅 {date_display} - Position: {position}", expanded=False):
                col_content, col_links = st.columns([2, 1])
                
                with col_content:
                    st.markdown("**🤖 AI Overview Content:**")
                    aio_content = row.get('AI Overview', '')
                    if has_ai_overview(aio_content):
                        st.text_area(
                            f"AI Overview content",
                            aio_content,
                            height=200,
                            key=f"ai_content_{idx}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.write("No AI Overview content available")
                
                with col_links:
                    st.markdown("**🔗 Extracted Links:**")
                    links = extract_aio_links(row.get('AIO Links', ''))
                    if links:
                        for i, link in enumerate(links, 1):
                            # Extract domain for display
                            try:
                                domain = urlparse(link).netloc.replace('www.', '')
                            except:
                                domain = link[:30] + "..." if len(link) > 30 else link
                            st.markdown(f"{i}. [{domain}]({link})")
                    else:
                        st.write("No links found")
                
                # Show original SERP positions
                st.markdown("**📊 Original SERP Positions:**")
                positions_data = []
                for pos in range(1, 6):
                    col_name = f'Position {pos}'
                    if col_name in row and pd.notna(row[col_name]) and row[col_name]:
                        url = str(row[col_name])
                        # Extract domain
                        try:
                            domain = urlparse(url).netloc.replace('www.', '')
                        except:
                            domain = url[:50] + "..." if len(url) > 50 else url
                        
                        is_recharge = 'recharge.com' in url.lower()
                        positions_data.append({
                            'Position': pos,
                            'Domain': domain,
                            'URL': url,
                            'Is Recharge': '🔋 Yes' if is_recharge else '❌ No'
                        })
                
                if positions_data:
                    positions_df = pd.DataFrame(positions_data)
                    st.dataframe(positions_df, use_container_width=True, hide_index=True)
        
        # AI Overview Links Table
        st.markdown('<h4 style="color: #ffffff;">🔗 All AI Overview Links for this Keyword</h4>', unsafe_allow_html=True)
        
        all_links = []
        for idx, row in keyword_ai_data.iterrows():
            date_str = row.get('DateTime', 'Unknown Date')
            if hasattr(date_str, 'strftime'):
                date_display = date_str.strftime('%b %d, %Y at %I:%M:%S %p')
            else:
                date_display = str(date_str)
            
            links = extract_aio_links(row.get('AIO Links', ''))
            for link in links:
                try:
                    domain = urlparse(link).netloc.replace('www.', '')
                except:
                    domain = link[:50]
                    
                all_links.append({
                    'Date': date_display,
                    'URL': link,
                    'Domain': domain
                })
        
        if all_links:
            links_df = pd.DataFrame(all_links)
            st.dataframe(links_df, use_container_width=True, hide_index=True)
        else:
            st.write("No links found in AI Overview content")

def show_date_comparison(df_processed):
    """Date Comparison Page with full SERP results comparison"""
    st.markdown('<h2 class="section-header">📅 SERP Results Comparison</h2>', unsafe_allow_html=True)
    
    # Keyword selector first
    if 'Keyword' in df_processed.columns:
        available_keywords = sorted(df_processed['Keyword'].unique())
        selected_keyword = st.selectbox(
            "🔍 Select keyword to compare SERP results:",
            available_keywords,
            key="serp_comparison_keyword"
        )
    else:
        st.markdown('<div class="stError">❌ No "Keyword" column found in data</div>', unsafe_allow_html=True)
        return
    
    if not selected_keyword:
        return
    
    # Get available datetimes for selected keyword only - Show actual times from data
    if 'DateTime' in df_processed.columns:
        keyword_data = df_processed[df_processed['Keyword'] == selected_keyword].copy()
        available_datetimes = sorted(keyword_data['DateTime'].dropna().unique())
        
        if len(available_datetimes) < 2:
            st.markdown('<div class="stWarning">⚠️ Need at least 2 different times for comparison for this keyword.</div>', unsafe_allow_html=True)
            st.markdown('<div class="stInfo">💡 This feature will be most useful when you have multiple data points.</div>', unsafe_allow_html=True)
            
            # Show what times we do have for this keyword
            if len(available_datetimes) > 0:
                st.markdown('<h4 style="color: #ffffff;">Available data times for this keyword:</h4>', unsafe_allow_html=True)
                for dt in available_datetimes:
                    if hasattr(dt, 'strftime'):
                        st.markdown(f'<p style="color: #a0a9c0;">📅 {dt.strftime("%b %d, %Y at %I:%M:%S %p")}</p>', unsafe_allow_html=True)
            return
        
        # Convert to readable format for display - show actual times with more detail
        datetime_options = []
        for dt in available_datetimes:
            if hasattr(dt, 'strftime'):
                # Format: "Jul 30, 2025 at 10:19:18 AM" 
                display_time = dt.strftime('%b %d, %Y at %I:%M:%S %p')
                datetime_options.append((display_time, dt))
        
        st.markdown(f'<p style="color: #10b981;">✅ Found {len(datetime_options)} data points for "{selected_keyword}"</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_dt1_display = st.selectbox(
                "📅 Select First Time (Baseline)",
                options=[opt[0] for opt in datetime_options],
                index=0,
                key="datetime1"
            )
            # Get the actual datetime object
            selected_dt1 = next(opt[1] for opt in datetime_options if opt[0] == selected_dt1_display)
        
        with col2:
            selected_dt2_display = st.selectbox(
                "📅 Select Second Time (Comparison)",
                options=[opt[0] for opt in datetime_options],
                index=len(datetime_options)-1,
                key="datetime2"
            )
            # Get the actual datetime object
            selected_dt2 = next(opt[1] for opt in datetime_options if opt[0] == selected_dt2_display)
        
        if selected_dt1 == selected_dt2:
            st.markdown('<div class="stWarning">⚠️ Please select two different times for comparison.</div>', unsafe_allow_html=True)
            return
        
        # Filter data for selected datetimes and keyword
        data1 = keyword_data[keyword_data['DateTime'] == selected_dt1].copy()
        data2 = keyword_data[keyword_data['DateTime'] == selected_dt2].copy()
        
        if data1.empty or data2.empty:
            st.markdown('<div class="stError">❌ No data found for one or both selected times for this keyword.</div>', unsafe_allow_html=True)
            return
        
        # Get data for selected keyword
        kw_data1 = data1.iloc[0] if not data1.empty else None
        kw_data2 = data2.iloc[0] if not data2.empty else None
        
        if kw_data1 is None and kw_data2 is None:
            st.markdown('<div class="stError">❌ No data found for selected keyword at either time.</div>', unsafe_allow_html=True)
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
                    📅 {selected_dt1.strftime('%b %d, %Y at %I:%M %p')}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Show SERP results for datetime1
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
                    📅 {selected_dt2.strftime('%b %d, %Y at %I:%M %p')}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Show SERP results for datetime2
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
            st.metric(f"Position at {selected_dt1.strftime('%b %d, %I:%M %p')}", pos1_display)
        
        with col2:
            pos2_display = str(int(recharge_pos2)) if isinstance(recharge_pos2, (int, float)) else "Not Ranking"
            st.metric(f"Position at {selected_dt2.strftime('%b %d, %I:%M %p')}", pos2_display)
        
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
            st.markdown(f'<h4 style="color: #ffffff;">📅 {selected_dt1.strftime("%b %d, %Y at %I:%M %p")}</h4>', unsafe_allow_html=True)
            
            if kw_data1 is not None:
                ai_content1 = kw_data1.get('AI Overview', '')
                ai_status1 = "🤖 Yes" if has_ai_overview(ai_content1) else "❌ No"
                st.markdown(f'<p style="color: #a0a9c0;">AI Overview: {ai_status1}</p>', unsafe_allow_html=True)
                
                if has_ai_overview(ai_content1):
                    with st.expander(f"🤖 AI Overview Content - {selected_dt1_display}", expanded=False):
                        st.text_area(
                            f"AI Overview content",
                            ai_content1,
                            height=200,
                            key=f"aio_content_1_{selected_keyword}",
                            label_visibility="collapsed"
                        )
                
                if 'Full Results Data' in kw_data1:
                    with st.expander(f"📄 Full Results Data - {selected_dt1_display}", expanded=False):
                        full_results = kw_data1.get('Full Results Data', '')
                        if pd.notna(full_results) and full_results and str(full_results) != '#ERROR!':
                            st.text_area(
                                f"Complete search results",
                                full_results,
                                height=300,
                                key=f"full_results_1_{selected_keyword}",
                                label_visibility="collapsed"
                            )
                        else:
                            st.write("No full results data available")
            else:
                st.write("No data available for this time")
        
        with col_ai2:
            st.markdown(f'<h4 style="color: #ffffff;">📅 {selected_dt2.strftime("%b %d, %Y at %I:%M %p")}</h4>', unsafe_allow_html=True)
            
            if kw_data2 is not None:
                ai_content2 = kw_data2.get('AI Overview', '')
                ai_status2 = "🤖 Yes" if has_ai_overview(ai_content2) else "❌ No"
                st.markdown(f'<p style="color: #a0a9c0;">AI Overview: {ai_status2}</p>', unsafe_allow_html=True)
                
                if has_ai_overview(ai_content2):
                    with st.expander(f"🤖 AI Overview Content - {selected_dt2_display}", expanded=False):
                        st.text_area(
                            f"AI Overview content",
                            ai_content2,
                            height=200,
                            key=f"aio_content_2_{selected_keyword}",
                            label_visibility="collapsed"
                        )
                
                if 'Full Results Data' in kw_data2:
                    with st.expander(f"📄 Full Results Data - {selected_dt2_display}", expanded=False):
                        full_results = kw_data2.get('Full Results Data', '')
                        if pd.notna(full_results) and full_results and str(full_results) != '#ERROR!':
                            st.text_area(
                                f"Complete search results",
                                full_results,
                                height=300,
                                key=f"full_results_2_{selected_keyword}",
                                label_visibility="collapsed"
                            )
                        else:
                            st.write("No full results data available")
            else:
                st.write("No data available for this time")
        
        # Export functionality
        st.markdown('<h3 class="section-header">📥 Export SERP Comparison</h3>', unsafe_allow_html=True)
        
        # Create detailed export data
        export_data = []
        
        # Export SERP positions
        for position in range(1, 6):
            row = {'Position': position}
            
            if position in serp1:
                row[f'URL_{selected_dt1_display}'] = serp1[position]['url']
                row[f'Domain_{selected_dt1_display}'] = serp1[position]['domain']
            else:
                row[f'URL_{selected_dt1_display}'] = ""
                row[f'Domain_{selected_dt1_display}'] = ""
            
            if position in serp2:
                row[f'URL_{selected_dt2_display}'] = serp2[position]['url']
                row[f'Domain_{selected_dt2_display}'] = serp2[position]['domain']
            else:
                row[f'URL_{selected_dt2_display}'] = ""
                row[f'Domain_{selected_dt2_display}'] = ""
            
            export_data.append(row)
        
        # Add Recharge position data
        export_data.append({
            'Position': 'Recharge.com',
            f'URL_{selected_dt1_display}': f'Position {recharge_pos1}' if recharge_pos1 else 'Not Ranking',
            f'Domain_{selected_dt1_display}': 'recharge.com',
            f'URL_{selected_dt2_display}': f'Position {recharge_pos2}' if recharge_pos2 else 'Not Ranking',
            f'Domain_{selected_dt2_display}': 'recharge.com'
        })
        
        export_df = pd.DataFrame(export_data)
        csv_data = export_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download SERP Comparison as CSV",
            data=csv_data,
            file_name=f"serp_comparison_{selected_keyword.replace(' ', '_')}_{selected_dt1.strftime('%Y%m%d_%H%M%S')}_vs_{selected_dt2.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.markdown('<div class="stError">❌ No datetime information found in the data.</div>', unsafe_allow_html=True)

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
    
    # Add helpful info about expected format
    with st.expander("💡 Expected File Format", expanded=False):
        st.markdown("""
        **Expected Excel file structure:**
        - Multiple sheets (one per keyword)
        - Each sheet should have columns like: `Date/Time`, `Keyword`, `Recharge Position`, `AI Overview`, etc.
        - Date/Time formats supported: `7/30/2025, 10:19:18 AM`, `7/30/2025 10:19:18 AM`, `2025-07-30 10:19:18`
        """)
    
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
    
    # Initialize parsing_info
    parsing_info = None
    
    # Convert datetime - DIRECT approach for exact Excel column parsing
    if 'Date/Time' in df_processed.columns:
        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3 style="color: #ffffff;">🔍 Raw Date/Time Data</h3>', unsafe_allow_html=True)
        
        # Show first few raw values exactly as they are in Excel
        raw_samples = df_processed['Date/Time'].dropna().head(5).tolist()
        for i, raw_date in enumerate(raw_samples):
            st.sidebar.markdown(f'<p style="color: #a0a9c0; font-size: 11px;">Row {i+1}: "{raw_date}" (type: {type(raw_date).__name__})</p>', unsafe_allow_html=True)
        
        # Simple parsing - let pandas handle it directly
        def parse_excel_datetime(date_val):
            if pd.isna(date_val):
                return pd.NaT
            
            # If it's already a datetime object from Excel, return as-is
            if isinstance(date_val, (pd.Timestamp, datetime.datetime)):
                return pd.Timestamp(date_val)
            
            # Convert to string and try parsing
            date_str = str(date_val).strip()
            
            # Try pandas with different settings
            try:
                # First try - let pandas infer everything
                result = pd.to_datetime(date_str, errors='coerce', infer_datetime_format=True)
                if pd.notna(result):
                    return result
            except:
                pass
            
            # Manual format matching for your specific format
            # Pattern: 7/30/2025, 10:19:18 AM
            pattern = r'(\d{1,2})/(\d{1,2})/(\d{4}),?\s+(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)'
            match = re.match(pattern, date_str)
            
            if match:
                month, day, year, hour, minute, second, ampm = match.groups()
                hour = int(hour)
                if ampm.upper() == 'PM' and hour != 12:
                    hour += 12
                elif ampm.upper() == 'AM' and hour == 12:
                    hour = 0
                
                try:
                    dt = datetime.datetime(int(year), int(month), int(day), hour, int(minute), int(second))
                    return pd.Timestamp(dt)
                except:
                    pass
            
            return pd.NaT
        
        # Apply parsing
        df_processed['DateTime'] = df_processed['Date/Time'].apply(parse_excel_datetime)
        
        # Check results
        successful = df_processed['DateTime'].notna().sum()
        total = len(df_processed)
        failed = total - successful
        
        st.sidebar.markdown(f'<p style="color: #10b981; font-size: 12px;">✅ Parsed: {successful}/{total}</p>', unsafe_allow_html=True)
        if failed > 0:
            st.sidebar.markdown(f'<p style="color: #ef4444; font-size: 12px;">❌ Failed: {failed}</p>', unsafe_allow_html=True)
        
        # Show parsed results
        if successful > 0:
            parsed_samples = df_processed[df_processed['DateTime'].notna()]['DateTime'].head(3)
            st.sidebar.markdown('<p style="color: #10b981; font-size: 11px;">Parsed results:</p>', unsafe_allow_html=True)
            for i, parsed_dt in enumerate(parsed_samples):
                formatted = parsed_dt.strftime('%m/%d/%Y %I:%M:%S %p')
                st.sidebar.markdown(f'<p style="color: #10b981; font-size: 11px;">✅ {formatted}</p>', unsafe_allow_html=True)
        
        # Remove failed parsing rows
        df_processed = df_processed.dropna(subset=['DateTime'])
        latest_data = df_processed.sort_values('DateTime').groupby('Keyword_Clean').tail(1).reset_index(drop=True)
        
        parsing_info = {
            'successful_parse': successful,
            'total_rows': total,
            'removed_rows': failed
        }
    else:
        parsing_info = None
        latest_data = df_processed.groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    
    # Sidebar Navigation
    st.sidebar.markdown('<h2 style="color: #ffffff;">🎛️ Navigation</h2>', unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard Overview", "📈 Keyword Tracking", "🤖 AI Overview Tracking", "📅 Date Comparison"],
        key="main_nav"
    )
    
    # Filters (not for Date Comparison or AI Overview pages)
    if page not in ["📅 Date Comparison", "🤖 AI Overview Tracking"]:
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
    
    # Show datetime parsing debug info
    if parsing_info:
        st.sidebar.markdown('<h3 style="color: #ffffff;">🔍 DateTime Parsing</h3>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<p style="color: #a0a9c0; font-size: 12px;">Parsed: {parsing_info["successful_parse"]}/{parsing_info["total_rows"]} dates</p>', unsafe_allow_html=True)
        
        if parsing_info["removed_rows"] > 0:
            st.sidebar.markdown(f'<p style="color: #f59e0b; font-size: 12px;">⚠️ Removed {parsing_info["removed_rows"]} rows with invalid dates</p>', unsafe_allow_html=True)
    
    # Page routing
    if page == "📊 Dashboard Overview":
        show_dashboard_overview(latest_data, filtered_data)
    elif page == "📈 Keyword Tracking":
        show_keyword_tracking(df_processed, filtered_data)
    elif page == "🤖 AI Overview Tracking":
        show_ai_overview_tracking(df_processed)
    elif page == "📅 Date Comparison":
        show_date_comparison(df_processed)

if __name__ == "__main__":
    main()
