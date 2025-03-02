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
    Updates automatically every 10 seconds.
""")

# Excel URL input and refresh controls
col1, col2 = st.columns([3, 1])
with col1:
    excel_url = st.text_input(
        "https://nsbm365-my.sharepoint.com/:x:/g/personal/dkavishan_students_nsbm_ac_lk/EQJX1bcJDaRJvVDdq57n3JYBVb2scE40HPjZVYrJBDaIEA?e=s5KYVq",
        help="Paste the URL of your online Excel file here"
    )
with col2:
    if st.button("🔄 Refresh Now"):
        st.session_state.last_refresh = 0
        st.rerun()

if excel_url:
    st.session_state.data_handler.set_excel_url(excel_url)

    # Auto-refresh mechanism
    current_time = time.time()
    if current_time - st.session_state.last_refresh >= 10:  # Changed from 30 to 10 seconds
        st.session_state.last_refresh = current_time
        st.rerun()

    # Data loading and processing
    with st.spinner("Loading data..."):
        df = st.session_state.data_handler.fetch_data()
        if df is not None:
            gantt_df = st.session_state.data_handler.process_data_for_gantt(df)

            # Create tabs for different views
            tab1, tab2 = st.tabs(["Gantt Chart", "Data Table"])

            with tab1:
                # Create Gantt chart
                fig = st.session_state.gantt_chart.create_gantt(gantt_df)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)

                    # Display task details
                    st.subheader("Task Details")
                    for _, row in gantt_df.iterrows():
                        with st.expander(f"Task: {row['Task ID']}"):
                            st.markdown(create_task_details(row))

            with tab2:
                st.subheader("Task Data Table")
                # Add search/filter box
                search = st.text_input("Search tasks", "")

                # Filter data based on search
                if search:
                    filtered_df = gantt_df[
                        gantt_df['Customer name'].str.contains(search, case=False) |
                        gantt_df['Batch No'].astype(str).str.contains(search, case=False) |
                        gantt_df['Style'].str.contains(search, case=False)
                    ]
                else:
                    filtered_df = gantt_df

                # Display filtered data
                if not filtered_df.empty:
                    # Select columns to display
                    display_cols = [
                        'Customer name', 'Batch No', 'Style', 
                        'Submission type', 'Required members',
                        'Inspection start time', 'Inspection End time',
                        'Inspection Exceed time'
                    ]
                    # Convert required members list to string for display
                    filtered_df['Required members'] = filtered_df['Required members'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
                    st.dataframe(
                        filtered_df[display_cols],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No matching tasks found")

            # Display last refresh time and statistics
            st.sidebar.info(f"Last refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.sidebar.subheader("Dashboard Statistics")
            st.sidebar.metric("Total Tasks", len(df))
            st.sidebar.metric("Active Members",
                            len(set([member for members in df['Required members'] for member in members])))
else:
    st.info("Please enter the Excel URL to begin")

# Footer
st.markdown("---")
st.markdown("Dashboard updates automatically every 10 seconds")