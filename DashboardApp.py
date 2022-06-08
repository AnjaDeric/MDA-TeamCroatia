import pandas as pd
from pandas.api.types import CategoricalDtype
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
from dash import Dash, dcc, html, Input, Output
from datetime import date
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import networkx as nx


app = Dash(__name__)
server = app.server

# data cleaning
url = "https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/Data/Mid-Points/county_info_with_key.csv"
df = pd.read_csv(url, dtype={"fips": str}).to_dict(orient='records')
df_counties = pd.read_csv(url)

url2 = "https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/active_cases.csv"
df_active = pd.read_csv(url2, dtype={"fips": str})
df_long = pd.melt(df_active, id_vars=['fips', 'county'], value_vars=df_active.columns[6:], var_name='date',
                  value_name='cases')
df_long['Date'] = df_long['date'].str[5:9] + '-' + df_long['date'].str[1:3] + '-' + df_long['date'].str[3:5]

url3 = "https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/Data/adj_dist_all_final.csv"
df_edges = pd.read_csv(url3)
df_edges['county_fips'] = df_edges['county_fips'].apply('{:0>5}'.format)
df_edges['bcounty_fips'] = df_edges['bcounty_fips'].apply('{:0>5}'.format)
H = nx.Graph()
H = nx.from_pandas_edgelist(df_edges, source = 'county_fips', target = 'bcounty_fips', edge_attr = 'gc_dist_km')

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("Covid19 in the USA", style={'text-align': 'center'}),
    html.Div(children=[
            html.Div(children=[
                html.H4("From:"),
                dcc.Dropdown(id="county_from",
                    options=[{'label': i['combined_key'], 'value': i['fips']} for i in df],
                    multi=False,
                    value='49003',
                    style={'width': "90%"}
                    )],style=dict(width='45%', display='inline-block')),
            html.Div(children=[
                html.H4("To:"),
                dcc.Dropdown(id="county_to",
                    options=[{'label': i['combined_key'], 'value': i['fips']} for i in df],
                    multi=False,
                    value='47185',
                    style={'width': "90%"}
                    )],style=dict(width='45%', display='inline-block')),
            html.Div(children=[
                html.H4("Pick a date"),
                dcc.DatePickerSingle(
                    id='date_selected',
                    min_date_allowed=date(2021, 1, 1),
                    max_date_allowed=(dt.date.today() - dt.timedelta(days=2)),
                    initial_visible_month=date(2021, 1, 31),
                    date=(dt.date.today() - dt.timedelta(days=2))
                    )],style=dict(width='45%', display='inline-block')),
            html.Div(children=[
                html.H4("Number of clusters"),
                dcc.Dropdown(id="n_clust",
                    options=[{'label': x, 'value': x} for x in range(1,21)],
                    multi=False,
                    value=3,
                   style={'width': "90%"}
                    )], style=dict(width='45%', display='inline-block'))
            ], style=dict(display='flex')),

    html.Div(id='output-container-date-picker-single'),
    html.Br(),

    html.Div(children=[
            dcc.Loading(id="loading",type="graph",children=[
            html.Div(children=[
                html.Div(children=[dcc.Graph(id='map', figure={})], style=dict(align='left', width='90%', display='inline-block')),
                html.Div(children=[html.H3("Safest Path"),
                                   html.Div(id='km_sapa', children=[]),
                                   html.Div(id='cases_sapa', children=[]),
                                   html.Div(id='counties_sapa', children=[]),
                                   html.H3("Shortest Path"),
                                   html.Div(id='km_shopa', children=[]),
                                   html.Div(id='cases_shopa', children=[]),
                                   html.Div(id='counties_shopa', children=[]),
                                   ], style=dict(display='inline-block', width="30%",verticalAlign='middle'))],
                style=dict(display='flex'))],style=dict(width='100%', display='inline-block'))]),
            html.Div(children=[
                dcc.Loading(id="loading2",type="circle",children=[
                html.Div(children=[dcc.Graph(id='map2', figure={})], style=dict(align='left', width='100%', display='inline-block'))
                ], style=dict(display='inline-block', width="100%")),
                html.Div(children=[dcc.Graph(id='ts', figure={})], style=dict(width='75%', display='inline-block', centering='right'))],
                style=dict(display='flex'))
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

@app.callback(
    [Output(component_id='km_sapa', component_property='children'),
     Output(component_id='cases_sapa', component_property='children'),
     Output(component_id='counties_sapa', component_property='children'),
     Output(component_id='km_shopa', component_property='children'),
     Output(component_id='cases_shopa', component_property='children'),
     Output(component_id='counties_shopa', component_property='children'),
     Output(component_id='map', component_property='figure'),
     Output(component_id='ts', component_property='figure')],
    [Input(component_id='county_from', component_property='value'),
     Input(component_id='county_to', component_property='value'),
     Input(component_id='date_selected', component_property='date')]
)

def update_graph(option_1, option_2, option_3):

    option1_str='{:0>5}'.format(str(option_1))
    option2_str='{:0>5}'.format(str(option_2))

    date_split = option_3.split('-')
    if (len(date_split[2]) < 2):
        day_str = str(0) + str(date_split[2])
    else:
        day_str = str(date_split[2])
    if (len(date_split[1]) < 2):
        month_str = str(0) + str(date_split[1])
    else:
        month_str = str(date_split[1])
    year_str = date_split[0]
    date_str = 'd' +  month_str + day_str + year_str

    # subset data set for selected day
    data_covid_request = df_active.loc[:, ['fips', 'county', 'population', date_str]]
    data_covid_request.columns = ['fips', 'county', 'population', 'active_cases']
    data_covid_request['prop'] = 1000 * (data_covid_request['active_cases'] / data_covid_request['population'])

    url3 = "https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/Data/adj_dist_all_final.csv"
    df_edges = pd.read_csv(url3)
    df_edges['county_fips'] = df_edges['county_fips'].apply('{:0>5}'.format)
    df_edges['bcounty_fips'] = df_edges['bcounty_fips'].apply('{:0>5}'.format)

    # add active cases to df_adj
    df_edges = df_edges.merge(data_covid_request, left_on='county_fips', right_on='fips')
    df_edges = df_edges.merge(data_covid_request, left_on='bcounty_fips', right_on='fips')

    # prep
    source_nodes = df_edges.loc[:, 'county_fips'].astype(str)
    dest_nodes = df_edges.loc[:, 'bcounty_fips'].astype(str)
    data_nodes = df_edges.loc[:, 'active_cases_x'].astype(int)
    data2_nodes = df_edges.loc[:, 'active_cases_y'].astype(int)
    # create graph
    G = nx.MultiDiGraph()
    for u, v, d in zip(source_nodes, dest_nodes, data2_nodes):
        G.add_edge(u, v, cases=d, key='a')
    for u, v, d in zip(dest_nodes, source_nodes, data_nodes):
        G.add_edge(u, v, cases=d, key='a')
    # calculate safest path
    pathC = nx.single_source_dijkstra(G, option1_str, option2_str, weight='cases')
    pathC_counties = list(map(int, pathC[1]))
    safest_path = df_counties[df_counties['fips'].isin(pathC_counties)]
    pathC_order = CategoricalDtype(pathC_counties, ordered=True)
    safest_path['fips'] = safest_path['fips'].astype(pathC_order)
    safest_path.sort_values('fips', inplace=True)

    # calculate shortest path
    pathD = nx.single_source_dijkstra(H, option1_str, option2_str, weight='gc_dist_km')
    pathD_counties = list(map(int, pathD[1]))
    shortest_path = df_counties[df_counties['fips'].isin(pathD_counties)]
    pathD_order = CategoricalDtype(pathD_counties, ordered=True)
    shortest_path['fips'] = shortest_path['fips'].astype(pathD_order)
    shortest_path.sort_values('fips', inplace=True)

    # calculate total km/cases/counties for each path
    pathC_nNodes = len(pathC_counties)
    pathD_nNodes = len(pathD_counties)
    pathC_str = ["{:0>5}".format(item) for item in pathC_counties]
    pathD_str = ["{:0>5}".format(item) for item in pathD_counties]
    pathC_cases = nx.path_weight(G, pathC_str, weight='cases')
    pathC_km = round(nx.path_weight(H, pathC_str, weight='gc_dist_km'), 2)
    pathD_cases = nx.path_weight(G, pathD_str, weight='cases')
    pathD_km = round(nx.path_weight(H, pathD_str, weight='gc_dist_km'), 2)

    km_sapa = "Total distance: {}km".format(pathC_km)
    cases_sapa = "Total cases: {}".format(pathC_cases)
    counties_sapa = "Total counties: {}".format(pathC_nNodes)
    km_shopa = "Total distance: {}km".format(pathD_km)
    cases_shopa = "Total cases: {}".format(pathD_cases)
    counties_shopa = "Total counties: {}".format(pathD_nNodes)

    covidmap = px.choropleth_mapbox(data_covid_request, geojson=counties, locations='fips', color='prop', hover_name='county',
                                    hover_data=['fips', 'active_cases', 'population'], color_continuous_scale="sunsetdark",
                                    range_color=(data_covid_request['prop'].min(), data_covid_request['prop'].max()),
                                    mapbox_style="carto-positron", zoom=3.25, center={"lat": 37.0902, "lon": -95.7129},
                                    opacity=0.9, labels={'prop': 'Active cases <br> per thousand <br> residents'})

    col1 = "darkslategrey"
    col2 = "lightslategrey"

    covidmap.add_trace(go.Scattermapbox(
        name="Safest Path",
        mode="markers+lines",
        lon=safest_path['long'],
        lat=safest_path['lat'],
        marker=dict(size=7, color=col1),
        line=dict(width=4, color=col1)
        ))
    covidmap.add_trace(go.Scattermapbox(
        name="Shortest Path",
        mode="markers+lines",
        lon=shortest_path['long'],
        lat=shortest_path['lat'],
        marker=dict(size=7, color=col2),
        line=dict(width=4, color=col2)
        ))
    covidmap.update_traces(selector=dict(type='scattermapbox'))
    covidmap.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                           legend=dict( orientation="h",
                                        yanchor="bottom",#y=1.02,
                                        xanchor="right", x=1))

    dff = df_long[(df_long["fips"] == option1_str) | (df_long["fips"] == option2_str)]

    ts = px.line(dff, x='Date', y="cases", color='county',
                 hover_data={"Date": "|%B %d, %Y"}, color_discrete_sequence=['#E69F00', '#0072B2'] )
    ts.add_vline(x=option_3)
    ts.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y")
    ts.update_xaxes(rangeslider_visible=True)
    ts.update_layout(  # margin={"r": 0, "t": 0, "l": 0, "b": 0}
                        legend=dict(orientation="h",
                        yanchor="bottom",  # y=1.02,
                        xanchor="right", x=1))

    return km_sapa, cases_sapa, counties_sapa, km_shopa, cases_shopa, counties_shopa, covidmap, ts

@app.callback(
         Output(component_id='map2', component_property='figure'),
         Input(component_id='n_clust', component_property='value'))
def apply_clustering(option_4):

    url4 = "https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/Data/Counties_clustered.csv"
    df_clusters = pd.read_csv(url4)
    df_clusters['fips'] = df_clusters['fips'].apply('{:0>5}'.format)
    cluster_count = "clusters_{}".format(option_4)
    df_clusters[cluster_count] = df_clusters[cluster_count].astype(str)
    df_clusters = df_clusters.loc[:,['fips', 'county', 'state', 'lat', 'long', 'population', cluster_count]]

    covidmap2 = px.choropleth_mapbox(df_clusters, geojson=counties, locations='fips', color=cluster_count, hover_name='county',
                                 hover_data=['fips', 'state', 'population'],
                                 color_discrete_sequence=px.colors.qualitative.Dark24,
                                 mapbox_style="carto-positron", zoom=2.25, center={"lat": 37.0902, "lon": -95.7129},
                                 opacity=0.9, labels={cluster_count: 'cluster'})

    covidmap2.update_layout(legend=dict(orientation="h",yanchor="bottom", xanchor="right", x=1))

    return covidmap2
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
