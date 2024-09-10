from dash import html

import views.context_view
import views.nav_view


class HomePage(object):
    """Class that displays the homepage"""

    def __init__(
        self,
    ):
        pass

    def generate_context(self):
        context_view = views.context_view.ContextView()
        navbar_view = views.nav_view.NavView()

        content = html.Div(
            [
                navbar_view.generate_context(),
                context_view.generate_context(),
            ]
        )

        return content


if __name__ == "__main__":
    raise RuntimeError("[ERROR] This module cannot be run like a script.")
