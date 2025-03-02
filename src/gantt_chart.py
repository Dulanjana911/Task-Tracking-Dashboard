from datetime import datetime
import plotly.figure_factory as ff
import plotly.express as px
import streamlit as st

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

            for _, row in df.iterrows():
                members_display = ', '.join(row['Required members']) if isinstance(row['Required members'], list) else str(row['Required members'])
                gantt_data.append(dict(
                    Task=f"{row['Task ID']} - Members: {members_display}",
                    Start=row['Inspection start time'],
                    Finish=row['Inspection End time'],
                    Resource=row['Customer name'],
                    Description=f"Batch: {row['Batch No']}<br>"
                                f"Style: {row['Style']}<br>"
                                f"Members: {members_display}"
                ))

            # Create Gantt chart
            fig = ff.create_gantt(
                gantt_data,
                colors=self.colors,
                index_col='Resource',
                show_colorbar=True,
                group_tasks=True,
                showgrid_x=True,
                showgrid_y=True
            )

            # Add a vertical line for the current timeline
            current_time = datetime.now()
            fig.add_vline(
                x=current_time,
                line=dict(color='red', width=2, dash='dash'),
                name='Current Time'
            )

            # Add annotation showing current date and time
            fig.add_annotation(
                x=current_time,
                y=1.05,  # Position annotation above the chart
                text=f"Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                font=dict(size=12, color="black"),
                bgcolor="white",
                borderpad=4,
                bordercolor="black",
                borderwidth=1
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