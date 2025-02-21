import pandas as pd
from datetime import datetime
import streamlit as st
import requests
from io import BytesIO

class DataHandler:
    def __init__(self):
        self.excel_url = None

    def set_excel_url(self, url):
        """Set the Excel URL and validate it"""
        if "sharepoint" in url.lower():
            # Convert sharepoint view URL to direct download URL
            if "?" in url:
                base_url = url.split("?")[0]
                self.excel_url = base_url + "?download=1"
            else:
                self.excel_url = url + "?download=1"
        else:
            self.excel_url = url

    def fetch_data(self):
        """Fetch data from Excel file"""
        try:
            if not self.excel_url:
                return None

            # For SharePoint URLs, use requests to get the content
            response = requests.get(self.excel_url)
            if response.status_code != 200:
                st.error(f"Failed to fetch Excel file. Status code: {response.status_code}")
                return None

            # Read Excel content from memory
            excel_content = BytesIO(response.content)
            df = pd.read_excel(excel_content)

            # Validate required columns
            required_columns = [
                'Dye out date and time',
                'Customer name',
                'Batch No',
                'Style',
                'Submission type',
                'Required members',
                'Inspection start time',
                'Inspection End time',
                'Inspection Exceed time'
            ]

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"Missing columns in Excel file: {', '.join(missing_columns)}")
                return None

            # Convert datetime columns
            datetime_columns = ['Dye out date and time', 'Inspection start time', 'Inspection End time', 'Inspection Exceed time']
            for col in datetime_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

            return df

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return None

    def process_data_for_gantt(self, df):
        """Transform data for Gantt chart"""
        if df is None:
            return None

        try:
            gantt_df = df.copy()

            # Create task IDs
            gantt_df['Task ID'] = gantt_df['Batch No'].astype(str) + '_' + gantt_df['Style'].astype(str)

            # Calculate duration
            gantt_df['Duration'] = (gantt_df['Inspection End time'] - gantt_df['Inspection start time']).dt.total_seconds() / 3600

            # Format members list
            gantt_df['Required members'] = gantt_df['Required members'].fillna('').astype(str)
            gantt_df['Required members'] = gantt_df['Required members'].apply(lambda x: [m.strip() for m in x.split(',') if m.strip()])

            return gantt_df

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            return None