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
    """Date Comparison Page with visual SERP-style layout"""
    st.markdown('<h2 class="section-header">📅 Date Comparison Analysis</h2>', unsafe_allow_html=True)
    
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
        
        # Perform comparison
        st.markdown(f'<h3 class="section-header">📊 SERP Comparison: {date1} vs {date2}</h3>', unsafe_allow_html=True)
        
        # Summary badges
        all_keywords = set(data1['Keyword'].unique()) | set(data2['Keyword'].unique())
        
        # Calculate changes
        improved_count = 0
        declined_count = 0
        new_count = 0
        lost_count = 0
        
        comparison_data = []
        for keyword in all_keywords:
            kw_data1 = data1[data1['Keyword'] == keyword]
            kw_data2 = data2[data2['Keyword'] == keyword]
            
            pos1 = kw_data1['Recharge Position'].iloc[0] if not kw_data1.empty else None
            pos2 = kw_data2['Recharge Position'].iloc[0] if not kw_data2.empty else None
            
            market = kw_data1['Market'].iloc[0] if not kw_data1.empty else (kw_data2['Market'].iloc[0] if not kw_data2.empty else 'Unknown')
            
            change_val, change_desc = calculate_position_change(pos1, pos2)
            
            if change_val == float('inf'):
                new_count += 1
                change_type = "new"
            elif change_val == float('-inf'):
                lost_count += 1
                change_type = "lost"
            elif change_val > 0:
                improved_count += 1
                change_type = "improved"
            elif change_val < 0:
                declined_count += 1
                change_type = "declined"
            else:
                change_type = "stable"
            
            comparison_data.append({
                'keyword': keyword,
                'market': market,
                'pos1': pos1,
                'pos2': pos2,
                'change_val': change_val,
                'change_desc': change_desc,
                'change_type': change_type
            })
        
        # Summary badges
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; margin: 1rem 0;">
            <span style="background: #10b981; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                Improved {improved_count}
            </span>
            <span style="background: #ef4444; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                Declined {declined_count}
            </span>
            <span style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                New {new_count}
            </span>
            <span style="background: #f59e0b; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                Lost {lost_count}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Visual SERP-style comparison
        st.markdown("""
        <style>
        .serp-comparison {
            display: flex;
            gap: 2rem;
            margin: 2rem 0;
        }
        
        .serp-column {
            flex: 1;
            background: #1a1a2e;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #667eea;
        }
        
        .serp-header {
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }
        
        .serp-item {
            display: flex;
            align-items: center;
            margin: 0.8rem 0;
            padding: 0.8rem;
            background: #16213e;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .serp-item.improved {
            border-left-color: #10b981;
            background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, #16213e 100%);
        }
        
        .serp-item.declined {
            border-left-color: #ef4444;
            background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, #16213e 100%);
        }
        
        .serp-item.new {
            border-left-color: #3b82f6;
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, #16213e 100%);
        }
        
        .serp-item.lost {
            border-left-color: #f59e0b;
            background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, #16213e 100%);
        }
        
        .position-number {
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 1rem;
            flex-shrink: 0;
        }
        
        .position-number.improved {
            background: #10b981;
        }
        
        .position-number.declined {
            background: #ef4444;
        }
        
        .position-number.new {
            background: #3b82f6;
        }
        
        .position-number.lost {
            background: #f59e0b;
        }
        
        .position-number.not-ranking {
            background: #6b7280;
        }
        
        .keyword-info {
            flex: 1;
        }
        
        .keyword-title {
            color: #ffffff;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        
        .keyword-market {
            color: #a0a9c0;
            font-size: 0.9rem;
        }
        
        .change-indicator {
            font-size: 0.8rem;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            margin-left: 0.5rem;
        }
        
        .change-indicator.improved {
            background: #10b981;
            color: white;
        }
        
        .change-indicator.declined {
            background: #ef4444;
            color: white;
        }
        
        .change-indicator.new {
            background: #3b82f6;
            color: white;
        }
        
        .change-indicator.lost {
            background: #f59e0b;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create SERP-style layout
        html_content = f"""
        <div class="serp-comparison">
            <div class="serp-column">
                <div class="serp-header">{date1}</div>
        """
        
        # Sort keywords by position for date1
        date1_sorted = sorted(comparison_data, key=lambda x: x['pos1'] if isinstance(x['pos1'], (int, float)) else 999)
        
        for item in date1_sorted:
            pos1 = item['pos1']
            pos_display = str(pos1) if isinstance(pos1, (int, float)) else "NR"
            pos_class = "not-ranking" if not isinstance(pos1, (int, float)) else ""
            
            html_content += f"""
                <div class="serp-item">
                    <div class="position-number {pos_class}">{pos_display}</div>
                    <div class="keyword-info">
                        <div class="keyword-title">{item['keyword']}</div>
                        <div class="keyword-market">{item['market']}</div>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
            <div class="serp-column">
        """
        
        html_content += f'<div class="serp-header">{date2}</div>'
        
        # Sort keywords by position for date2
        date2_sorted = sorted(comparison_data, key=lambda x: x['pos2'] if isinstance(x['pos2'], (int, float)) else 999)
        
        for item in date2_sorted:
            pos2 = item['pos2']
            pos_display = str(pos2) if isinstance(pos2, (int, float)) else "NR"
            change_type = item['change_type']
            
            change_text = ""
            if change_type == "improved":
                change_text = f"↗ +{item['change_val']}"
            elif change_type == "declined":
                change_text = f"↘ {item['change_val']}"
            elif change_type == "new":
                change_text = "NEW"
            elif change_type == "lost":
                change_text = "LOST"
            
            html_content += f"""
                <div class="serp-item {change_type}">
                    <div class="position-number {change_type}">{pos_display}</div>
                    <div class="keyword-info">
                        <div class="keyword-title">{item['keyword']}</div>
                        <div class="keyword-market">{item['market']}</div>
                    </div>
                    {f'<div class="change-indicator {change_type}">{change_text}</div>' if change_text else ''}
                </div>
            """
        
        html_content += """
            </div>
        </div>
        """
        
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Export comparison results
        st.markdown('<h3 class="section-header">📥 Export Results</h3>', unsafe_allow_html=True)
        
        # Create DataFrame for export
        export_df = pd.DataFrame(comparison_data)
        export_df = export_df[['keyword', 'market', 'pos1', 'pos2', 'change_desc']].copy()
        export_df.columns = ['Keyword', 'Market', f'Position {date1}', f'Position {date2}', 'Change']
        
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Comparison Results as CSV",
            data=csv_data,
            file_name=f"ranking_comparison_{date1}_vs_{date2}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
