import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------------------------------
# Page Configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Anomaly Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------------------------
# Custom CSS for styling (Evreka Brand Colors)
# --------------------------------------------------------------------------
def local_css():
    st.markdown("""
        <style>
            /* General Body and Font */
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f8fafb;
            }

            /* Evreka Brand Colors */
            :root {
                --evreka-navy: #0b2b51;
                --evreka-dark-blue: #1a3d6b;
                --evreka-green: #5cb85c;
                --evreka-light-green: #d4edda;
                --evreka-bg-light: #f8fafb;
                --evreka-border: #e3e6ea;
                --evreka-text-primary: #0b2b51;
                --evreka-text-secondary: #6c757d;
                --evreka-accent: #27ae60;
                --evreka-gradient-1: linear-gradient(135deg, #0b2b51 0%, #1a3d6b 50%, #5cb85c 100%);
                --evreka-gradient-2: linear-gradient(45deg, #5cb85c 0%, #27ae60 100%);
            }

            /* Remove Streamlit Header/Footer and padding */
            .st-emotion-cache-18ni7ap, .st-emotion-cache-h4xjwg {
                padding-top: 2rem;
            }
            header, footer {
                visibility: hidden;
            }

            /* Main container background */
            .main .block-container {
                background-color: var(--evreka-bg-light);
                padding-top: 1rem;
            }

            /* KPI Card Styling - Enhanced Evreka Style */
            .kpi-card {
                background: linear-gradient(145deg, #ffffff 0%, #f8fafb 100%);
                border: 2px solid transparent;
                background-clip: padding-box;
                border-radius: 16px;
                padding: 2rem;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 8px 30px rgba(11, 43, 81, 0.08);
                position: relative;
                overflow: hidden;
            }
            .kpi-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 6px;
                background: var(--evreka-gradient-1);
                border-radius: 16px 16px 0 0;
            }
            .kpi-card::after {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle, rgba(92, 184, 92, 0.05) 0%, transparent 70%);
                transform: rotate(25deg);
                transition: all 0.4s ease;
                opacity: 0;
            }
            .kpi-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 40px rgba(11, 43, 81, 0.15);
                border-color: var(--evreka-green);
            }
            .kpi-card:hover::after {
                opacity: 1;
                top: -25%;
                right: -25%;
            }
            .kpi-title {
                font-size: 0.9rem;
                font-weight: 700;
                color: var(--evreka-text-secondary);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 0.5rem;
            }
            .kpi-value {
                font-size: 3rem;
                font-weight: 800;
                margin-top: 0.5rem;
                color: var(--evreka-navy);
                text-shadow: 0 2px 4px rgba(11, 43, 81, 0.1);
                position: relative;
                z-index: 2;
            }
            
            /* AI Suggestion Card Styling - Enhanced Evreka Style */
            .ai-card {
                background: linear-gradient(145deg, #ffffff 0%, #f8fafb 100%);
                border: 2px solid transparent;
                border-left: 6px solid var(--evreka-green);
                border-radius: 16px;
                padding: 2rem;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 8px 30px rgba(11, 43, 81, 0.08);
                position: relative;
                overflow: hidden;
            }
            .ai-card::before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 60px;
                height: 60px;
                background: radial-gradient(circle, rgba(92, 184, 92, 0.1) 0%, transparent 70%);
                border-radius: 50%;
                transform: translate(50%, -50%);
                transition: all 0.4s ease;
            }
            .ai-card:hover {
                border-left: 6px solid var(--evreka-navy);
                box-shadow: 0 20px 40px rgba(11, 43, 81, 0.15);
                transform: translateY(-8px) scale(1.02);
                background: linear-gradient(145deg, #ffffff 0%, #f0f9ff 100%);
            }
            .ai-card:hover::before {
                width: 120px;
                height: 120px;
                background: radial-gradient(circle, rgba(11, 43, 81, 0.05) 0%, transparent 70%);
            }
            .ai-card-title {
                font-weight: 800;
                font-size: 1.3rem;
                color: var(--evreka-navy);
                margin-bottom: 0.5rem;
                text-shadow: 0 1px 2px rgba(11, 43, 81, 0.1);
            }
            .ai-card-metrics {
                font-size: 0.9rem;
                color: var(--evreka-text-secondary);
                margin-bottom: 1.5rem;
                padding: 1rem;
                background: linear-gradient(135deg, var(--evreka-light-green) 0%, rgba(92, 184, 92, 0.1) 100%);
                border-radius: 12px;
                border-left: 4px solid var(--evreka-green);
                font-weight: 600;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }
            .ai-card-suggestion {
                color: var(--evreka-text-primary);
                line-height: 1.7;
                font-size: 1rem;
                font-weight: 500;
                position: relative;
                z-index: 2;
            }

            /* Badge Styling - Enhanced Evreka Colors */
            .suggestion-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.6rem 1.2rem;
                border-radius: 25px;
                font-weight: 700;
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
            }
            .suggestion-badge::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                transition: left 0.6s;
            }
            .suggestion-badge:hover::before {
                left: 100%;
            }
            .badge-green { 
                background: var(--evreka-gradient-2);
                color: white;
                box-shadow: 0 4px 15px rgba(92, 184, 92, 0.4);
                border: 2px solid rgba(255,255,255,0.3);
            }
            .badge-blue { 
                background: var(--evreka-gradient-1);
                color: white;
                box-shadow: 0 4px 15px rgba(11, 43, 81, 0.4);
                border: 2px solid rgba(255,255,255,0.3);
            }
            .badge-orange { 
                background: linear-gradient(135deg, #f39c12, #e67e22);
                color: white;
                box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4);
                border: 2px solid rgba(255,255,255,0.3);
            }
            
            /* Header Styling - Enhanced */
            .dashboard-header {
                background: var(--evreka-gradient-1);
                padding: 2.5rem;
                border-radius: 20px;
                margin-bottom: 2rem;
                box-shadow: 0 10px 40px rgba(11, 43, 81, 0.25);
                position: relative;
                overflow: hidden;
            }
            .dashboard-header::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -20%;
                width: 100%;
                height: 200%;
                background: radial-gradient(ellipse, rgba(255,255,255,0.1) 0%, transparent 70%);
                transform: rotate(25deg);
                animation: headerGlow 6s ease-in-out infinite alternate;
            }
            @keyframes headerGlow {
                0% { transform: rotate(25deg) scale(1); }
                100% { transform: rotate(25deg) scale(1.1); }
            }
            .dashboard-header h1 {
                color: white;
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 10px rgba(0,0,0,0.3);
                position: relative;
                z-index: 2;
            }
            .dashboard-header p {
                color: rgba(255, 255, 255, 0.9);
                font-size: 1.2rem;
                margin: 0;
                font-weight: 500;
                position: relative;
                z-index: 2;
            }
            .header-icon {
                background: linear-gradient(135deg, var(--evreka-green), var(--evreka-accent));
                padding: 1.2rem;
                border-radius: 20px;
                box-shadow: 0 8px 25px rgba(92, 184, 92, 0.4);
                position: relative;
                z-index: 2;
                transition: all 0.3s ease;
            }
            .header-icon:hover {
                transform: scale(1.1) rotate(5deg);
                box-shadow: 0 12px 35px rgba(92, 184, 92, 0.6);
            }
            
            /* Button Styling - Enhanced */
            .stButton > button {
                background: var(--evreka-gradient-2);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.7rem 2rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 15px rgba(92, 184, 92, 0.4);
                position: relative;
                overflow: hidden;
                font-size: 0.85rem;
            }
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            .stButton > button:hover::before {
                left: 100%;
            }
            .stButton > button:hover {
                background: var(--evreka-gradient-1);
                color: white;
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(11, 43, 81, 0.4);
                border-radius: 25px;
            }
            .stButton > button:active {
                transform: translateY(-1px);
            }
            
            /* Table Styling */
            .stDataFrame {
                border: 1px solid var(--evreka-border);
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
            }
            
            /* Section Title Styling */
            .section-title {
                color: var(--evreka-navy);
                font-weight: 700;
                font-size: 1.8rem;
                margin-bottom: 1rem;
                position: relative;
                padding-bottom: 0.5rem;
            }
            .section-title::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 60px;
                height: 3px;
                background: linear-gradient(90deg, var(--evreka-green), var(--evreka-navy));
                border-radius: 2px;
            }
            
            /* Checkbox styling */
            .stCheckbox > label {
                color: var(--evreka-navy);
                font-weight: 600;
            }
            
            /* Divider styling */
            hr {
                border: none;
                height: 2px;
                background: linear-gradient(90deg, var(--evreka-green), transparent);
                margin: 2rem 0;
            }
        </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Data Loading and Caching
# --------------------------------------------------------------------------
@st.cache_data
def load_data(relative_path):
    """
    Loads the service point metrics from a CSV file using a path relative 
    to the script's location.
    """
    # Get the absolute path of the directory where the script is located
    script_dir = Path(__file__).resolve().parent
    # Combine it with the relative path to the data file
    data_file = script_dir / relative_path
    
    if not data_file.exists():
        st.error(f"Data file not found. Attempted to load from: {data_file}")
        return pd.DataFrame()
    return pd.read_csv(data_file)

# --------------------------------------------------------------------------
# AI Suggestion Logic
# --------------------------------------------------------------------------
def get_ai_suggestions(anomalous_df, all_df):
    """Generates AI-powered suggestions for anomalous service points."""
    suggestions = {}
    other_sp_names = all_df[all_df['Anomaly State'] == 'No']['Service Point'].tolist()

    # Separate candidates for rebalancing to apply special rules
    rebalance_candidates = []

    for _, row in anomalous_df.iterrows():
        sp_name = row['Service Point']
        caiv = row['CAIv Ratio']
        
        if caiv > 1.2:
            suggestions[sp_name] = {"text": "High overflow risk. Recommend **adding 2 new containers** to increase capacity.", "icon": "M12 6V18M6 12H18", "color": "green"}
        elif caiv > 0.9:
            suggestions[sp_name] = {"text": "High utilization. Recommend **adding 1 new container** to prevent overflows.", "icon": "M12 6V18M6 12H18", "color": "green"}
        elif caiv < 0.3:
            suggestions[sp_name] = {"text": "Low utilization. Recommend **removing 1 container** to optimize costs.", "icon": "M18 12H6", "color": "blue"}
        else:
            rebalance_candidates.append(row)

    # Sort rebalance candidates by CAIv Ratio descending
    rebalance_candidates.sort(key=lambda x: x['CAIv Ratio'], reverse=True)

    # Assign suggestions to the sorted rebalance candidates
    for i, row in enumerate(rebalance_candidates):
        sp_name = row['Service Point']
        # The top 2 get the "add 1 container" suggestion
        if i < 2:
            suggestions[sp_name] = {"text": "High utilization. Recommend **adding 1 new container** to prevent overflows.", "icon": "M12 6V18M6 12H18", "color": "green"}
        else:
            # The rest get the rebalance suggestion
            if other_sp_names:
                random_neighbor = pd.Series(other_sp_names).sample(1).iloc[0]
                suggestions[sp_name] = {"text": f"Unbalanced fill rate. Suggest **rebalancing load** with nearby point: **{random_neighbor}**.", "icon": "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4", "color": "orange"}
            else:
                suggestions[sp_name] = {"text": "Unbalanced fill rate. Consider adjusting service frequency.", "icon": "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4", "color": "orange"}
            
    return suggestions

# --------------------------------------------------------------------------
# Main Application
# --------------------------------------------------------------------------
def main():
    local_css()

    # --- Load Data ---
    # The path is now relative to this script's location (ui/)
    df = load_data("../output/sp_metrics.csv")
    if df.empty:
        st.stop()

    # --- State Management ---
    if 'view' not in st.session_state:
        st.session_state.view = 'ai_suggestions'

    # --- Header - Evreka Style ---
    st.markdown("""
        <div class="dashboard-header">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div class="header-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                </div>
                <div>
                    <h1>Service Point Analytics Dashboard</h1>
                    <p>AI-Powered Anomaly Detection & Optimization</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- KPI Cards ---
    total_sp = len(df)
    anomalous_sp_count = len(df[df['Anomaly State'] == 'Yes'])
    
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Service Points</div>
                <div class="kpi-value">{total_sp}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Anomalous Service Points</div>
                <div class="kpi-value" style="color: #e74c3c;">{anomalous_sp_count}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Main Content Area ---
    with st.container():
        # --- View Toggle Controls ---
        title_col, controls_col = st.columns([2, 1])
        
        with title_col:
            view_title = "AI Optimization Suggestions" if st.session_state.view == 'ai_suggestions' else "Service Points Data"
            st.markdown(f'<h2 class="section-title">{view_title}</h2>', unsafe_allow_html=True)

        with controls_col:
            # This container will hold the controls, aligned to the right
            st.markdown('<div style="display: flex; justify-content: flex-end; align-items: center; gap: 1rem;"></div>', unsafe_allow_html=True)
            
            button_text = "View Data Table" if st.session_state.view == 'ai_suggestions' else "View AI Suggestions"
            if st.button(button_text, key="toggle_button"):
                st.session_state.view = 'data_table' if st.session_state.view == 'ai_suggestions' else 'ai_suggestions'
                st.rerun()

        st.markdown("<hr/>", unsafe_allow_html=True)

        # --- Display Content Based on View ---
        if st.session_state.view == 'ai_suggestions':
            anomalous_df = df[df['Anomaly State'] == 'Yes'].copy()
            suggestions = get_ai_suggestions(anomalous_df, df)
            
            # Ensure there are suggestions to display
            if not suggestions:
                st.info("No anomalies found to generate suggestions.")
            else:
                # Dynamically create columns based on the number of suggestions
                num_suggestions = len(anomalous_df)
                cols = st.columns(min(num_suggestions, 3))
                
                for i, (_, row) in enumerate(anomalous_df.iterrows()):
                    sp_name = row['Service Point']
                    suggestion = suggestions.get(sp_name)
                    if not suggestion: continue

                    with cols[i % min(num_suggestions, 3)]:
                        st.markdown(f"""
                            <div class="ai-card">
                                <div>
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                                        <p class="ai-card-title">{sp_name}</p>
                                        <span class="suggestion-badge badge-{suggestion['color']}">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="{suggestion['icon']}"/></svg>
                                            SUGGESTION
                                        </span>
                                    </div>
                                    <div class="ai-card-metrics">
                                        <strong>CAIv Ratio:</strong> {row['CAIv Ratio']:.3f} | <strong>Anomaly Score:</strong> {row['Max Anomaly Score']:.3f}
                                    </div>
                                </div>
                                <p class="ai-card-suggestion">{suggestion['text'].replace('**', '<strong>').replace('**', '</strong>')}</p>
                            </div>
                            <br>
                        """, unsafe_allow_html=True)

        else: # Data Table View
            show_only_anomalies = st.checkbox("Show only anomalies", value=False)
            
            df_to_show = df[df['Anomaly State'] == 'Yes'].copy() if show_only_anomalies else df.copy()

            def highlight_anomalies(row):
                return ['background-color: #fff5f5']*len(row) if row['Anomaly State'] == "Yes" else ['background-color: white']*len(row)

            st.dataframe(
                df_to_show.style.apply(highlight_anomalies, axis=1).format({
                    'Max Anomaly Score': '{:.4f}',
                    'lat': '{:.6f}',
                    'lon': '{:.6f}',
                    'CAIv Ratio': '{:.4f}',
                    'VOF %': '{:.2f}',
                    'VUR %': '{:.2f}',
                    'CVv Ratio': '{:.4f}',
                    'PMRv Ratio': '{:.4f}',
                    'GR p90 (kg/day)': '{:.2f}',
                    'DtO (days)': '{:.2f}',
                    'CVgr Ratio': '{:.4f}',
                }),
                use_container_width=True
            )
            
            # --- Metric Explanations Section ---
            st.markdown("<br><hr/><br>", unsafe_allow_html=True)
            st.markdown('<h2 class="section-title">Metric Explanations</h2>', unsafe_allow_html=True)
            
            exp1, exp2, exp3 = st.columns(3)
            with exp1:
                st.markdown("""
                #### Capacity Alignment (CAIv)
                **Answers:** "Is the container capacity right for this location?"
                - **> 1.0:** Chronic under-capacity (high overflow risk).
                - **< 0.4:** Chronic over-capacity (wasted resources).
                """)
            with exp2:
                st.markdown("""
                #### Visit Overflow Frequency (VOF)
                **Answers:** "On what percentage of visits was the container already overflowing?"
                - **> 5%:** A significant problem requiring immediate action.
                - **< 2%:** Healthy service level.
                """)
            with exp3:
                st.markdown("""
                #### Visit Utilization Ratio (VUR)
                **Answers:** "On average, how full are the containers when we collect them?"
                - **< 40%:** Inefficient; containers are collected too empty, wasting fuel and time.
                - **> 80%:** Risky; containers are consistently near full capacity.
                """)


if __name__ == "__main__":
    main()
