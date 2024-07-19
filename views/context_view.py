from dash import dcc, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import cv2
import os


class ContextView(object):
    def __init__(self) -> None:
        self.show_instructions = False

    def _generate_instructions(self):
        instructions_toast = dbc.Toast(
            [
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            "Match points in the images. Always select the first point from the left image."
                        ),
                        dbc.ListGroupItem(
                            "Each match will be annotated with a number corresponding to the clicking order."
                        ),
                        dbc.ListGroupItem(
                            'The matches are saved as JSON files in the following format: {"matches": [{"x1": px, "y1": px, "x2": px, "y2": px}]}'
                        ),
                        dbc.ListGroupItem(
                            'If no matches are chosen, the annotation will contain {"matches": null}'
                        ),
                    ],
                    numbered=True,
                ),
            ],
            id="instruction_toast",
            header="Instructions",
            is_open=self.show_instructions,
            dismissable=True,
            icon="info",
            style={"position": "fixed", "top": 60, "right": 10, "max-width": 640},
        )
        return instructions_toast

    def _create_empty_bg_figure(self):
        GS = 100

        fig = px.scatter(
            x=np.repeat(np.linspace(0, 1, GS), GS),
            y=np.tile(np.linspace(0, 1, GS), GS),
        ).update_traces(marker_color="rgba(0,0,0,0)")

        fig.update_xaxes(fixedrange=True, zeroline=True, showgrid=False)
        fig.update_yaxes(fixedrange=True, zeroline=True, showgrid=False)
        fig.update_layout(
            margin={"l": 0, "r": 0, "t": 70, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
            yaxis_title=None,
            xaxis_title=None,
        )

        return fig

        # return {
        #     "data": [
        #         px.scatter(
        #             x=np.repeat(np.linspace(0, 1, GS), GS),
        #             y=np.tile(np.linspace(0, 1, GS), GS),
        #         )  # .update_traces(marker_color="rgba(0,0,0,0)")
        #     ],
        #     "layout": {
        #         "xaxis": {
        #             # "range": [0, 2],
        #             # "showgrid": False,
        #             "zeroline": False,
        #             # "visible": False,
        #             "fixedrange": True,  # Disables zoom in
        #         },
        #         "yaxis": {
        #             # "range": [0, 1],
        #             # "showgrid": False,
        #             "zeroline": False,
        #             # "visible": False,
        #             "fixedrange": True,  # Disables zoom in
        #         },
        #         "margin": {"l": 0, "r": 0, "t": 70, "b": 0},
        #         "paper_bgcolor": "rgba(0,0,0,0)",  # Transparent background
        #         "plot_bgcolor": "rgba(0,0,0,0)",  # Transparent plot area
        #         "shapes": [],
        #     },
        # }

    def _generate_display(self):
        # At some point get a path to an image we want to annotate
        self.path = None

        if self.path:
            display_content = html.Div(id="rand")
        else:
            # No images chosen
            display_content = dbc.Row(
                [
                    # html.P(
                    #     "No images in the input folder.",
                    #     style={"padding": "15px", "margin-bottom": "0px"},
                    # ),
                    # Add two Store components for line visualization
                    # dcc.Store(id="points-store-1", data=[]),
                    # dcc.Store(id="points-store-2", data=[]),
                    # dcc.Graph(
                    #     id="line-graph",
                    #     figure=self._create_empty_bg_figure(),
                    #     config={"displayModeBar": False},  # , "staticPlot": True},
                    #     style={
                    #         "position": "absolute",
                    #         "width": "100%",
                    #         "height": "100%",
                    #         "z-index": 1,
                    #         "pointer-events": "all",
                    #         "opacity": 0,
                    #     },
                    # ),
                    dcc.Store(id="store-last-annot", data=""),
                    dbc.Col(
                        [
                            dcc.Upload(
                                id="upload-image",
                                children=html.Div(
                                    [
                                        "Drag and Drop or ",
                                        html.A(
                                            "Select File",
                                            style={"font-weight": "bold"},
                                        ),
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
                            html.Div(
                                id="output-image-upload",
                                style={
                                    "maxWidth": "100%",
                                    "margin": "10px",
                                    "zIndex": 2,
                                },
                            ),
                        ],
                        style={"width": "50%"},
                    ),
                    dbc.Col(
                        [
                            dcc.Upload(
                                id="upload-image-two",
                                children=html.Div(
                                    [
                                        "Drag and Drop or ",
                                        html.A(
                                            "Select File",
                                            style={"font-weight": "bold"},
                                        ),
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
                            html.Div(
                                id="output-image-upload-two",
                                style={
                                    "maxWidth": "100%",
                                    "margin": "10px",
                                    "zIndex": 2,
                                },
                            ),
                        ],
                        style={"width": "50%"},
                    ),
                    # html.Div(  # SVG container
                    #     id="svg-container",
                    #     style={
                    #         "position": "absolute",
                    #         "top": 0,
                    #         "left": 0,
                    #         "width": "100%",
                    #         "height": "100%",
                    #         "pointerEvents": "none",
                    #         "zIndex": 3,
                    #     },
                    # ),
                ],
                style={"width": "100%"},
            )
            header = "Choose two images and match corresponding points."

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
            style={"width": "100%", "margin-left": "10px"},
            body_style={"padding": "0px 0px 0px 0px", "margin": "0px 0px 0px 0px"},
        )

        return display_content_toast

    def _generate_matches(self):
        matches_content_toast = dbc.Toast(
            [
                dbc.ListGroup(
                    id="matched_points",
                    children=[],
                    style={"border": "0px", "border-radius": "0%"},
                    className="mb-0",
                    numbered=True,
                ),
            ],
            header="Matched Points",
            style={"maxWidth": "400px"},
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
                        dbc.Col(
                            display_content_toast,
                            style={"padding-right": "0px", "maxWidth": "100%"},
                            width=9,
                        ),
                        dbc.Col(
                            matches_content_toast,
                            style={"padding-right": "0px", "margin-right": "0px"},
                            width=3,
                        ),
                    ],
                    class_name="mb-3",
                ),
                # generate instructions here
                instructions_toast,
            ],
            style={"width": "100%"},
        )

        return content


if __name__ == "__main__":
    raise RuntimeError("[ERROR] This module cannot be run like a script.")
