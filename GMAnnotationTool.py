from dash import Dash, html, dcc, ctx
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import cv2
from PIL import Image
import io
import base64
import inspect
from pathlib import Path

import functionalities.annotator
import homepage

app = Dash(__name__, suppress_callback_exceptions=True)
app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

# app.layout = [html.Div(children="Hello World")]

# Create functionality objects
left_annotator = functionalities.annotator.MatchAnnotator(name="left")
right_annotator = functionalities.annotator.MatchAnnotator(name="right")

# Define CWD
CWD_PATH = Path.cwd()


@app.callback(
    dash.dependencies.Output("page-content", "children"),
    dash.dependencies.Input("save-button", "n_clicks"),
    dash.dependencies.Input("url", "pathname"),
)
def display_page(n_clicks, pathname):
    # Click on the submit button
    if n_clicks is not None:
        return homepage.HomePage().generate_context()

    # HTTP GET of any URL
    if pathname is not None:
        return homepage.HomePage().generate_context()
        if pathname == "/instructions":
            pass
        else:
            pass


@app.callback(
    dash.dependencies.Output("instruction_toast", "is_open"),
    dash.dependencies.Input("instructions_toggle", "n_clicks"),
)
def display_instructions(n_clicks):
    return True if n_clicks else False


@app.callback(
    dash.dependencies.Output("save-button", "disabled"),
    dash.dependencies.Output("undo-button", "disabled"),
    dash.dependencies.Output("clear-button", "disabled"),
    dash.dependencies.Input("matched_points", "children"),
    prevent_initial_call=True,
)
def enable_disable_buttons(matched_points_list):
    # Enable the save,undo and clear selection buttons
    return (
        (True, True, True)
        if matched_points_list is None or len(matched_points_list) == 0
        else (False, False, False)
    )


def parse_contents(contents, filename, date, f_name):

    max_display_width = 512

    # Remove 'data:image/png;base64' from the image string,
    # see https://stackoverflow.com/a/26079673/11989081
    if "png;" in contents:
        data = contents.replace("data:image/png;base64,", "")
    elif "jpeg;" in contents:
        data = contents.replace("data:image/jpeg;base64,", "")

    try:
        img = Image.open(io.BytesIO(base64.b64decode(data)))
    except Exception as e:
        # print(e)
        return html.Div(["There was an error processing this file."])
    img = np.array(img)

    # Resize image to the standard width
    resized = None
    scale_factor = 1.0
    if img.shape[1] > max_display_width:
        scale_factor = max_display_width / img.shape[1]
        width = int(round(img.shape[1] * scale_factor))
        height = int(round(img.shape[0] * scale_factor))
        resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
    else:
        resized = img

    # Tell the annotator the info about the image we are currently annotating
    # functionalities.annotator.MatchAnnotator().new_image(filename, scale_factor)
    graph_div_id = ""
    graph_id = ""
    if f_name == "update_image":
        left_annotator.new_image(filename, scale_factor)
        graph_div_id = "left_graph_div"
        graph_id = "left_graph"
    elif f_name == "update_image_two":
        right_annotator.new_image(filename, scale_factor)
        graph_div_id = "right_graph_div"
        graph_id = "right_graph"

    # Plot image
    # img = resized[..., ::-1].copy()
    img = resized.copy()

    # Convert the image string to numpy array and create a
    # Plotly figure, see https://plotly.com/python/imshow/
    fig = px.imshow(img)

    # Configure axes
    fig.update_xaxes(
        visible=False,
        # range=[0, img.shape[1]],
        # fixedrange=False,  # This removes the zooming option
    )
    fig.update_yaxes(
        visible=False,
        # range=[img.shape[0], 0],
        # the scaleanchor attribute ensures that the aspect ratio stays constant
        scaleanchor="x",
    )

    # Configure figure layout
    fig.update_layout(
        width=img.shape[1],
        height=img.shape[0],
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )
    fig.update_traces(hovertemplate=None, hoverinfo="none")
    config = {
        "displayModeBar": True,
        "displaylogo": False,
        "doubleClick": False,
        "scrollZoom": True,
        "modeBarButtonsToRemove": [
            "zoom",
            "pan",
            "select",
            "zoomIn",
            "zoomOut",
            "resetScale",
            "lasso2d",
            "toImage",
        ],
        "modeBarButtonsToAdd": ["resetViews"],
        #'editable': True,
    }

    # Create canvas
    graph = dcc.Graph(
        id=graph_id,
        figure=fig,
        config=config,
        style={"height": "100%", "width": "100%"},
    )

    return html.Div(
        [
            html.H5(filename),
            # html.H6(datetime.datetime.fromtimestamp(date)),
            # HTML images accept base64 encoded strings in the same format
            # that is supplied by the upload
            graph,
            # html.Img(src=contents, style={"height": "100%", "width": "100%"}),
            # html.Hr(),
            # html.Div("Raw Content"),
            # html.Pre(
            #     contents[0:200] + "...",
            #     style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
            # ),
        ],
        id=graph_div_id,
    )


@app.callback(
    dash.dependencies.Output("output-image-upload", "children"),
    dash.dependencies.Input("upload-image", "contents"),
    dash.dependencies.State("upload-image", "filename"),
    dash.dependencies.State("upload-image", "last_modified"),
)
def update_image(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        # self.path = False
        children = [
            parse_contents(c, n, d, str(inspect.stack()[0][3]))
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


@app.callback(
    dash.dependencies.Output("output-image-upload-two", "children"),
    dash.dependencies.Input("upload-image-two", "contents"),
    dash.dependencies.State("upload-image-two", "filename"),
    dash.dependencies.State("upload-image-two", "last_modified"),
)
def update_image_two(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        # self.path = False
        children = [
            parse_contents(c, n, d, str(inspect.stack()[0][3]))
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


def click_event_handler(clickData, annotator, fig, matched_points: list):
    # Click on the graph canvas
    # Pass clicks to the annotator
    points = clickData.get("points")[0]
    x = points.get("x")
    y = points.get("y")
    idx = len(annotator.clicks)
    annotator.add_click(x, y)
    print(annotator, annotator.clicks)

    fig = go.Figure(fig)
    # Update the figure with the new annotation
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            showlegend=False,
            mode="markers",
            name="Match " + str(idx + 1),
        )
    )

    # Update the Matched Points list
    if annotator.name == "left":
        new_point = dbc.ListGroupItem(f"x = {x}, y = {y}")
        matched_points.append(new_point)
    elif annotator.name == "right":
        matched_points[-1] = dbc.ListGroupItem(
            matched_points[-1]["props"]["children"] + f" -> x = {x}, y = {y}"
        )

    return fig, matched_points


@app.callback(
    dash.dependencies.Output("left_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("matched_points", "children", allow_duplicate=True),
    dash.dependencies.Input("left_graph", "clickData"),
    dash.dependencies.State("left_graph", "figure"),
    dash.dependencies.State("matched_points", "children"),
    prevent_initial_call=True,
)
def handle_left_click(clickData, fig, matched_points):
    if not clickData or len(left_annotator.clicks) > len(right_annotator.clicks):
        raise PreventUpdate
    else:
        # print(fig["data"])
        figure, matched_points_view = click_event_handler(
            clickData, left_annotator, fig, matched_points
        )

        return figure, matched_points_view


@app.callback(
    dash.dependencies.Output("right_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("matched_points", "children", allow_duplicate=True),
    dash.dependencies.Input("right_graph", "clickData"),
    dash.dependencies.State("right_graph", "figure"),
    dash.dependencies.State("matched_points", "children"),
    prevent_initial_call=True,
)
def handle_right_click(clickData, fig, matched_points):
    if not clickData or len(left_annotator.clicks) <= len(right_annotator.clicks):
        raise PreventUpdate
    else:
        # print(fig["data"])
        figure, matched_points_view = click_event_handler(
            clickData, right_annotator, fig, matched_points
        )

        return figure, matched_points_view


def undo_event_handler(undo_n_clicks):
    pass


@app.callback(
    dash.dependencies.Output("matched_points", "children"),
    dash.dependencies.Output("left_graph", "figure"),
    dash.dependencies.Output("right_graph", "figure"),
    dash.dependencies.Input("clear-button", "n_clicks"),
    dash.dependencies.State("left_graph", "figure"),
    dash.dependencies.State("right_graph", "figure"),
    prevent_initial_call=True,
)
def clear_selection_handler(clear_n_clicks, l_fig, r_fig):
    if clear_n_clicks:
        left_annotator.reset_all_annotations()
        right_annotator.reset_all_annotations()

        # for trace in l_fig["data"][:]:
        #     if trace["type"] == "scatter":
        #         l_fig["data"].remove(trace)
        # for trace in r_fig["data"][:]:
        #     if trace["type"] == "scatter":
        #         r_fig["data"].remove(trace)

        l_fig["data"] = [l_fig["data"][0]]
        r_fig["data"] = [r_fig["data"][0]]

        return [], l_fig, r_fig
    else:
        raise PreventUpdate


def save_event_handler(save_n_clicks):
    pass


def main():
    # Create web app basic layout
    app.title = "Graph Matching Annotation Tool"
    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(
                id="page-content",
                children=[
                    html.Div(
                        id="submit-button-hidden-div",
                        style={"display": "none"},
                        children=[
                            dbc.Button(
                                "Submit",
                                id="save-button",
                                color="success",
                            ),
                        ],
                    ),  # Used for the callback, otherwise the page would not load
                    # as a button has to be created for the callback to work
                ],
            ),
        ]
    )

    app.run(debug=True)


if __name__ == "__main__":
    main()
