# Author: Ty Andrews
# Date: 2023-10-15

import random
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from dashgpt.logs import get_logger

logger = get_logger(__name__)

SAMPLE_QUESTIONS = [
    {
        "question_start": "Tell me a one liner joke about ",
        "question_end": [
            "dogs",
            "cats",
            "dinosaurs",
            "aliens",
            "artificial intelligence"
        ],
    },
    {
        "question_start": "Tell me a joke about ",
        "question_end": [
            "dogs",
            "cats",
            "dinosaurs",
            "aliens",
            "artificial intelligence"
        ],
    }
]


def get_random_sample_question():
    """
    Randomly picks a sample question from the list of sample questions.

    Returns
    -------
    tuple
        A tuple containing the question start and question end.
    """
    sample_question = random.choice(SAMPLE_QUESTIONS)
    question_start = sample_question["question_start"]
    question_end = random.choice(sample_question["question_end"])

    return question_start, question_end


def generate_sample_question_button():
    """
    Generates a sample question button.

    Returns
    -------
    dmc.Button
        A sample question button.
    """
    question_start, question_end = get_random_sample_question()

    sample_question_button = dmc.Button(
        children=[
            html.Div(
                children=[
                    html.Strong(question_start),
                    html.Br(),
                    question_end,
                ],
                style={"display": "flex", "flex-direction": "column"},
            )
        ],
        id={"type": "sample-question-button", "index": question_start + question_end},
        variant="gradient",
        leftIcon=DashIconify(icon="pajamas:question", width=30),
        gradient={"from": "#004D40", "to": "#2d695e"},
        radius="lg",
        style={
            "margin-right": "10px",
            "margin-left": "10px",
            "margin-top": "2px",
            "margin-bottom": "2px",
            "height": "55px",
            "display": "flex",
            "align-items": "flex-start",
        },
        fullWidth=True,
    )

    return sample_question_button


def generate_sample_questions():
    # Generate 4 sample questions and put them in the sample questions col
    sample_question_button_1 = generate_sample_question_button()
    sample_question_button_2 = generate_sample_question_button()
    # check that the questions are different and regenerate if they are the same
    while sample_question_button_1.id == sample_question_button_2.id:
        sample_question_button_2 = generate_sample_question_button()

    sample_questions = dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(
                        sample_question_button_1,
                        width=12,
                        lg=6,
                        className="mx-auto",
                        style={"padding": "2px"},
                    ),
                    dbc.Col(
                        sample_question_button_2,
                        width=12,
                        lg=6,
                        className="mx-auto",
                        style={"padding": "2px"},
                    ),
                ],
                style={"margin-bottom": "2px"},
            ),
        ],
        style={
            "width": "95%",
            "padding": "5px",
        },
    )

    return sample_questions
