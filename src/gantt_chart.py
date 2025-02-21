import plotly.figure_factory as ff
import plotly.express as px
from datetime import datetime, timedelta

class GanttChart:
    def __init__(self):
        self.colors = px.colors.qualitative.Set3
        
    def create_gantt(self, df):
        """Create Gantt chart from processed data"""
        if df is None or df.empty:
            return None
            
        try:
            # Prepare data for Gantt
            gantt_data = []
            
            for idx, row in df.iterrows():
                gantt_data.append(dict(
                    Task=row['Task ID'],
                    Start=row['Inspection start time'],
                    Finish=row['Inspection End time'],
                    Resource=row['Customer name'],
                    Description=f"Batch: {row['Batch No']}<br>"
                              f"Style: {row['Style']}<br>"
                              f"Members: {', '.join(row['Required members'])}"
                ))
                
            fig = ff.create_gantt(
                gantt_data,
                colors=self.colors,
                index_col='Resource',
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True
            )
            
            # Update layout
            fig.update_layout(
                title="Task Timeline",
                height=600,
                font=dict(size=10),
                showlegend=True,
                xaxis_title="Timeline",
                yaxis_title="Tasks",
                hovermode='x'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating Gantt chart: {str(e)}")
            return None
