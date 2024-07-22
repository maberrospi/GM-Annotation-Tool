from dash import Dash, html, dcc
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import cv2
from PIL import Image
import io
import os
import base64
import inspect
import json
from pathlib import Path

import functionalities.annotator
import homepage

app = Dash(__name__, suppress_callback_exceptions=True)
app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

# Create annotation functionality objects
left_annotator = functionalities.annotator.MatchAnnotator(name="left")
right_annotator = functionalities.annotator.MatchAnnotator(name="right")

# Define CWD
CWD_PATH = Path.cwd()


@app.callback(
    dash.dependencies.Output("page-content", "children"),
    dash.dependencies.Input("url", "pathname"),
)
def display_page(pathname):
    # HTTP GET of any URL
    if pathname is not None:
        return homepage.HomePage().generate_context()


@app.callback(
    dash.dependencies.Output("instruction_toast", "is_open"),
    dash.dependencies.Input("instructions_toggle", "n_clicks"),
)
def display_instructions(n_clicks):
    return True if n_clicks or n_clicks > 0 else False


@app.callback(
    dash.dependencies.Output("save-button", "disabled"),
    dash.dependencies.Output("undo-button", "disabled"),
    dash.dependencies.Output("clear-button", "disabled"),
    dash.dependencies.Output("upload-json", "disabled"),
    dash.dependencies.Input("output-image-upload", "children"),
    dash.dependencies.Input("output-image-upload-two", "children"),
)
def enable_disable_buttons(div_children_one, div_children_two):
    # Enable buttons only if both images have been loaded.
    if (
        div_children_one
        and "children" in div_children_one[0]["props"]
        and any("type" in ch for ch in div_children_one[0]["props"]["children"])
        and any(
            [
                True if ch["type"] == "Graph" else False
                for ch in div_children_one[0]["props"]["children"][:]
            ]
        )
    ) and (
        div_children_two
        and "children" in div_children_two[0]["props"]
        and any("type" in ch for ch in div_children_two[0]["props"]["children"])
        and any(
            [
                True if ch["type"] == "Graph" else False
                for ch in div_children_two[0]["props"]["children"][:]
            ]
        )
    ):
        return (False, False, False, False)
    else:
        return (True, True, True, True)


def parse_contents(contents, filename, date, f_name):

    max_display_width = 512
    min_display_width = 250

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
    if img.shape[1] > max_display_width or img.shape[1] <= min_display_width:
        scale_factor = max_display_width / img.shape[1]
        width = int(round(img.shape[1] * scale_factor))
        height = int(round(img.shape[0] * scale_factor))
        resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
    else:
        resized = img

    # Enlarge the image if its too small
    # if img.shape[1] <= min_display_width:
    #     scale_factor = max_display_width / img.shape[1]
    #     width = int(round(img.shape[1] * scale_factor))
    #     height = int(round(img.shape[0] * scale_factor))
    #     resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)

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

    img = resized.copy()

    # Convert the image string to numpy array and create a
    # Plotly figure, see https://plotly.com/python/imshow/
    if len(img.shape) == 3:
        fig = px.imshow(img)
    elif len(img.shape) == 2:
        fig = px.imshow(img, binary_string=True)  # Grayscale
    else:
        return html.Div(["There was an error processing this file."])
        # raise Exception("The created graph does not contain any nodes.")

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
        children = [
            parse_contents(c, n, d, str(inspect.stack()[0][3]))
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


def click_event_handler(
    clickData, annotator, fig, matched_points: list
):  # , line_g_hover, vis_pts
    # Click on the graph canvas
    # Pass clicks to the annotator
    points = clickData.get("points")[0]
    x = points.get("x")
    y = points.get("y")
    idx = len(annotator.clicks)
    annotator.add_click(x, y)
    print(annotator, annotator.clicks)

    # Add points to store for line visuaization
    # line_x = line_g_hover["points"][0]["x"]
    # line_y = line_g_hover["points"][0]["y"]
    # vis_pts.append((line_x, line_y))
    # print(vis_pts)

    fig = go.Figure(fig)
    # Update the figure with the new annotation
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            showlegend=False,
            mode="markers",
            name="Match " + str(idx + 1),
            marker=dict(size=12),
            marker_line=dict(width=2, color="DarkSlateGrey"),
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

    return fig, matched_points  # , vis_pts


@app.callback(
    dash.dependencies.Output("left_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("matched_points", "children", allow_duplicate=True),
    dash.dependencies.Output("store-last-annot", "data", allow_duplicate=True),
    dash.dependencies.Input("left_graph", "clickData"),
    dash.dependencies.State("left_graph", "figure"),
    dash.dependencies.State("matched_points", "children"),
    # dash.dependencies.State("line-graph", "hoverData"),
    # dash.dependencies.State("points-store-1", "data"),
    prevent_initial_call=True,
)
def handle_left_click(clickData, fig, matched_points):  # , line_g_hover, vis_pts_1
    # print(line_g_hover)
    if not clickData or len(left_annotator.clicks) > len(right_annotator.clicks):
        raise PreventUpdate
    else:
        # print(fig["data"])
        figure, matched_points_view = click_event_handler(
            clickData, left_annotator, fig, matched_points
        )  # , line_g_hover, vis_pts_1
        # Update the last annotated stored value
        store_last_annot = "left"

        return figure, matched_points_view, store_last_annot  # , vis_pts


@app.callback(
    dash.dependencies.Output("right_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("matched_points", "children", allow_duplicate=True),
    dash.dependencies.Output("store-last-annot", "data", allow_duplicate=True),
    dash.dependencies.Input("right_graph", "clickData"),
    dash.dependencies.State("right_graph", "figure"),
    dash.dependencies.State("matched_points", "children"),
    # dash.dependencies.State("line-graph", "hoverData"),
    # dash.dependencies.State("points-store-2", "data"),
    prevent_initial_call=True,
)
def handle_right_click(clickData, fig, matched_points):  # , line_g_hover, vis_pts_2
    if not clickData or len(left_annotator.clicks) <= len(right_annotator.clicks):
        raise PreventUpdate
    else:
        # print(fig["data"])
        figure, matched_points_view = click_event_handler(
            clickData, right_annotator, fig, matched_points
        )  # , line_g_hover, vis_pts_2
        # Update the last annotated stored value
        store_last_annot = "right"

        return figure, matched_points_view, store_last_annot  # , vis_pts


# @app.callback(
#     dash.dependencies.Output('background', 'figure'),
#     dash.dependencies.Input("right_graph", "clickData"),
#     dash.dependencies.State('left-image', 'figure'),
#     dash.dependencies.State('right-image', 'figure')
# )

# def draw_match_line(clickData,left_fig,right_fig):
# Determine the full x range across both images
#     left_x_range = left_figure['layout']['xaxis']['range']
# right_x_range = right_figure['layout']['xaxis']['range']
# full_x_range = [left_x_range[0], right_x_range[1]]


@app.callback(
    dash.dependencies.Output("matched_points", "children", allow_duplicate=True),
    dash.dependencies.Output("left_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("right_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("store-last-annot", "data", allow_duplicate=True),
    dash.dependencies.Input("undo-button", "n_clicks"),
    dash.dependencies.State("left_graph", "figure"),
    dash.dependencies.State("right_graph", "figure"),
    dash.dependencies.State("store-last-annot", "data"),
    prevent_initial_call=True,
)
def undo_event_handler(undo_n_clicks, l_fig, r_fig, last_annotation):
    if undo_n_clicks:
        if not left_annotator.clicks:
            raise PreventUpdate
        if last_annotation == "left":
            updated_last_annot = "right"
            # Update figures
            l_fig["data"].pop()
            # Update annotation points
            left_annotator.clicks.pop()
        elif last_annotation == "right":
            updated_last_annot = "left"
            # Update figures
            r_fig["data"].pop()
            # Update annotation points
            right_annotator.clicks.pop()

        updated_matched_points = []

        for points in zip(left_annotator.clicks, right_annotator.clicks):
            left_point, right_point = points[0], points[1]
            new_point = dbc.ListGroupItem(
                f"x = {left_point['x']}, y = {left_point['y']} -> x = {right_point['x']}, y = {right_point['y']}"
            )
            updated_matched_points.append(new_point)

        if len(left_annotator.clicks) != len(right_annotator.clicks):
            # The last point from the left annotator was skipped so add it
            new_point = dbc.ListGroupItem(
                f"x = {left_annotator.clicks[-1]['x']}, y = {left_annotator.clicks[-1]['y']}"
            )
            updated_matched_points.append(new_point)

        return updated_matched_points, l_fig, r_fig, updated_last_annot
    else:
        raise PreventUpdate


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


def create_JSON_annotation():
    real_clicks = []

    for clicks in zip(left_annotator.clicks, right_annotator.clicks):
        left_clks = clicks[0]
        right_clks = clicks[1]
        left_scale_factor = left_annotator.scale_factor
        right_scale_factor = right_annotator.scale_factor
        real_clicks.append(
            {
                "x1": int(round(left_clks["x"] / left_scale_factor)),
                "y1": int(round(left_clks["y"] / left_scale_factor)),
                "x2": int(round(right_clks["x"] / right_scale_factor)),
                "y2": int(round(right_clks["y"] / right_scale_factor)),
            }
        )

    return {"matches": real_clicks}


@app.callback(
    dash.dependencies.Output("save-modal", "is_open"),
    dash.dependencies.Output("page-content", "children", allow_duplicate=True),
    dash.dependencies.Output("save-button", "n_clicks"),
    dash.dependencies.Output("success-pop-up", "is_open"),
    dash.dependencies.Input("save-button", "n_clicks"),
    dash.dependencies.Input("close-message", "n_clicks"),
    dash.dependencies.State("save-modal", "is_open"),
    prevent_initial_call=True,
)
def save_event_handler(save_n_clicks, close_n_clicks, modal_is_open):
    # First time running it
    if save_n_clicks is None:
        raise PreventUpdate

    changed_btn_id = [b["prop_id"] for b in dash.ctx.triggered][0]

    if changed_btn_id == "close-message.n_clicks":
        return not modal_is_open, dash.no_update, save_n_clicks, dash.no_update
    elif changed_btn_id == "save-button.n_clicks":

        l_annot_n_clicks = len(left_annotator.clicks)
        r_annot_n_clicks = len(right_annotator.clicks)
        if l_annot_n_clicks != r_annot_n_clicks:
            # print(not modal_is_open)
            return not modal_is_open, dash.no_update, 0, dash.no_update

        im1_path = left_annotator.img_path.split(".")[0]
        im2_path = right_annotator.img_path.split(".")[0]
        json_fname = im1_path + "-" + im2_path + ".json"
        output_dir = left_annotator.output_dir  # Left dir == right dir
        dst_path = os.path.join(CWD_PATH, output_dir, json_fname)
        Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

        if l_annot_n_clicks == 0 and r_annot_n_clicks == 0:
            json_dict = {"matches": None}
        else:
            json_dict = create_JSON_annotation()

        with open(dst_path, "w") as json_file:
            json.dump(json_dict, json_file)

        # If save succesfully reset annotations for next pair
        left_annotator.reset_all_annotations()
        right_annotator.reset_all_annotations()

        return modal_is_open, homepage.HomePage().generate_context(), 0, True


@app.callback(
    dash.dependencies.Output("json-error", "is_open"),
    dash.dependencies.Output("left_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("right_graph", "figure", allow_duplicate=True),
    dash.dependencies.Output("matched_points", "children", allow_duplicate=True),
    dash.dependencies.Input("upload-json", "contents"),
    dash.dependencies.Input("upload-json", "filename"),
    dash.dependencies.State("left_graph", "figure"),
    dash.dependencies.State("right_graph", "figure"),
    prevent_initial_call=True,
)
def upload_JSON_annotation(contents, filename, left_fig, right_fig):
    if contents is None:
        raise PreventUpdate

    if not filename.endswith(".json"):
        return True, dash.no_update, dash.no_update, dash.no_update

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    # Load annotations
    data = json.loads(decoded)
    matches = data.get("matches")
    # print(matches)

    if matches is None:
        return True, dash.no_update, dash.no_update, dash.no_update

    left_annotator.reset_all_annotations()
    right_annotator.reset_all_annotations()

    l_fig = go.Figure(left_fig)
    r_fig = go.Figure(right_fig)
    updated_matched_points = []

    l_fig["data"] = [l_fig["data"][0]]
    r_fig["data"] = [r_fig["data"][0]]

    for idx, points in enumerate(matches):
        # Pass clicks to the annotator
        x1 = round(points.get("x1") * left_annotator.scale_factor)
        y1 = round(points.get("y1") * left_annotator.scale_factor)
        x2 = round(points.get("x2") * right_annotator.scale_factor)
        y2 = round(points.get("y2") * right_annotator.scale_factor)

        left_annotator.add_click(x1, y1)
        right_annotator.add_click(x2, y2)
        # print(annotator, annotator.clicks)

        # Add points to store for line visuaization
        # line_x = line_g_hover["points"][0]["x"]
        # line_y = line_g_hover["points"][0]["y"]
        # vis_pts.append((line_x, line_y))
        # print(vis_pts)

        # Update the figures with the new annotations
        l_fig.add_trace(
            go.Scatter(
                x=[x1],
                y=[y1],
                showlegend=False,
                mode="markers",
                name="Match " + str(idx + 1),
                marker=dict(size=12),
                marker_line=dict(width=2, color="DarkSlateGrey"),
            )
        )
        r_fig.add_trace(
            go.Scatter(
                x=[x2],
                y=[y2],
                showlegend=False,
                mode="markers",
                name="Match " + str(idx + 1),
                marker=dict(size=12),
                marker_line=dict(width=2, color="DarkSlateGrey"),
            )
        )

        # Update the Matched Points list
        new_point = dbc.ListGroupItem(f"x = {x1}, y = {y1} -> x = {x2}, y = {y2}")
        updated_matched_points.append(new_point)

    return dash.no_update, l_fig, r_fig, updated_matched_points


def main():
    # Create web app basic layout
    app.title = "Graph Matching Annotation Tool"
    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(
                id="page-content",
                children=[],
            ),
        ]
    )

    app.run(debug=True)


if __name__ == "__main__":
    main()
