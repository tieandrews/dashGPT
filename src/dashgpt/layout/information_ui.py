# Author: Ty Andrews
# Date: 2023-09-21

import dash_mantine_components as dmc
from dash import dcc, html

from dashgpt.logs import get_logger

logger = get_logger(__name__)


def generate_information_modal(information_modal_id="information-modal"):
    information_modal = dmc.Modal(
        id=information_modal_id,
        title="DashGPT Information",
        size="xl",
        children=[
            html.H2("About DashGPT"),
            html.P(
                "DashGPT is a chat interface built entirely with Plotly Dash meant to be a template for production Dash chat apps."
            ),
            # bullet pointed list of features
            html.H5("Primary Features"),
            # written in markdown
            dcc.Markdown(
                """
                - **Chat Interface**: Simple UI and UX for users to interact with the chatbot.
                - **Retrieval Augmented Generation**: Uses a combination of retrieval and generative models to provide answers to user questions.
                - **User Feedback**: Users can provide feedback on the answers provided by the chatbot.
                """
            ),
            html.Hr(),
            html.H4("How to Use DashGPT"),
            # insert a image of the chat interface
            html.Img(
                src="/assets/images/getting-started-guide.png",
                style={"width": "100%", "height": "100%"},
            ),
        ],
    )

    return information_modal
