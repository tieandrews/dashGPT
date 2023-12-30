# Author: Ty Andrews
# Date: 2023-08-15
import dash
from dash import html
import dash_bootstrap_components as dbc
import os
from flask import Flask
from dotenv import load_dotenv, find_dotenv

from dashgpt.logs import get_logger

load_dotenv(find_dotenv())

logger = get_logger(__name__)

flask_server = Flask(__name__)

dash_app = dash.Dash(
    __name__,
    use_pages=True,
    server=flask_server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        os.path.join("src", "dashgpt", "assets", "styles.css"),
        "https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap",
    ],
    title="DashGPT",
    suppress_callback_exceptions=True,
)

# dash_app.index_string = """
# <!DOCTYPE html>
# <html>
# <head>
# <!-- Google tag (gtag.js) -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-Z0JFX6WWM6"></script>
# <script>
#   window.dataLayer = window.dataLayer || [];
#   function gtag(){dataLayer.push(arguments);}
#   gtag('js', new Date());

#   gtag('config', 'G-Z0JFX6WWM6');
# </script>

# {%metas%}
# <title>{%title%}</title>
# {%favicon%}
# {%css%}
# </head>
# <body>
# {%app_entry%}
# <footer>
# {%config%}
# {%scripts%}
# {%renderer%}
# </footer>
# </body>
# </html>
# """

dash_app.layout = html.Div(
    children=[dash.page_container],
    className="container-fluid",
    style={
        "width": "100%",
        "height": "100%",
        "overflow": "hidden",
    },
)
dash_app._favicon = "dashgpt.ico"

if __name__ == "__main__":

    dash_app.run(debug=False, port=8050)
