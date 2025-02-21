import streamlit as st
import time
from src.data_handler import DataHandler
from src.gantt_chart import GanttChart
from src.utils import create_task_details

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()
if 'gantt_chart' not in st.session_state:
    st.session_state.gantt_chart = GanttChart()

# App title and description
st.title("Task Tracking Dashboard")
st.markdown("""
    This dashboard provides real-time visualization of task tracking data from Excel.
    Updates automatically every 30 seconds.
""")

# Excel URL input
excel_url = st.text_input(
    "Enter Excel URL",
    help="Paste the URL of your online Excel file here"
)

if excel_url:
    st.session_state.data_handler.set_excel_url(excel_url)
    
    # Auto-refresh mechanism
    current_time = time.time()
    if current_time - st.session_state.last_refresh >= 30:
        st.session_state.last_refresh = current_time
        st.experimental_rerun()
    
    # Data loading and processing
    with st.spinner("Loading data..."):
        df = st.session_state.data_handler.fetch_data()
        if df is not None:
            gantt_df = st.session_state.data_handler.process_data_for_gantt(df)
            
            # Create Gantt chart
            fig = st.session_state.gantt_chart.create_gantt(gantt_df)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
                
                # Display task details
                st.subheader("Task Details")
                for _, row in gantt_df.iterrows():
                    with st.expander(f"Task: {row['Task ID']}"):
                        st.markdown(create_task_details(row))
            
            # Display last refresh time
            st.sidebar.info(f"Last refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Display data statistics
            st.sidebar.subheader("Dashboard Statistics")
            st.sidebar.metric("Total Tasks", len(df))
            st.sidebar.metric("Active Members", 
                            len(set([member for members in df['Required members'] for member in members])))
else:
    st.info("Please enter the Excel URL to begin")

# Footer
st.markdown("---")
st.markdown("Dashboard updates automatically every 30 seconds")
