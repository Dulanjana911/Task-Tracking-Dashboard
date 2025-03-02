import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

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
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True  # Default: Auto-refresh enabled

# App title and description
st.set_page_config(layout="wide")  # Set full-screen mode
st.title("Task Tracking Dashboard")
st.markdown("""
    This dashboard provides real-time visualization of task tracking data from Excel.
    Updates automatically every 10 seconds (unless disabled).
""")

# Excel URL input and refresh controls
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    excel_url = st.text_input(
        "Enter Excel File URL",
        "https://nsbm365-my.sharepoint.com/:x:/g/personal/dkavishan_students_nsbm_ac_lk/EQJX1bcJDaRJvVDdq57n3JYBVb2scE40HPjZVYrJBDaIEA?e=s5KYVq",
        help="Provide a direct URL to the Excel file."
    )
with col2:
    if st.button("🔄 Refresh Now"):
        st.session_state.last_refresh = time.time()
        st.rerun()
with col3:
    st.session_state.auto_refresh = st.toggle("Auto Refresh", value=st.session_state.auto_refresh)

if excel_url:
    st.session_state.data_handler.set_excel_url(excel_url)

    # Auto-refresh every 10 seconds if enabled
    if st.session_state.auto_refresh:
        st_autorefresh(interval=10 * 1000, key="data_refresh")

    placeholder = st.empty()  # Placeholder for partial refresh

    with placeholder.container():  # Refresh only this section
        with st.spinner("Loading data..."):
            df = st.session_state.data_handler.fetch_data()

            if df is not None and not df.empty:
                gantt_df = st.session_state.data_handler.process_data_for_gantt(df)

                # Always show Gantt chart in full-screen mode
                st.subheader("Gantt Chart")
                fig = st.session_state.gantt_chart.create_gantt(gantt_df)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)

                # Extract member columns (assuming columns contain 'Member' in their name)
                member_columns = [col for col in df.columns if "Member" in col]

                # Collect all members from the columns
                all_members = set()
                for col in member_columns:
                    all_members.update(df[col].dropna().unique())  # Drop NA values and get unique member names

                # Convert member names to comma-separated strings
                all_members_str = ', '.join(sorted(all_members)) if all_members else "No members found"

                # Extract current working members (based on 'Required members' in gantt_df)
                current_working_members = set(
                    member for members in gantt_df['Required members'] for member in members if isinstance(members, list)
                )

                # Convert current working members to a comma-separated string
                current_working_members_str = ', '.join(sorted(current_working_members)) if current_working_members else "No active members"

                # Calculate absent members
                absent_members = all_members - current_working_members

                # Convert absent members to a comma-separated string
                absent_members_str = ', '.join(sorted(absent_members)) if absent_members else "No absent members"

                # Display member lists in columns for a structured layout
                st.markdown("### Member Status")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("#### 👥 All Members")
                    st.info(all_members_str)

                with col2:
                    st.markdown("#### ✅ Current Working Members")
                    st.success(current_working_members_str)

                with col3:
                    st.markdown("#### 🚫 Absent Members")
                    st.warning(absent_members_str)

                # Create tabs for additional views
                tab1, tab2 = st.tabs(["Task Details", "Data Table"])

                with tab1:
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
                            gantt_df['Customer name'].str.contains(search, case=False, na=False) |
                            gantt_df['Batch No'].astype(str).str.contains(search, case=False, na=False) |
                            gantt_df['Style'].str.contains(search, case=False, na=False)
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
                        filtered_df['Required members'] = filtered_df['Required members'].apply(
                            lambda x: ', '.join(x) if isinstance(x, list) else str(x))
                        st.dataframe(
                            filtered_df[display_cols],
                            use_container_width=True
                        )
                    else:
                        st.info("No matching tasks found")

        # Display last refresh time and statistics in the sidebar
        st.sidebar.info(f"Last refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.sidebar.subheader("Dashboard Statistics")
        st.sidebar.metric("Total Tasks", len(df))
        st.sidebar.metric("All Members", len(all_members))
        st.sidebar.metric("Active Members", len(current_working_members))
        st.sidebar.metric("Absent Members", len(absent_members))
else:
    st.info("Please enter the Excel URL to begin")

# Footer
st.markdown("---")
st.markdown("Dashboard updates automatically every 10 seconds (if enabled).")
