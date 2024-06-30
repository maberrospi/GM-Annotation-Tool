from dash import dcc, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
import plotly.express as pex
import cv2
import os

from GMAnnotationTool import app


class ContextView(object):
    def __init__(self) -> None:
        self.show_instructions = False

    def _generate_instructions(self):
        instructions_toast = dbc.Toast(
            [
                html.P(
                    "Match points in the images. Always select the first point from the left image.",
                    className="mb-0",
                ),
                html.P(
                    "Each match will be annotated with a number corresponding to the clicking order.",
                    className="mb-0",
                ),
            ],
            id="instruction_toast",
            header="Instructions",
            is_open=self.show_instructions,
            dismissable=True,
            icon="info",
            style={"position": "fixed", "top": 66, "right": 15, "max-width": 640},
        )
        return instructions_toast

    def _generate_display(self):
        # At some point get a path to an image we want to annotate
        self.path = None

        if self.path:
            display_content = html.Div(id="rand")
        else:
            # No images chosen
            display_content = dbc.Row(
                [
                    html.P(
                        "No images in the input folder.",
                        style={"padding": "15px", "margin-bottom": "0px"},
                    ),
                    dcc.Upload(
                        id="upload-image",
                        children=html.Div(
                            [
                                "Drag and Drop or ",
                                html.A("Select Files", style={"font-weight": "bold"}),
                            ]
                        ),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                        },
                        multiple=True,
                    ),
                    html.Div(id="output-image-upload", style={"width": "100%"}),
                ],
                style={"width": "100%"},
            )
            header = "Yay no files"

        display_content_toast = dbc.Toast(
            [
                html.Div(
                    [
                        display_content,
                    ],
                    id="display-div",
                    style={"width": "100%"},
                )
            ],
            header=header,
            style={"width": "100%", "maxWidth": "900px", "margin-left": "10px"},
            body_style={"padding": "0px 0px 0px 0px", "margin": "0px 0px 0px 0px"},
        )

        return display_content_toast

    def _generate_matches(self):
        matches_content_toast = dbc.Toast(
            [
                dbc.ListGroup(
                    id="matched-points",
                    children=[],
                    style={"border": "0px", "border-radius": "0%"},
                    className="mb-0",
                ),
            ],
            header="Matched Points",
            style={"width": "400px", "maxWidth": "400px"},
            body_style={"padding": "0px 0px 0px 0px", "margin": "0px 0px 0px 0px"},
        )
        return matches_content_toast

    def generate_context(self):
        instructions_toast = self._generate_instructions()
        display_content_toast = self._generate_display()
        matches_content_toast = self._generate_matches()

        content = html.Div(
            className="mt-3",
            children=[
                dbc.Row(
                    [
                        dbc.Col(display_content_toast, style={"padding-right": "0px"}),
                        dbc.Col(matches_content_toast, style={"padding-right": "0px"}),
                    ],
                    class_name="mb-3",
                ),
                dbc.Button(
                    "Instructions",
                    id="instructions_toggle",
                    n_clicks=0,
                    style={
                        "position": "fixed",
                        "top": 66,
                        "right": 10,
                    },
                ),
                # generate instructions here
                instructions_toast,
            ],
            style={"width": "100%"},
        )

        return content
