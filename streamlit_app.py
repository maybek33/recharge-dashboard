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
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div > select {
        background-color: #f8f9fa;
    }
    h1 {
        color: #1a237e;
        text-align: center;
        margin-bottom: 2rem;
    }
    .dataframe {
        border: none !important;
    }
    .stDataFrame > div {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets connection
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_sheets():
    """Load data from Google Sheets"""
    try:
        # Set up credentials (you'll need to add your service account key)
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Load credentials from Streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        
        # Connect to Google Sheets
        gc = gspread.authorize(credentials)
        
        # Open the spreadsheet by URL
        sheet_url = "https://docs.google.com/spreadsheets/d/1hOMEaZ_zfliPxJ7N-9EJ64KvyRl9J-feoR30GB-bI_o/edit"
        spreadsheet = gc.open_by_url(sheet_url)
        
        # Get all worksheet names
        worksheets = spreadsheet.worksheets()
        
        # Filter out the main admin sheet and get keyword sheets
        keyword_sheets = [ws for ws in worksheets if ws.title not in ['Main', 'ADMIN', '⚙️ ADMIN']]
        
        # Combine data from all keyword sheets
        all_data = []
        
        for sheet in keyword_sheets:
            try:
                # Get all data from the sheet
                data = sheet.get_all_records()
                if data:  # If sheet has data
                    df = pd.DataFrame(data)
                    df['Sheet_Name'] = sheet.title
                    all_data.append(df)
            except Exception as e:
                st.error(f"Error reading sheet {sheet.title}: {e}")
                continue
        
        if all_data:
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        # Return sample data for demo purposes
        return get_sample_data()

def get_sample_data():
    """Sample data for demo purposes"""
    return pd.DataFrame({
        'Date/Time': ['2024-01-15 14:30', '2024-01-15 14:31', '2024-01-15 14:32'],
        'Keyword': ['recarga digi', 'ricarica iliad', 'recharge transcash'],
        'Position 1': ['https://www.digimobil.es/recargar', 'https://www.iliad.it/ricarica', 'https://www.transcash.fr/recharge'],
        'Recharge URL': ['https://www.recharge.com/es/es/digimobil', '', 'https://www.recharge.com/fr/fr/transcash'],
        'Recharge Position': [2, 'Not Ranking', 7],
        'Position Change': ['Improved (+1)', 'Lost', 'Declined (-2)'],
        'AI Overview': ['No', 'Yes', 'Yes'],
        'AIO Links': ['', 'https://example.com/ai1', 'https://example.com/ai2'],
        'Sheet_Name': ['recarga_digi_es_es', 'ricarica_iliad_it_it', 'recharge_transcash_fr_fr']
    })

def parse_sheet_info(sheet_name):
    """Extract keyword, language, and location from sheet name"""
    parts = sheet_name.split('_')
    if len(parts) >= 3:
        keyword = parts[0].replace('_', ' ')
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
        return 'Not Ranking', '#dc3545'
    try:
        pos = int(position)
        if pos <= 3:
            return f'#{pos}', '#28a745'
        elif pos <= 10:
            return f'#{pos}', '#ffc107'
        else:
            return f'#{pos}', '#fd7e14'
    except:
        return str(position), '#6c757d'

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

# Main dashboard
def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 2rem; color: white;'>
        <h1 style='color: white; margin: 0;'>🔋 RECHARGE.COM</h1>
        <h3 style='color: white; margin: 0; font-weight: 300;'>Ranking Tracker Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data from Google Sheets...'):
        df = load_data_from_sheets()
    
    if df.empty:
        st.warning("No data found. Please check your Google Sheets connection.")
        return
    
    # Process data
    df_processed = df.copy()
    
    # Extract keyword, language, location from sheet names
    df_processed[['Keyword_Clean', 'Language', 'Location']] = df_processed['Sheet_Name'].apply(
        lambda x: pd.Series(parse_sheet_info(x))
    )
    
    # Add country flags
    df_processed['Market'] = df_processed['Location'].apply(get_country_flag)
    
    # Get latest data for each keyword (most recent timestamp)
    if 'Date/Time' in df_processed.columns:
        df_processed['DateTime'] = pd.to_datetime(df_processed['Date/Time'], errors='coerce')
        latest_data = df_processed.sort_values('DateTime').groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    else:
        latest_data = df_processed.groupby('Keyword_Clean').tail(1).reset_index(drop=True)
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Market filter
    markets = ['All Markets'] + sorted(latest_data['Market'].unique().tolist())
    selected_market = st.sidebar.selectbox("Select Market", markets)
    
    # Position filter
    position_options = ['All Positions', 'Top 3 (1-3)', 'Positions 4-10', 'Not Ranking']
    selected_position = st.sidebar.selectbox("Position Range", position_options)
    
    # AI Overview filter
    ai_options = ['All', 'With AI Overview', 'Without AI Overview']
    selected_ai = st.sidebar.selectbox("AI Overview Status", ai_options)
    
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
    
    # Key Metrics
    st.markdown("## 📊 Key Metrics")
    
    if 'Recharge Position' in latest_data.columns:
        # Calculate metrics
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
        
        # Display metrics in columns
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
    st.markdown("## 🔍 Keywords Overview")
    
    if not filtered_data.empty:
        # Prepare display data
        display_data = filtered_data.copy()
        
        # Format the data for display
        if 'Recharge Position' in display_data.columns:
            display_data['Position_Display'] = display_data['Recharge Position'].apply(
                lambda x: get_position_status(x)[0]
            )
        
        if 'Position Change' in display_data.columns:
            display_data['Trend'] = display_data['Position Change'].apply(get_trend_emoji)
        
        # Select columns for display
        display_columns = []
        column_mapping = {}
        
        if 'Keyword_Clean' in display_data.columns:
            display_columns.append('Keyword_Clean')
            column_mapping['Keyword_Clean'] = 'Keyword'
        
        if 'Market' in display_data.columns:
            display_columns.append('Market')
        
        if 'Position_Display' in display_data.columns:
            display_columns.append('Position_Display')
            column_mapping['Position_Display'] = 'Position'
        
        if 'Trend' in display_data.columns and 'Position Change' in display_data.columns:
            display_data['Change_Display'] = display_data['Trend'] + ' ' + display_data['Position Change'].fillna('')
            display_columns.append('Change_Display')
            column_mapping['Change_Display'] = 'Change'
        
        if 'AI Overview' in display_data.columns:
            display_data['AI_Display'] = display_data['AI Overview'].apply(
                lambda x: '🤖 Yes' if str(x).lower() in ['yes', 'y', 'true'] else '❌ No'
            )
            display_columns.append('AI_Display')
            column_mapping['AI_Display'] = 'AI Overview'
        
        if 'Date/Time' in display_data.columns:
            display_data['Last_Check'] = pd.to_datetime(display_data['Date/Time'], errors='coerce')
            display_data['Time_Ago'] = display_data['Last_Check'].apply(
                lambda x: f"{(datetime.datetime.now() - x).total_seconds() / 3600:.1f}h ago" 
                if pd.notna(x) else 'Unknown'
            )
            display_columns.append('Time_Ago')
            column_mapping['Time_Ago'] = 'Last Check'
        
        # Show the table
        if display_columns:
            table_data = display_data[display_columns].rename(columns=column_mapping)
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No data matches the selected filters.")
    
    # Charts Section
    st.markdown("## 📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Position Distribution Chart
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
                    'Top 3 (1-3)': '#28a745',
                    'Positions 4-10': '#ffc107',
                    'Not Ranking': '#dc3545'
                }
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Market Performance Chart
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
                    color_continuous_scale=['#28a745', '#ffc107', '#dc3545']
                )
                fig_bar.update_layout(height=400, yaxis_title="Average Position")
                st.plotly_chart(fig_bar, use_container_width=True)
    
    # Market Performance Cards
    st.markdown("## 🌍 Market Performance")
    
    if 'Market' in latest_data.columns:
        markets_stats = []
        for market in latest_data['Market'].unique():
            market_data = latest_data[latest_data['Market'] == market]
            
            keyword_count = len(market_data)
            
            # Average position (only numeric positions)
            numeric_positions = market_data['Recharge Position'].apply(
                lambda x: x if isinstance(x, (int, float)) else None
            ).dropna()
            avg_position = numeric_positions.mean() if len(numeric_positions) > 0 else None
            
            # AI coverage
            ai_coverage = len(market_data[
                market_data['AI Overview'].str.lower().isin(['yes', 'y', 'true'])
            ]) / len(market_data) * 100 if len(market_data) > 0 else 0
            
            markets_stats.append({
                'Market': market,
                'Keywords': keyword_count,
                'Avg Position': f"{avg_position:.1f}" if avg_position else "N/A",
                'AI Coverage': f"{ai_coverage:.0f}%"
            })
        
        # Display market cards
        market_cols = st.columns(min(len(markets_stats), 4))
        for i, stats in enumerate(markets_stats):
            with market_cols[i % 4]:
                st.markdown(f"""
                <div style='padding: 1rem; background: white; border-radius: 10px; 
                           border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h4 style='margin: 0; color: #333;'>{stats['Market']}</h4>
                    <p style='margin: 5px 0;'><strong>Keywords:</strong> {stats['Keywords']}</p>
                    <p style='margin: 5px 0;'><strong>Avg Position:</strong> {stats['Avg Position']}</p>
                    <p style='margin: 5px 0;'><strong>AI Coverage:</strong> {stats['AI Coverage']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666; padding: 1rem;'>"
        f"Last updated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')} | "
        f"Total Keywords: {len(latest_data)} | "
        f"Data refresh: Every 5 minutes"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
