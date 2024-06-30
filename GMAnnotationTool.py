from dash import Dash, html
from dash import dcc
import dash
import dash_bootstrap_components as dbc

import homepage

app = Dash(__name__, suppress_callback_exceptions=True)
app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

# app.layout = [html.Div(children="Hello World")]


@app.callback(
    dash.dependencies.Output("page-content", "children"),
    dash.dependencies.Input("submit-button", "n_clicks"),
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


def parse_contents(contents, filename, date):
    return html.Div(
        [
            html.H5(filename),
            # html.H6(datetime.datetime.fromtimestamp(date)),
            # HTML images accept base64 encoded strings in the same format
            # that is supplied by the upload
            html.Img(src=contents),
            html.Hr(),
            html.Div("Raw Content"),
            html.Pre(
                contents[0:200] + "...",
                style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
            ),
        ]
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
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children


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
                                id="submit-button",
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
