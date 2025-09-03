import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, ctx
from django_plotly_dash import DjangoDash

# Sample Data
data = pd.DataFrame({
    'Client': ['C1', 'C1', 'C2', 'C2', 'C2'],
    'Project': ['P1', 'P2', 'P1', 'P2', 'P3'],
    'Total Seekers': [25, 35, 100, 28, 65],
    'Minimum': [18, 22, 75, 12, 64],
    'Optimum': [12, 20, 22, 2, 60]
})

# Initialize Dash app
app = DjangoDash('SpeedometerDashboard')  # Dash app name

# Layout for Dash app
app.layout = html.Div([
    html.H1("Speedometer Dashboard (Minimum and Optimum)"),
    dcc.Graph(id='minimum-speedometer', style={'display': 'inline-block', 'width': '48%'}),
    dcc.Graph(id='optimum-speedometer', style={'display': 'inline-block', 'width': '48%'})
])

@app.callback(
    Output('minimum-speedometer', 'figure'),
    Output('optimum-speedometer', 'figure'),
    [Input('url', 'search')]
)
def update_speedometers(query_string):
    # Extract query parameters from URL
    query_params = ctx.request.query
    client = query_params.get('client', 'C1')
    project = query_params.get('project', 'P1')

    # Filter data
    filtered_data = data[(data['Client'] == client) & (data['Project'] == project)]
    if not filtered_data.empty:
        total_seekers = filtered_data['Total Seekers'].values[0]
        minimum = filtered_data['Minimum'].values[0]
        optimum = filtered_data['Optimum'].values[0]

        # Thresholds
        first_threshold = total_seekers / 3
        second_threshold = 2 * total_seekers / 3

        # Minimum Speedometer
        minimum_fig = go.Figure()
        minimum_fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=minimum,
            title={'text': f"Minimum Speedometer"},
            gauge={
                'axis': {'range': [0, total_seekers], 'tickwidth': 2, 'tickcolor': "black"},
                'bar': {'color': "black", 'thickness': 0.05},
                'steps': [
                    {'range': [0, first_threshold], 'color': "red"},
                    {'range': [first_threshold, second_threshold], 'color': "yellow"},
                    {'range': [second_threshold, total_seekers], 'color': "green"}
                ],
                'threshold': {'line': {'color': "black", 'width': 2}, 'value': minimum}
            }
        ))

        # Optimum Speedometer
        optimum_fig = go.Figure()
        optimum_fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=optimum,
            title={'text': f"Optimum Speedometer"},
            gauge={
                'axis': {'range': [0, total_seekers], 'tickwidth': 2, 'tickcolor': "black"},
                'bar': {'color': "black", 'thickness': 0.05},
                'steps': [
                    {'range': [0, first_threshold], 'color': "red"},
                    {'range': [first_threshold, second_threshold], 'color': "yellow"},
                    {'range': [second_threshold, total_seekers], 'color': "green"}
                ],
                'threshold': {'line': {'color': "black", 'width': 2}, 'value': optimum}
            }
        ))

        return minimum_fig, optimum_fig

    return go.Figure(), go.Figure()
