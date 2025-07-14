import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import altair as alt

load_dotenv()

# --- Configuration ---
POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL", "postgresql://user:password@localhost:5432/calif")

# --- Page Config ---
st.set_page_config(
    page_title="CALIF Deal Dashboard",
    page_icon="💎",
    layout="wide",
)

# --- Database Connection ---
@st.cache_resource
def get_db_engine():
    """Initializes and returns a SQLAlchemy engine, cached for performance."""
    if not POSTGRES_DB_URL:
        st.error("POSTGRES_DB_URL must be set in the environment.")
        return None
    try:
        engine = create_engine(POSTGRES_DB_URL)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to the database: {e}")
        return None

# --- Data Loading ---
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_signals_data(_engine) -> pd.DataFrame:
    """Loads deal signals from the Postgres database."""
    if _engine is None:
        return pd.DataFrame()
    try:
        query = "SELECT * FROM signals WHERE is_deal = TRUE ORDER BY updated_at DESC"
        df = pd.read_sql(query, _engine)
        return df
    except Exception as e:
        st.warning(f"Could not load signals data. The 'signals' table may not exist yet. Error: {e}")
        return pd.DataFrame()


# --- Main Dashboard UI ---
def main():
    st.title("💎 Cross-Asset Luxury Investment Feed (CALIF)")
    st.subheader("Live Deal Signals")

    engine = get_db_engine()
    signals_df = load_signals_data(engine)

    if not signals_df.empty:
        # --- Display Metrics ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Deals", len(signals_df))
        if 'asset_type' in signals_df.columns:
            col2.metric("Asset Classes with Deals", signals_df['asset_type'].nunique())
        if 'updated_at' in signals_df.columns:
            latest_update = pd.to_datetime(signals_df['updated_at']).max()
            col3.metric("Last Updated", latest_update.strftime("%Y-%m-%d %H:%M:%S UTC"))

        st.markdown("---")

        # --- Display Table ---
        st.dataframe(signals_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Deal Analysis")

        # --- Charts ---
        if 'asset_type' in signals_df.columns and 'z_score' in signals_df.columns:
            # Bar chart of deals by asset type
            deal_counts = signals_df['asset_type'].value_counts().reset_index()
            deal_counts.columns = ['asset_type', 'count']
            
            bar_chart = alt.Chart(deal_counts).mark_bar().encode(
                x=alt.X('asset_type:N', title='Asset Type'),
                y=alt.Y('count:Q', title='Number of Deals'),
                tooltip=['asset_type', 'count']
            ).properties(
                title='Deals by Asset Type'
            )
            
            # Scatter plot of Z-score vs. price
            scatter_plot = alt.Chart(signals_df).mark_circle(size=60).encode(
                x=alt.X('last_price:Q', title='Last Price', scale=alt.Scale(zero=False)),
                y=alt.Y('z_score:Q', title='Z-Score'),
                color='asset_type',
                tooltip=['asset_type', 'last_price', 'z_score']
            ).properties(
                title='Z-Score vs. Price for Active Deals'
            )
            
            st.altair_chart(bar_chart, use_container_width=True)
            st.altair_chart(scatter_plot, use_container_width=True)
        
    else:
        st.info("No active deal signals found. Check back later!")

if __name__ == "__main__":
    main() 