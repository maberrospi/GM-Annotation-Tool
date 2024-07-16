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
                                width="auto",
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
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(
                                                dbc.ModalTitle("Unable to Save."),
                                                close_button=True,
                                            ),
                                            dbc.ModalBody(
                                                "Please make sure the images contain the same number of annotations."
                                            ),
                                            dbc.ModalFooter(
                                                dbc.Button(
                                                    "Close",
                                                    id="close-message",
                                                    class_name="ms-auto",
                                                    n_clicks=0,
                                                )
                                            ),
                                        ],
                                        id="save-modal",
                                        centered=True,
                                        is_open=False,
                                    ),
                                    dbc.Alert(
                                        "The annotations have been saved successfully!!!",
                                        id="success-pop-up",
                                        is_open=False,
                                        duration=5000,
                                        color="success",
                                        style={
                                            "position": "fixed",
                                            "bottom": 0,
                                            "right": 10,
                                        },
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
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Instructions",
                                    id="instructions_toggle",
                                    n_clicks=0,
                                ),
                                width="auto",  # width={"size": 1},  # , "offset": 4},
                                style={
                                    "position": "fixed",
                                    "top": 10,
                                    "right": 10,
                                },
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
