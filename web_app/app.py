import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


app = dash.Dash(
                external_stylesheets=[dbc.themes.DARKLY],
                use_pages=True,
                prevent_initial_callbacks=True,
                suppress_callback_exceptions=True,
                update_title=None,
                title='Lapis.io')


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page['name'], href=page["relative_path"]))
        for page in filter(lambda page : page["relative_path"] != "/",  list(dash.page_registry.values()))
    ],
    brand="Lapis",
    brand_href="/",
    color="secondary",
    dark=True,
)

app.layout = html.Div([
    html.Div(navbar),
    html.Div(dash.page_container, className="mt-2")
    
])

if __name__ == '__main__':
    app.run(debug=True)