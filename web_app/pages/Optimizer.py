import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback



dash.register_page(__name__)




offcanvas = html.Div(
    [
        
        dbc.Offcanvas(
            html.P(
                "This is the content of the Offcanvas. "
                "Close it by clicking on the close button, or "
                "the backdrop."
            ),
            id="optimizer_offcanvas",
            title="Title",
            is_open=False,
        ),
    ]
)

analysis = html.Div([
    dbc.Button("Open Config", id="open_optimizer_offcanvas", n_clicks=0),
])

layout = html.Div([offcanvas, analysis]) # add profil


@callback(
    Output("optimizer_offcanvas", "is_open"),
    Input("open_optimizer_offcanvas", "n_clicks"),
    [State("optimizer_offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open
