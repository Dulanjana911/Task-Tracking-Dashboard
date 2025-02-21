import pandas as pd
from datetime import datetime
import streamlit as st

def format_time(time):
    """Format datetime object to string"""
    if pd.isna(time):
        return "N/A"
    return time.strftime("%Y-%m-%d %H:%M")

def calculate_exceed_time(end_time, exceed_time):
    """Calculate if task exceeded allocated time"""
    if pd.isna(end_time) or pd.isna(exceed_time):
        return "N/A"

    exceed_duration = exceed_time - end_time
    if exceed_duration.total_seconds() > 0:
        return f"Exceeded by {exceed_duration}"
    return "Within time"

def create_task_details(row):
    """Create formatted task details for display"""
    return f"""
    **Customer:** {row['Customer name']}  
    **Batch No:** {row['Batch No']}  
    **Style:** {row['Style']}  
    **Submission Type:** {row['Submission type']}  
    **Members:** {', '.join(row['Required members'])}  
    **Timeline:**  
    - Start: {format_time(row['Inspection start time'])}  
    - End: {format_time(row['Inspection End time'])}  
    - Status: {calculate_exceed_time(row['Inspection End time'], row['Inspection Exceed time'])}
    """