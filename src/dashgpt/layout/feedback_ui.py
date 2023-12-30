# Author: Ty Andrews
# Date: 2023-09-21

import os

import dash
import dash_mantine_components as dmc
from dash import callback, Output, Input, State
from dash import html
from dash_iconify import DashIconify
import re

from dashgpt.logs import get_logger

logger = get_logger(__name__)

FEEDBACK_TYPES = [
    ["not-funny", "Not Very Funny"],
    ["too-funny", "Too Funny"],
    ["incorrect-dangerous", "Incorrect & Dangerous"],
    ["other", "Other"],
]


def generate_feedback_modal(message_id: str):  # feedback_modal_id="feedback-modal"
    # ensure passed in message_id is a string
    if not isinstance(message_id, str):
        raise TypeError("message_id must be a string.")

    feedback_modal = dmc.Modal(
        id={"type": "feedback-modal", "index": message_id},
        title="Feedback",
        children=[
            # add info about how some of team isn't experts so specific feedback is helpful
            html.P(
                "We appreciate your feedback! Please provide as much detail as possible so we can improve our service.",
                style={"margin-bottom": "0px"},
            ),
            dmc.Textarea(
                id={"type": "feedback-text-area", "index": message_id},
                placeholder="Please provide feedback on the response.",
                minRows=4,
            ),
            dmc.RadioGroup(
                [dmc.Radio(l, value=k) for k, l in FEEDBACK_TYPES],
                id={"type": "feedback-type", "index": message_id},
                value="",
                label="What type of issue is this? (Required)",
                size="md",
                mt=10,
                required=True,
                persisted_props=[],  # don't persist the value
                persistence_type="session",
            ),
            html.Hr(),
            dmc.Button(
                "Submit",
                id={"type": "feedback-submit-button", "index": message_id},
                variant="gradient",
                gradient={"from": "#004D40", "to": "#2d695e"},
                radius="xl",
                style={"margin-right": "5px", "margin-left": "5px"},
                compact=True,
            ),
        ],
        size="lg",
    )

    return feedback_modal


def generate_thumbs_up_down_buttons(message_id: str):
    # ensure passed in message_id is a string
    if not isinstance(message_id, str):
        raise TypeError("message_id must be a string.")

    thumbs_up_button = dmc.Button(
        DashIconify(icon="octicon:thumbsup-16"),
        id={"type": "thumbs-up-button", "index": message_id},
        variant="gradient",
        gradient={"from": "#004D40", "to": "#2d695e"},
        radius="xl",
        style={
            "margin-right": "1px",
            "margin-left": "1px",
            "margin-top": "5px",
            "width": "40px",
        },
        compact=True,
        n_clicks=0,
    )
    thumbs_down_button = dmc.Button(
        DashIconify(icon="octicon:thumbsdown-16"),
        id={"type": "thumbs-down-button", "index": message_id},
        variant="gradient",
        gradient={"from": "#004D40", "to": "#2d695e"},
        radius="xl",
        style={
            "margin-right": "1px",
            "margin-left": "1px",
            "margin-top": "5px",
            "width": "40px",
        },
        compact=True,
        n_clicks=0,
    )

    return thumbs_up_button, thumbs_down_button
