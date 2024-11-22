# Importación de las librerías necesarias
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

csv_file = r"csv_files/spacex_launch_dash.csv"
df = pd.read_csv(csv_file)

min_payload = df['Payload Mass (kg)'].min()
max_payload = df['Payload Mass (kg)'].max()

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1('Dashboard de Registros de Lanzamientos de SpaceX',
            style={'textAlign': 'center', 'color': '#343A40', 'font-size': 40}),
    dcc.Dropdown(
        id='launch-site-dropdown',
        options=[
            {'label': 'Todos los Sitios', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        ],
        value='ALL',
        placeholder='Seleccione un Sitio de Lanzamiento',
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Rango de carga útil (Kg):"),
    dcc.RangeSlider(
        id='payload-range-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('launch-site-dropdown', 'value')
)
def render_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            df[df['class'] == 1],
            names='Launch Site',
            title='Total de Lanzamientos Exitosos por Sitio'
        )
    else:
        filtered_df = df[df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['Outcome', 'Count']
        success_counts['Outcome'] = success_counts['Outcome'].map({1: 'Éxito', 0: 'Fracaso'})
        fig = px.pie(
            success_counts,
            names='Outcome',
            values='Count',
            title=f'Total de Lanzamientos en {selected_site}'
        )
    return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('launch-site-dropdown', 'value'),
        Input('payload-range-slider', 'value')
    ]
)
def render_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    mask = (df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)
    filtered_df = df[mask]
    
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlación entre Carga Útil y Éxito para Todos los Sitios',
            hover_data=['Launch Site']
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlación entre Carga Útil y Éxito en {selected_site}',
            hover_data=['Launch Site']
        )
    return fig

if __name__ == '__main__':
    app.run_server()