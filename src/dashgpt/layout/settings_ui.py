# Author: Ty Andrews
# Date: 2023-09-21

import os

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html


def generate_settings_offcanvas(settings_offcanvas_id="settings-offcanvas"):

    settings_offcanvas = dbc.Offcanvas(
        children=[
            html.H6(f"Welcome to DashGPT!"),
            html.Hr(),
            html.H6("EXAMPLE: Edit the System Prompt:"),
            html.P(
                "This doesn't actually edit the system prompt as I ran out of time to connect it up with callbacks, but it does show how to use the settings offcanvas!",
                style={"margin-bottom": "0px"},
            ),
            dmc.Textarea(
                id="system-prompt",
                value="Dummy system prompt",
                minRows=4,
                maxRows=6,
            ),
            html.Hr(),
            # put temperature slider here
            html.H6("EXAMPLE: Edit the Temperature"),
            html.P("Again, out of time to connect it up with callbacks, you get the gist!"),
            dmc.Slider(
                id="temperature-slider",
                value=0.5,
                min=0,
                max=1,
                step=0.01,
                labelAlwaysOn=False,
                color="indigo",
                style={"margin-bottom": "10px"},
                marks = [
                    {"value": 0, "label": "0"},
                    {"value": 0.25, "label": "0.25"},
                    {"value": 0.5, "label": "0.5"},
                    {"value": 0.75, "label": "0.75"},
                    {"value": 1, "label": "1"},
                ]
            ),
        ],
        id=settings_offcanvas_id,
        title="DashGPT Settings",
        is_open=False,
        backdrop=True,
    )

    return settings_offcanvas
