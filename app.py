import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go


CSS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=CSS)
server = app.server

# Load data.
df = pd.read_csv('data/final.csv', parse_dates=['dob'])

# Create components and set app layout.
row1 = html.Div(id='row1')
row2 = html.Div(id='row2')

app.layout = html.Div([row1, row2])


if __name__ == '__main__':
    app.run_server()
