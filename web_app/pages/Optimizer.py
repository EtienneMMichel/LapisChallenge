import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback, dcc
import pandas as pd
import plotly.express as px

from utils import api_provider
from utils import FORECASTER_MODELS, OPTIMIZER_MODELS, SPORTS, MIN_YEAR, MAX_YEAR, ZONES, COMPETITIONS

import json

dash.register_page(__name__)


data_selector = dbc.Form([
    html.Div(
    [
        dbc.Label("Sports"),
        dcc.Dropdown(SPORTS, SPORTS[0], id='portfolio_optimizer-sports'),
    ],className="mb-3"),

    html.Div(
    [
        dbc.Label("Date Range"),
        dcc.RangeSlider(MIN_YEAR, MAX_YEAR, 2, value=[MAX_YEAR - 2, MAX_YEAR], id='portfolio_optimizer-date'),
    ],className="mb-3"),

    html.Div(
    [
        dbc.Label("Zone"),
        dcc.Dropdown(ZONES, ZONES[0], id='portfolio_optimizer-zones'),
    ],className="mb-3"),

    html.Div(
    [
        dbc.Label("Competition"),
        dcc.Dropdown(COMPETITIONS, COMPETITIONS[0], id='portfolio_optimizer-competitions'),
    ],className="mb-3"),
])

forecaster_selector = html.Div([
    dbc.Label("Forecaster model"),
    dcc.Dropdown(FORECASTER_MODELS, FORECASTER_MODELS[0], id='portfolio_optimizer-forecaster_selector'),
],className="mb-3")

optimizer_selector = html.Div([
    dbc.Label("Optimizer models"),
    dcc.Dropdown(OPTIMIZER_MODELS, OPTIMIZER_MODELS[0], id='portfolio_optimizer-optimizer_selector', multi=True),
],className="mb-3")

launch_button = dbc.Button("Launch Analysis", id="portfolio_optimizer-launch_button", n_clicks=0, color="secondary", className="mb-3")

offcanvas = html.Div(
    [
        
        dbc.Offcanvas(
            [html.P(
                "This is the config section. "
                "feel free to play with parameters. "
                "Good analysis ;)"
            ),
            data_selector,
            forecaster_selector,
            optimizer_selector,
            launch_button],
            id="portfolio_optimizer-offcanvas",
            title="Config",
            is_open=False,
        ),
    ]
)



graph_analysis = html.Div([
        dcc.Graph(id='portfolio_historic'),
        dcc.Graph(id='portfolio_exploitation'),
    ], style={'display': 'inline-block', 'width': '49%'})



analysis = html.Div([
    dbc.Button("Config", id="portfolio_optimizer-open_offcanvas", n_clicks=0),
    dcc.Store(id='portfolio_optimizer-results'),
    graph_analysis,
])


layout = html.Div([offcanvas, analysis]) # add profil


@callback(
    Output("portfolio_optimizer-offcanvas", "is_open"),
    Input("portfolio_optimizer-open_offcanvas", "n_clicks"),
    [State("portfolio_optimizer-offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open



@callback(
    Output('portfolio_optimizer-results', 'data'),
    [
        Input('portfolio_optimizer-forecaster_selector', 'value'),
        Input('portfolio_optimizer-optimizer_selector', 'value'),
        Input('portfolio_optimizer-sports', 'value'),
        Input('portfolio_optimizer-zones', 'value'),
        Input('portfolio_optimizer-competitions', 'value'),
        Input('portfolio_optimizer-date', 'value'),
        Input("portfolio_optimizer-launch_button", "n_clicks")
    ]
    )
def results(forecaster_name:str, optimizers_name:list[str], sport:str, zone:str, competitions:list[str], dates: list[int], launch_button):
    if not launch_button is None:
        forecaster_condition = forecaster_name is None
        optimizer_condition = len(optimizers_name) == 0
        sport_condition = sport is None
        if forecaster_condition or optimizer_condition or sport_condition:
            return {}
        
        dates = [int(f"20{dates[0]}"), int(f"20{dates[1]}")]
        res =  api_provider.get_optimizer_backtest(sport, dates, forecaster_name, optimizers_name, zone, competitions)["data"]
        
        return res
    else:
        return {}
    

@callback(
    Output(component_id='portfolio_historic', component_property='figure'),
    [Input('portfolio_optimizer-results', 'data')]
)
def update_graph(jsonified_data):
    data = {}
    data["date"] = [r["date"] for r in jsonified_data]
    optimizers_name = list(jsonified_data[0]["rewards"].keys())
    for optimizer in optimizers_name:
        rewards =  [r["rewards"][optimizer] for r in jsonified_data]
        data[f"rewards_{optimizer}"] = rewards

        portfolio = [1]
        for r in rewards[:-1]:
            portfolio.append(portfolio[-1]*(1+r))
        data[f"portfolio_{optimizer}"] = portfolio
        

    
    df = pd.DataFrame(data)
    fig = px.line(df, x="date", y="rewards_dummy", title='Life expectancy in Canada')
    
    return fig
