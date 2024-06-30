from dash import dcc
import dash_bootstrap_components as dbc
from dash import html


class NavView(object):

    def generate_context(self):

        nav_content = dbc.Navbar(
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.A(
                                    dbc.NavbarBrand("Graph Matching Annotation Tool"),
                                ),
                                width=2,
                                style={"padding-top": "3px", "padding-left": "25px"},
                            ),
                        ]
                    )
                ],
                style={"width": "100%"},
            ),
            color="dark",
            dark=True,
        )

        return nav_content
