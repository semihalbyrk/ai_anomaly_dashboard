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
# Custom CSS for styling (adapted from the final HTML design)
# --------------------------------------------------------------------------
def local_css():
    st.markdown("""
        <style>
            /* General Body and Font */
            body {
                font-family: 'Inter', sans-serif;
            }

            /* Main Colors */
            :root {
                --brand-blue: #0b2b51;
                --brand-green: #07bc0c;
                --light-red-bg: #ffe6e6;
            }

            /* Remove Streamlit Header/Footer and padding */
            .st-emotion-cache-18ni7ap, .st-emotion-cache-h4xjwg {
                padding-top: 2rem;
            }
            header, footer {
                visibility: hidden;
            }

            /* KPI Card Styling */
            .kpi-card {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 0.5rem;
                padding: 1.5rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
            }
            .kpi-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            }
            .kpi-title {
                font-size: 0.875rem;
                font-weight: 500;
                color: #6c757d;
            }
            .kpi-value {
                font-size: 2.25rem;
                font-weight: 700;
                margin-top: 0.5rem;
            }
            
            /* AI Suggestion Card Styling */
            .ai-card {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-left: 4px solid #dee2e6;
                border-radius: 0.5rem;
                padding: 1.25rem;
                transition: all 0.3s ease;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .ai-card:hover {
                border-left: 4px solid var(--brand-blue);
                box-shadow: 0 8px 25px -5px rgba(0,0,0,0.08);
            }
            .ai-card-title {
                font-weight: 700;
                font-size: 1.125rem;
                color: var(--brand-blue);
            }
            .ai-card-metrics {
                font-size: 0.8rem;
                color: #6c757d;
                margin-top: 0.25rem;
            }
            .ai-card-suggestion {
                margin-top: 1rem;
                color: #495057;
                line-height: 1.6;
            }

            /* Badge Styling */
            .suggestion-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.375rem 0.875rem;
                border-radius: 9999px;
                font-weight: 600;
                font-size: 0.8rem;
            }
            .badge-green { background-color: rgba(7, 188, 12, 0.1); border: 1px solid rgba(7, 188, 12, 0.3); color: #068a09; }
            .badge-blue { background-color: rgba(11, 43, 81, 0.1); border: 1px solid rgba(11, 43, 81, 0.3); color: var(--brand-blue); }
            .badge-orange { background-color: rgba(249, 115, 22, 0.1); border: 1px solid rgba(249, 115, 22, 0.3); color: #f97316; }
            
            /* Table Styling */
            .stDataFrame {
                border: 1px solid #dee2e6;
                border-radius: 0.5rem;
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

    # --- Header ---
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
            <div style="padding: 0.5rem; background-color: #e7f0ff; border-radius: 0.5rem; border: 1px solid #d0e0ff;">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0b2b51" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            </div>
            <div>
                <h1 style="color: var(--brand-blue); font-size: 2rem; font-weight: 700; margin-bottom: 0;">Service Point Analytics Dashboard</h1>
                <p style="color: #495057; margin-top: 0;">AI-Powered Anomaly Detection & Suggestion</p>
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
                <div class="kpi-value" style="color: var(--brand-blue);">{total_sp}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Anomalous Service Points</div>
                <div class="kpi-value" style="color: #dc3545;">{anomalous_sp_count}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Main Content Area ---
    with st.container():
        # --- View Toggle Controls ---
        title_col, controls_col = st.columns([2, 1])
        
        with title_col:
            view_title = "AI Optimization Suggestions" if st.session_state.view == 'ai_suggestions' else "Service Points Data"
            st.markdown(f'<h2 style="color: var(--brand-blue); font-weight: 700;">{view_title}</h2>', unsafe_allow_html=True)

        with controls_col:
            # This container will hold the controls, aligned to the right
            st.markdown('<div style="display: flex; justify-content: flex-end; align-items: center; gap: 1rem;"></div>', unsafe_allow_html=True)
            
            button_text = "View Data Table" if st.session_state.view == 'ai_suggestions' else "View AI Suggestions"
            if st.button(button_text, key="toggle_button"):
                st.session_state.view = 'data_table' if st.session_state.view == 'ai_suggestions' else 'ai_suggestions'
                st.rerun()

        st.markdown("<hr style='margin-top: 0; margin-bottom: 1.5rem;'/>", unsafe_allow_html=True)

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
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                        <p class="ai-card-title">{sp_name}</p>
                                        <span class="suggestion-badge badge-{suggestion['color']}">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="{suggestion['icon']}"/></svg>
                                            SUGGESTION
                                        </span>
                                    </div>
                                    <p class="ai-card-metrics">CAIv Ratio: <b>{row['CAIv Ratio']:.3f}</b> | Anomaly Score: <b>{row['Max Anomaly Score']:.3f}</b></p>
                                </div>
                                <p class="ai-card-suggestion">{suggestion['text'].replace('**', '<b>')}</p>
                            </div>
                            <br>
                        """, unsafe_allow_html=True)

        else: # Data Table View
            show_only_anomalies = st.checkbox("Show only anomalies", value=False)
            
            df_to_show = df[df['Anomaly State'] == 'Yes'].copy() if show_only_anomalies else df.copy()

            def highlight_anomalies(row):
                return ['background-color: #fff0f1']*len(row) if row['Anomaly State'] == "Yes" else ['background-color: white']*len(row)

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

if __name__ == "__main__":
    main()
