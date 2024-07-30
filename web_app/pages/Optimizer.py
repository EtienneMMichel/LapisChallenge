import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback, dcc
import pandas as pd
import plotly.express as px
import numpy as np

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
        dcc.Dropdown(ZONES, id='portfolio_optimizer-zones'),
    ],className="mb-3"),

    html.Div(
    [
        dbc.Label("Competition"),
        dcc.Dropdown(COMPETITIONS, id='portfolio_optimizer-competitions'),
    ],className="mb-3"),

    html.Div([
        dbc.Label("Forecaster model"),
        dcc.Dropdown(FORECASTER_MODELS, FORECASTER_MODELS[0], id='portfolio_optimizer-forecaster_selector'),
    ],className="mb-3"),

    html.Div([
        dbc.Label("Optimizer models"),
        dcc.Dropdown(OPTIMIZER_MODELS, OPTIMIZER_MODELS[0], id='portfolio_optimizer-optimizer_selector', multi=True),
    ],className="mb-3"),

    dbc.Button("Launch Analysis", id="portfolio_optimizer-launch_button", n_clicks=0, color="secondary", className="mb-3")

])

controls = dbc.Card(
    data_selector,
    body=True,
)

analysis = dbc.Spinner(
            [
                dcc.Store(id='portfolio_optimizer-results'),
                html.Div([dcc.Graph(id="portfolio_historic")]),
                html.Hr(),
                html.H4("REWARDS"),
                html.Div(id="portfolio_optimizer-table-rewards"),
                html.H4("GAIN"),
                html.Div(id="portfolio_optimizer-table-gain"),
                html.H4("REWARDS"),
                html.Div(id="portfolio_optimizer-table-drawdown"),
            ],
            delay_show=100,
        )




layout = dbc.Container(
            [
                html.H1("Portfolio Optimization Backtesting"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(controls, md=4),
                        dbc.Col(analysis, md=8),
                    ],
                    # align="center",
                ),
            ],
            fluid=True,
        )




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
        data[optimizer] = rewards

        # portfolio = [1]
        # for r in rewards[:-1]:
        #     portfolio.append(portfolio[-1]*(1+r))
        # data[f"portfolio_{optimizer}"] = portfolio
    
    df = pd.DataFrame(data)

    fig = px.line(df, x="date", y=optimizers_name, title='returns')
    fig.update_layout(template="plotly_dark")
    return fig



@callback(Output("portfolio_optimizer-table-rewards", "children"), [Input('portfolio_optimizer-results', 'data')])
def make_table_rewards(jsonified_data):
    data = {}
    optimizers_name = list(jsonified_data[0]["rewards"].keys())
    data["measures"] = ["mean",
                        "median",
                        "sharpe ratio",
                        ]
    for optimizer in optimizers_name:
        rewards =  np.array([r["rewards"][optimizer] for r in jsonified_data])
        rewards_mean = np.round(rewards.mean(),3)
        rewards_median = np.round(np.median(rewards),3)
        rewards_std =   rewards.std()
        rewards_sharpe_ratio = np.round(rewards_mean/rewards_std,3)

        gain = np.array(list(filter(lambda r: r>0, rewards)))
        drawdown = np.array(list(filter(lambda r: r<0, rewards)))

        data[optimizer] = [rewards_mean,
                           rewards_median,
                           rewards_sharpe_ratio,
                           ]

    df = pd.DataFrame(data)
    return dbc.Table.from_dataframe(df, striped=True, bordered=False, hover=False, index=False)



@callback(Output("portfolio_optimizer-table-gain", "children"), [Input('portfolio_optimizer-results', 'data')])
def make_table_rewards(jsonified_data):
    data = {}
    optimizers_name = list(jsonified_data[0]["rewards"].keys())
    data["measures"] = [
                        "proportion",
                        "mean",
                        "max", 
                        ]
    for optimizer in optimizers_name:
        rewards =  np.array([r["rewards"][optimizer] for r in jsonified_data])
        rewards_mean = np.round(rewards.mean(),3)
        rewards_median = np.round(np.median(rewards),3)
        rewards_std =   rewards.std()
        rewards_sharpe_ratio = np.round(rewards_mean/rewards_std,3)

        gain = np.array(list(filter(lambda r: r>0, rewards)))
        drawdown = np.array(list(filter(lambda r: r<0, rewards)))

        data[optimizer] = [
                           f"{np.round(len(gain)/len(rewards)*100,1)}%",
                           np.round(gain.mean(),3),
                           np.round(gain.max(),3),
                           ]

    df = pd.DataFrame(data)
    return dbc.Table.from_dataframe(df, striped=True, bordered=False, hover=False, index=False, color="success")




@callback(Output("portfolio_optimizer-table-drawdown", "children"), [Input('portfolio_optimizer-results', 'data')])
def make_table_rewards(jsonified_data):
    data = {}
    optimizers_name = list(jsonified_data[0]["rewards"].keys())
    data["measures"] = [
                        "proportion",
                        "mean",
                        "max",
                        ]
    for optimizer in optimizers_name:
        rewards =  np.array([r["rewards"][optimizer] for r in jsonified_data])
        rewards_mean = np.round(rewards.mean(),3)
        rewards_median = np.round(np.median(rewards),3)
        rewards_std =   rewards.std()
        rewards_sharpe_ratio = np.round(rewards_mean/rewards_std,3)

        gain = np.array(list(filter(lambda r: r>0, rewards)))
        drawdown = np.array(list(filter(lambda r: r<0, rewards)))

        data[optimizer] = [
                           f"{np.round(len(drawdown)/len(rewards)*100,1)}%",
                           np.round(drawdown.mean(),3),
                           np.round(drawdown.min(),3)
                           
                           ]

    df = pd.DataFrame(data)
    return dbc.Table.from_dataframe(df, striped=True, bordered=False, hover=False, index=False, color="danger")