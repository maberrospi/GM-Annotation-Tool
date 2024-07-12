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
                            dbc.Col(
                                [
                                    dbc.Button(
                                        "Save",
                                        id="save-button",
                                        color="success",
                                        style={"margin-right": "20px"},
                                        disabled=True,
                                    ),
                                    dbc.Button(
                                        "Undo",
                                        id="undo-button",
                                        color="secondary",
                                        style={"margin-right": "20px"},
                                        disabled=True,
                                    ),
                                    dbc.Button(
                                        "Clear Selection",
                                        id="clear-button",
                                        color="warning",
                                        disabled=True,
                                    ),
                                ],
                                width=2,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Instructions",
                                    id="instructions_toggle",
                                    n_clicks=0,
                                ),
                                width={"size": 1, "offset": 7},
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


if __name__ == "__main__":
    raise RuntimeError("[ERROR] This module cannot be run like a script.")
