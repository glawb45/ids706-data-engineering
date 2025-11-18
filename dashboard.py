import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text

# Page configuration
st.set_page_config(page_title="Real-Time Ride-Sharing Dashboard", layout="wide")
st.title("🚗 Real-Time Ride-Sharing Dashboard")

# Database connection
DATABASE_URL = "postgresql://kafka_user:kafka_password@localhost:5432/kafka_db"

@st.cache_resource
def get_engine(url: str):
    return create_engine(url, pool_pre_ping=True)

engine = get_engine(DATABASE_URL)

def load_data(status_filter: str | None = None, city_filter: str | None = None, limit: int = 200) -> pd.DataFrame:
    """Load trip data from PostgreSQL with optional filters."""
    base_query = "SELECT * FROM trips"
    conditions = []
    params = {}
    
    if status_filter and status_filter != "All":
        conditions.append("status = :status")
        params["status"] = status_filter
    
    if city_filter and city_filter != "All":
        conditions.append("city = :city")
        params["city"] = city_filter
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY timestamp DESC LIMIT :limit"
    params["limit"] = limit
    
    try:
        df = pd.read_sql_query(text(base_query), con=engine.connect(), params=params)
        return df
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

# Sidebar controls
st.sidebar.header("🎛️ Controls")

status_options = ["All", "requested", "accepted", "in_progress", "completed", "cancelled"]
selected_status = st.sidebar.selectbox("Filter by Status", status_options)

city_options = ["All", "New York", "Los Angeles", "Chicago", "San Francisco", "Miami"]
selected_city = st.sidebar.selectbox("Filter by City", city_options)

update_interval = st.sidebar.slider("Update Interval (seconds)", min_value=2, max_value=20, value=5)
limit_records = st.sidebar.number_input("Number of records to load", min_value=50, max_value=2000, value=200, step=50)

if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

# Main dashboard loop
placeholder = st.empty()

while True:
    df_trips = load_data(selected_status, selected_city, limit=int(limit_records))
    
    with placeholder.container():
        if df_trips.empty:
            st.warning("⚠️ No records found. Waiting for data...")
            time.sleep(update_interval)
            continue
        
        # Convert timestamp column
        if "timestamp" in df_trips.columns:
            df_trips["timestamp"] = pd.to_datetime(df_trips["timestamp"])
        
        # Calculate KPIs
        total_trips = len(df_trips)
        total_revenue = df_trips["fare"].sum()
        avg_fare = total_revenue / total_trips if total_trips > 0 else 0.0
        avg_distance = df_trips["distance_km"].mean()
        avg_rating = df_trips["rating"].mean()
        completed_trips = len(df_trips[df_trips["status"] == "completed"])
        completion_rate = (completed_trips / total_trips * 100) if total_trips > 0 else 0.0
        
        # Display filters
        st.subheader(f"📊 Displaying {total_trips} trips (Status: {selected_status} | City: {selected_city})")
        
        # KPI Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🚕 Total Trips", f"{total_trips:,}")
        col2.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
        col3.metric("🎫 Avg Fare", f"${avg_fare:.2f}")
        col4.metric("📏 Avg Distance", f"{avg_distance:.1f} km")
        col5.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
        
        col6, col7, col8 = st.columns(3)
        col6.metric("✅ Completed", f"{completed_trips:,}")
        col7.metric("📈 Completion Rate", f"{completion_rate:.1f}%")
        col8.metric("🚗 Active Drivers", df_trips["driver_id"].nunique())
        
        st.markdown("---")
        
        # Charts Row 1
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Revenue by city
            city_revenue = df_trips.groupby("city")["fare"].sum().reset_index().sort_values("fare", ascending=False)
            fig_city = px.bar(
                city_revenue,
                x="city",
                y="fare",
                title="💰 Revenue by City",
                labels={"fare": "Total Revenue ($)", "city": "City"},
                color="fare",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_city, use_container_width=True)
        
        with chart_col2:
            # Trips by vehicle type
            vehicle_counts = df_trips.groupby("vehicle_type").size().reset_index(name="count")
            fig_vehicle = px.pie(
                vehicle_counts,
                values="count",
                names="vehicle_type",
                title="🚙 Trips by Vehicle Type",
                hole=0.4
            )
            st.plotly_chart(fig_vehicle, use_container_width=True)
        
        # Charts Row 2
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            # Trip status distribution
            status_counts = df_trips.groupby("status").size().reset_index(name="count")
            fig_status = px.bar(
                status_counts,
                x="status",
                y="count",
                title="📊 Trip Status Distribution",
                labels={"count": "Number of Trips", "status": "Status"},
                color="status"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with chart_col4:
            # Average fare by city
            city_avg_fare = df_trips.groupby("city")["fare"].mean().reset_index().sort_values("fare", ascending=False)
            fig_avg_fare = px.bar(
                city_avg_fare,
                x="city",
                y="fare",
                title="🎫 Average Fare by City",
                labels={"fare": "Average Fare ($)", "city": "City"},
                color="fare",
                color_continuous_scale="Greens"
            )
            st.plotly_chart(fig_avg_fare, use_container_width=True)
        
        # Distance distribution
        st.subheader("📏 Distance Distribution")
        fig_distance = px.histogram(
            df_trips,
            x="distance_km",
            nbins=30,
            title="Trip Distance Distribution",
            labels={"distance_km": "Distance (km)", "count": "Number of Trips"}
        )
        st.plotly_chart(fig_distance, use_container_width=True)
        
        # Raw data table
        st.markdown("### 📋 Recent Trips (Top 10)")
        display_columns = ["trip_id", "city", "distance_km", "duration_minutes", "fare", "vehicle_type", "rating", "status", "timestamp"]
        st.dataframe(df_trips[display_columns].head(10), use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.caption(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Auto-refresh: {update_interval}s")
    
    time.sleep(update_interval)