import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback, dcc

from .utils import api_provider
from .utils import FORECASTER_MODELS, OPTIMIZER_MODELS, SPORTS, MIN_YEAR, MAX_YEAR, ZONES, COMPETITIONS

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
    dbc.Button("Open Config", id="portfolio_optimizer-open_offcanvas", n_clicks=0),
    dcc.Store(id='portfolio_optimizer-results'),
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
def results(forecaster_name:str, optimizers_name:list[str], sport:str, zones:list[str], competitions:list[str], dates: list[int], launch_button):
    if not launch_button is None:
        forecaster_condition = forecaster_name is None
        optimizer_condition = len(optimizers_name) == 0
        sport_condition = sport is None
        if forecaster_condition or optimizer_condition or sport_condition:
            return {}
        payload = {
            "sport":sport,
            "start_year":dates[0],
            "end_year":dates[1],
            "zones":zones,
            "competitions":competitions,
            "forecaster_name":forecaster_name,
            "optimizers_name":optimizers_name
        }
        res =  api_provider.get_optimizer_backtest(payload)
        return res
    else:
        return {}