import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go


CSS = ['https://codepen.io/Hmamin/pen/VOjQxN.css']
app = dash.Dash(__name__, external_stylesheets=CSS)
server = app.server

# Load and process data.
df = pd.read_csv('data/final.csv', parse_dates=['dob'])
stats = ['sapm', 'slpm', 'str_acc', 'str_def', 'td_acc', 'td_avg', 'td_def',
         'eff', 'active', 'grind', 'st_ratio', 'sub_avg']
attrs = ['height1', 'reach']
stat_names = ['Strikes Absorbed per Minute',
              'Strikes Landed per Minute',
              'Striking Accuracy (%)',
              'Striking Defense (%)',
              'Takedown Accuracy (%)',
              'Mean Takedowns per 15 Minutes',
              'Takedown Defense (%)',
              'Striking Efficiency (Ratio of Strikes Landed to Absorbed)',
              'Striking Activity (Strikes Landed + Strikes Absorbed per Minute)',
              'Takedowns to Submission Attempts Ratio',
              'Strike to Takedown Ratio',
              'Mean Submission Attempts per 15 Minutes'
              ]
wc_order = ['Strawweight', 'Flyweight', 'Bantamweight', 'Featherweight',
            'Lightweight', 'Welterweight', 'Middleweight',
            'Light Heavyweight', 'Heavyweight']
stat2name = dict([(stat, name) for stat, name in zip(stats, stat_names)])
gb = (df.groupby('weightclass')[stats+attrs].median().loc[wc_order])

# Create components and set app layout.
slider = dcc.Slider(id='slider', min=1, max=12, step=1, value=8,
                    marks=dict([(i, str(i)) for i in range(1, 13)]))
stat_dcc = dcc.Dropdown(id='stat_dcc',
                        options=[dict(label=name, value=stat)
                                 for stat, name in sorted(stat2name.items(),
                                                          key=lambda x: x[1])],
                        value='eff')
box_div = html.Div(id='box_div')
area_div = html.Div(id='area_div')
name_dcc = dcc.Dropdown(id='name_dcc',
                        options=[dict(label=name, value=name)
                                 for name in df.name1.unique()],
                        value=['Khabib Nurmagomedov', 'Tony Ferguson'],
                        multi=True)
polar_div = html.Div(id='polar_div', className='row')
notes_dcc = dcc.Markdown(children="""
### Reader Notes

* The "number of teams" slider will select the n teams with the largest number
of fighters who have appeared in the UFC. So for example, selecting a value of
1 will only display data for American Top Team, which has had the most UFC
fighters of any team.                 
* The weight class comparison plot uses the 
median value for each weight class.
* When viewing the team comparison
plot and the weight class comparison plot,
keep in mind that visual differences may seem 
magnified since the axes do not all start at 
zero. The goal here is to visualize small
differences between teams, weight classes,
and/or fighters, and I find the scale to
be more informative when zooming in on the
range of interest.
* Data was last updated April 13, 2019. I am still looking into ways to
continuously update the stats without scraping the entire dataset over again.
""",
                         className='notes')

app.layout = html.Div([html.H1('MMA Statistical Visualization Tool'),
                       html.Div(['Number of Teams', slider], className='row'),
                       box_div,
                       html.Div(stat_dcc, className='row'),
                       area_div,
                       polar_div,
                       html.Div(name_dcc, className='row'),
                       notes_dcc],
                      className='container')


@app.callback(Output('box_div', 'children'),
              [Input('slider', 'value'),
               Input('stat_dcc', 'value')])
def update_boxplot(n_teams, stat):
    """Filter df based on user-selected values and return a boxplot of the
    data.
    """
    common_teams = df.association.value_counts().head(n_teams)
    ordered_teams = (df[df.association.isin(common_teams.index)]
                     .groupby('association')[stat].median().sort_values())
    x_range = (df.loc[df.association.isin(common_teams.index), stat]
                 .quantile([.01, .99]))

    # Get list of graph traces.
    traces = []
    layout = go.Layout(title=f'Comparison of Top Fight Teams - '
                             f'{stat2name[stat].split("(")[0]}',
                       xaxis=dict(range=x_range,
                                  title=stat2name[stat],
                                  showline=True),
                       yaxis=dict(automargin=True,
                                  title='Team',
                                  showticklabels=False,
                                  showline=True),
                       showlegend=True,
                       legend=dict(traceorder='reversed'),
                       height=700,
                       # width=1100,
                       titlefont=dict(size=28))
    for team in ordered_teams.index:
        trace = go.Box(x=df.loc[df.association == team, stat],
                       boxpoints='outliers',
                       marker=dict(size=3),
                       name=team)
        traces.append(trace)
    fig = go.Figure(data=traces, layout=layout)
    return dcc.Graph(id='boxplot', figure=fig)


@app.callback(Output('area_div', 'children'),
              [Input('stat_dcc', 'value')])
def update_area_plot(stat):
    row = gb[stat]
    layout = go.Layout(title=f'Weight Class Comparison - '
                             f'{stat2name[stat].split("(")[0]}',
                       titlefont=dict(size=28),
                       xaxis=dict(tickangle=315,
                                  title='Weight Class'),
                       yaxis=dict(range=[0.9*row.min(), row.max()*1.1],
                                  title=stat2name[stat].split('(')[0]),
                       showlegend=False)
    trace = go.Scatter(x=gb.index,
                       y=row,
                       fill='tonexty',
                       mode='lines+markers',
                       line=dict(width=6),
                       marker=dict(size=10),
                       name=stat,
                       showlegend=True)
    fig = go.Figure(data=[trace], layout=layout)
    return dcc.Graph(id='area_plot', figure=fig)


@app.callback(Output('polar_div', 'children'),
              [Input('name_dcc', 'value')])
def update_polar_plot(names):
    polar_stats = ['td_avg', 'slpm', 'sub_avg', 'sapm']
    polar_names = ['Mean Takedowns <br>per 15 Minutes',
                   'Strikes <br>Landed/Minute',
                   'Mean Submission <br>Attempts per 15 Minutes',
                   'Strikes <br>Absorbed/Minute']
    layout = go.Layout(polar=dict(radialaxis={'visible': True,
                                              'showline': False
                                              },
                                  angularaxis={'showline': True,
                                               'linewidth': 3}),
                       title='Fighter Comparison',
                       titlefont=dict(size=28),
                       showlegend=True,
                       height=600
                       )

    # Accumulate traces for each fighter.
    traces = []
    for name in names:
        data = go.Scatterpolar(r=df.loc[df.name1 == name,
                                        polar_stats+[polar_stats[0]]].values[0],
                               theta=polar_names+[polar_names[0]],
                               fill='toself',
                               name=name,
                               opacity=0.75,
                               mode='lines+markers',
                               line=dict(width=2),
                               marker=dict(size=1)
                               )
        traces.append(data)
    fig = go.Figure(data=traces, layout = layout)
    return dcc.Graph(id='polar_plot', figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True, port=5000)
