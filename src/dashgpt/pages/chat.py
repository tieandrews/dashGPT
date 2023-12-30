# Author: Ty Andrews
# Date: 2023-09-17
import os

import dash
from dash import (
    html,
    dcc,
    Input,
    Output,
    State,
    clientside_callback,
    ClientsideFunction,
    ctx,
    callback, 
    ALL, 
    MATCH
)
import time
import random
import json
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from flask import request, Response
import uuid
from markdownify import markdownify
from dash_iconify import DashIconify
from dotenv import load_dotenv, find_dotenv


from dashgpt.logs import get_logger
from dashgpt.data.langchain_utils import (
    convert_documents_to_dict,
    convert_dict_to_documents,
)
from dashgpt.chat.chat_utils import (
    stream_send_messages,
    get_relevant_documents,
    connect_to_vectorstore,
    convert_documents_to_chat_context,
    convert_chat_history_to_string,
)
from dashgpt.chat.prompts import (
    generate_user_prompt,
    load_system_prompt,
)
from dashgpt.layout.chat_ui import (
    generate_user_textbox,
    generate_ai_textbox,
    render_response,
    generate_chat_controls,
    generate_related_content_accordion,
)
from dashgpt.layout.feedback_ui import (
    generate_feedback_modal,
    generate_thumbs_up_down_buttons,
)
from dashgpt.layout.settings_ui import generate_settings_offcanvas
from dashgpt.layout.information_ui import generate_information_modal
from dashgpt.chat.sample_questions import (
    generate_sample_questions,
)

load_dotenv(find_dotenv())

logger = get_logger(__name__)

dash.register_page(__name__, path="/")

# get the langchain vecotr store to use for similarity search
vector_store = connect_to_vectorstore()


def layout():
   
    # Define Layout for the chat messages
    conversation = html.Div(
        html.Div(id="chat-history", 
                 children=[
                    html.Div(
                        "Running Vector Store Setup for DashGPT...",
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            # "height": "100%",
                            "font-size": "24px",
                            "font-weight": "bold",
                            "color": "white",  
                        },
                    ),
                    # put in a smaller font sized line saying thins should take no more than 5s
                    html.Div(
                        "This shouldn't take more than 5 seconds.",
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "16px",
                            "color": "white",  
                        },
                    ),
                ]
        ),
        style={
            "overflow-y": "auto",
            "display": "flex",
            "height": "calc(76vh)",  # adjust this to prevent vertical scrolling on main screen/mobile
            "flex-direction": "column-reverse",
            "marginTop": "35px",
        },
    )

    # name="TODO: REMOVE NAME"

    settings_offcanvas = generate_settings_offcanvas(
        settings_offcanvas_id="settings-offcanvas"
    )

    information_modal = generate_information_modal(
        information_modal_id="information-modal"
    )

    layout = dbc.Container(
        [
            # a Div to trigger warmup actions to run on first-load
            html.Div(
                id="dashgpt-first-load",
                children=[],  # don't put anything in here, it's just a trigger
            ),
            # store the current conversation uuid
            dcc.Store(id="conversation-id", data=""),
            # data store for triggering when a new prompt is submitted and ready for generation
            dcc.Store(id="new-prompt", data=""),
            # data store to house the generated response
            dcc.Store(id="last-generated-response", data=""),
            # use a store to access the current-context formatted as a string
            dcc.Store(id="formatted-context", data=""),
            # store the complete context including metadaata
            dcc.Store(id="complete-context", data=""),
            # a store to track the object id of the card that streaming should output text to
            dcc.Store(id="current-streaming-object-id", data=""),
            # spot to store the current ai message id
            dcc.Store(id="current-ai-message-id", data=""),
            # store the history of the conversation
            dcc.Store(id="raw-chat-history", data='{"chat_history": []}'),
            settings_offcanvas,
            information_modal,
            dmc.Button(
                DashIconify(icon="octicon:gear-16"),
                id="settings-button",
                variant="gradient",
                gradient={"from": "#004D40", "to": "#2d695e"},
                radius="xl",
                style={"position": "absolute", "top": "10px", "left": "10px"},
                # compact=True,
            ),
            # put a text object with name in the top left
            html.H4(
                "DashGPT",
                style={
                    "position": "absolute",
                    "top": "15px",
                    "left": "70px",
                    "color": "white",
                    "font-family": "Poppins, sans-serif",
                },
            ),
            dmc.HoverCard(
                withArrow=True,
                width=200,
                shadow="md",
                children=[
                    dmc.HoverCardTarget(
                        # put another button right beside it whish has a plus on it
                        dmc.Button(
                            DashIconify(icon="octicon:plus-16"),
                            id="new-prompt-button",
                            variant="gradient",
                            gradient={"from": "#004D40", "to": "#2d695e"},
                            radius="xl",
                        ),
                    ),
                    dmc.HoverCardDropdown(
                        dmc.Text("Click here to start a new conversation", size="sm")
                    ),
                ],
                style={
                    "position": "absolute",
                    "top": "10px",
                    "right": "70px",
                },
            ),
            # put a button right beside the plus with an i in it for information
            dmc.Button(
                DashIconify(icon="octicon:info-16"),
                id="info-button",
                variant="gradient",
                gradient={"from": "#004D40", "to": "#2d695e"},
                radius="xl",
                style={
                    "position": "absolute",
                    "top": "10px",
                    "right": "10px",
                },
            ),
            dbc.Row(
                [
                    dbc.Col(conversation, width=12, lg=8, className="mx-auto"),
                ],
                className="my-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dcc.Loading(
                                id="loading",
                                type="default",
                                color="#2d695e",  # Change the color to #2d695e
                                children=[
                                    html.Div("", id="dummy-loading-output"),
                                ],
                            )
                        ],
                        id="input-controls-container",
                        width=12,
                        lg=8,
                        className="mx-auto"
                    ),
                ],
                className="my-4",
            ),
        ],
        fluid=True,
        className="px-0",
    )

    return layout


@callback(
    Output("dashgpt-first-load", "children"),
    Output("input-controls-container", "children"),
    Output("chat-history", "children"),
    Output("dummy-loading-output", "children"),
    Input("dashgpt-first-load", "id"),
    State("dashgpt-first-load", "children"),
)
def run_on_first_load(id, children):
    """
    Callback that runs on the first load of the dashgpt page.
    """
    if len(children) == 0:
        start_time = time.time()
        # run a simple retrieval to warm up the vector store connection
        _ = get_relevant_documents(
            user_prompt="Cats",
            vector_store=vector_store,
            k=1,
            method="similarity",
        )
        logger.info(
            f"Vector store connection warmed up, took {time.time() - start_time:.3f} seconds."
        )

        chat_controls = generate_chat_controls(
            text_input_id="text-prompt", submit_button_id="submit-prompt"
        )

        sample_questions = generate_sample_questions()

        return [html.Div(style={"display": "none"})], chat_controls, sample_questions, None
    else:
        raise dash.exceptions.PreventUpdate


# primary callback for on enter pressed, or submit button pressed creates the user message
# and the empty AI response card for text to be streamed into, disables submit button and
# updates the raw chat history
@callback(
    Output("chat-history", "children", allow_duplicate=True),
    Output("new-prompt", "data"),
    Output("text-prompt", "value"),
    Output("submit-prompt", "disabled", allow_duplicate=True),
    Output("current-streaming-object-id", "data"),
    Output("raw-chat-history", "data", allow_duplicate=True),
    Input("submit-prompt", "n_clicks"),
    Input("text-prompt", "value"),
    State("chat-history", "children"),
    State("raw-chat-history", "data"),
    prevent_initial_call=True,
)
def add_chat_card(n_clicks, user_prompt, chat_history, 
                  raw_chat_history
    ):
    if user_prompt is None or user_prompt == "":
        # don't do anything if the user prompt is empty
        raise dash.exceptions.PreventUpdate
    
    # case when only sample question buttons are present, reset
    # if chat_history is a dict, it's the first time the callback is being called
    if (len(chat_history) <= 1) or (chat_history is None) or (isinstance(chat_history, dict)):
        chat_history = []

    raw_chat_dict = json.loads(raw_chat_history)

    raw_chat_dict["chat_history"].append({"role": "user", "content": user_prompt})

    # create the users prompt card
    user_card = generate_user_textbox(user_prompt)

    # generate an object id for the current streaming object with random 4 digits at the end
    # this is used to trigger the streaming_chat callback
    streaming_object_id = f"streaming-object-{random.randint(1000, 9999)}"

    # create the AI response card
    ai_card = generate_ai_textbox(
        streaming_object_id, text="🔬 Searching relevant content..."
    )

    # add the new card to the chat history
    chat_history.append(user_card)
    chat_history.append(ai_card)

    return (
        chat_history,
        user_prompt,
        "",  # clear the input field
        True,  # disable the submit button
        streaming_object_id,
        json.dumps(raw_chat_dict),
    )


# once new-prompt is updated, get the context and update the context objects to prepare
# for chat completions
@callback(
    Output("formatted-context", "data"),
    Output("complete-context", "data"),
    Output("conversation-id", "data", allow_duplicate=True),
    Output("chat-history", "children", allow_duplicate=True),
    Input("new-prompt", "data"),
    State("conversation-id", "data"),
    State("raw-chat-history", "data"),
    State("chat-history", "children"),
    prevent_initial_call=True,
)
# function to get context and update context objects
def update_context(
    user_prompt,
    conversation_id,
    raw_chat_history,
    chat_history_cards,
):
    if user_prompt is None or user_prompt == "":
        # don't do anything if the user prompt is empty
        raise dash.exceptions.PreventUpdate

    chat_history_dict = json.loads(raw_chat_history)

    question_for_retrieval = user_prompt
    logger.debug(f"Original question used for retrieval: {question_for_retrieval}")

    relevant_docs = get_relevant_documents(
        user_prompt=question_for_retrieval,
        vector_store=vector_store,
        k=3,
        method="similarity",
    )

    relevant_docs_dict = convert_documents_to_dict(relevant_docs)

    formatted_context_str = convert_documents_to_chat_context(relevant_docs)

    # change the text in the last card to "Generating answer..."
    last_card = chat_history_cards[-1]
    last_card["props"]["children"][0]["props"]["children"]["props"][
        "children"
    ] = "✨Generating answer..."
    chat_history_cards[-1] = last_card

    return (
        formatted_context_str,
        relevant_docs_dict,
        conversation_id,
        chat_history_cards,
    )


# JS callback to send the question to the flask API, at the end it enables the submit button
# and returns the generated html response so formatting can be maintained
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="streaming_GPT"),
    Output("submit-prompt", "disabled"),
    Output("last-generated-response", "data"),
    Input("formatted-context", "data"),
    State("submit-prompt", "n_clicks"),
    State("new-prompt", "data"),
    State("current-streaming-object-id", "data"),
    State("raw-chat-history", "data"),
    prevent_initial_call=True,
)


# if you are creating a multipage app, you won't be able to import app object because of circular imports
# so unless you create the route in the same file where you define your Dash app
# you can simply use app = dash.get_app() to get the Dash app instance in any other page
app = dash.get_app()


@app.server.route("/streaming-chat", methods=["POST"])
def streaming_chat():
    user_prompt = request.json["prompt"]
    context_str = request.json["formatted_context"]
    chat_history = json.loads(request.json["chat_history"])

    # prompt engineering/data augmentation can be performed here
    # important thing is that this is happening on the backend, so that the users can't tamper with this
    # JS front-end only handles the response, and nothing else
    system_prompt = {
        "role": "system",
        "content": load_system_prompt(),
    }

    chat_completion_prompt = []
    chat_completion_prompt.append(system_prompt)

    # take the chat history and output it into a string llike "user: message\nassistant: message\nuser: message"
    # keep all but the lase message as it is the prompt
    chat_history_str = convert_chat_history_to_string(chat_history)

    user_prompt = generate_user_prompt(
        user_prompt=user_prompt,
        chat_context=context_str,
        chat_history=chat_history_str,
    )

    chat_completion_prompt.append(user_prompt)

    logger.debug(f"chat Prompt: {chat_completion_prompt}")

    def response_stream():
        yield from (
            line.choices[0].delta.get("content", "")
            for line in stream_send_messages(chat_completion_prompt)
        )

    logger.debug("End of streaming_chat function.")

    return Response(response_stream(), mimetype="text/response-stream")


# callback which is triggered when the last-generated-text is updated meaning streaming is done
# it takes the state of conversation-history and updates the last childs text with reformatted text
@callback(
    Output("chat-history", "children", allow_duplicate=True),
    Output("raw-chat-history", "data", allow_duplicate=True),
    Output("current-ai-message-id", "data", allow_duplicate=True),
    Input("last-generated-response", "data"),
    State("chat-history", "children"),
    State("complete-context", "data"),
    State("raw-chat-history", "data"),
    State("conversation-id", "data"),
    State("current-ai-message-id", "data"),
    prevent_initial_call=True,
)
def format_chat_history(
    last_generated_response,
    chat_history,
    complete_context_dict,
    raw_chat_history,
    conversation_id,
    current_ai_message_id,
):
    raw_chat_dict = json.loads(raw_chat_history)

    if chat_history is None:
        chat_history = []

    # if the last generated response is empty, don't do anything
    if last_generated_response is None or last_generated_response == "":
        logger.debug("Preventing format_chat_history callback from being called.")
        raise dash.exceptions.PreventUpdate

    # convert complete_context to a list of Document objects
    complete_context_docs = convert_dict_to_documents(complete_context_dict)

    style = {
        "max-width": "80%",
        "width": "max-content",
        "padding": "0px 0px",
        "border-radius": 25,
        "margin-bottom": 20,
        "margin-left": 0,
        "margin-right": "auto",
    }

    # convert the html to markdown, without this the returned raw text loses it's
    # formatting/bullet points etc.
    last_generated_response_md = markdownify(last_generated_response)

    message_id = str(uuid.uuid4())

    # ------------ FORMAT THE RESPONSE CARD ------------ #
    raw_chat_dict["chat_history"].append(
        {"role": "assistant", "content": last_generated_response_md}
    )

    # take the last generated response apply custom rendering
    card_children = [
        html.Div(render_response(last_generated_response_md.replace("* ", "• "))),
    ]

    # --------------- ADD RELATED CONTENT --------------- #
    related_source_accordion = generate_related_content_accordion(
        complete_context_docs,
        id="related-source-accordion",
    )

    card_children.append(related_source_accordion)

    # --------------- ADD FEEDBACK BUTTONS --------------- #
    feedback_modal = generate_feedback_modal(message_id=message_id)
    thumbs_up_button, thumbs_down_button = generate_thumbs_up_down_buttons(
        message_id=message_id,
    )

    # put the thumbsup/down buttons on the right hand edge of the card and the card on the right
    card_children.append(
        html.Div(
            [
                html.Div(),
                html.Div(
                    [thumbs_up_button, thumbs_down_button, feedback_modal],
                    style={"display": "flex", "flex-wrap": "nowrap"},
                ),
            ],
            style={
                "display": "flex",
                "justify-content": "space-between",
                "align-items": "center",
            },
        )
    )

    # create a new dbc.Card to replace the one streamed to
    card = dbc.Card(
        card_children,
        style=style,
        body=True,
        color="#ceeae5",
        inverse=False,
    )

    # replace the streamed to card with the new card
    chat_history[-1] = html.Div(
        [
            card,
        ]
    )

    return chat_history, json.dumps(raw_chat_dict), message_id


# a call back that takes settings-button as input and outputs is_open to settings-backdrop offcanvas
@callback(
    Output("settings-offcanvas", "is_open", allow_duplicate=True),
    Input("settings-button", "n_clicks"),
    State("settings-offcanvas", "is_open"),
    prevent_initial_call=True,
)
def toggle_settings_offcanvas(n, is_open):
    if n:
        return not is_open
    return is_open


# cllback to reset the conversation history
@callback(
    Output("chat-history", "children", allow_duplicate=True),
    Output("conversation-id", "data", allow_duplicate=True),
    Output("raw-chat-history", "data", allow_duplicate=True),
    Input("new-prompt-button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_chat_history(
    n_clicks, 
    ):
    if n_clicks:
        new_conversation_id = str(uuid.uuid4())
        logger.debug("New conversation id: " + new_conversation_id)
        # generate a sample quesiton button and put as children
        sample_questions = generate_sample_questions()
        return [sample_questions], new_conversation_id , '{"chat_history": []}'
    raise dash.exceptions.PreventUpdate


@callback(
    [
        Output(
            {"type": "thumbs-up-button", "index": MATCH},
            "gradient",
            allow_duplicate=True,
        ),
        Output(
            {"type": "thumbs-down-button", "index": MATCH},
            "gradient",
            allow_duplicate=True,
        ),
    ],
    [Input({"type": "thumbs-up-button", "index": MATCH}, "n_clicks")],
    [
        State({"type": "thumbs-up-button", "index": MATCH}, "id"),
    ],
    prevent_initial_call=True,
)
def thumbs_up(n_clicks, current_message_id
    ):
    if n_clicks:
        message_id = current_message_id["index"]
        logger.debug(
            f"Thumbs up button clicked for message {message_id}, do something with this..."
        )
        return {"from": "green", "to": "green"}, {"from": "grey", "to": "grey"}
    raise dash.exceptions.PreventUpdate


# on thumbsdown button press pop up a modal for getting feedback
@callback(
    [
        Output(
            {"type": "feedback-modal", "index": MATCH}, "opened", allow_duplicate=True
        ),
        Output(
            {"type": "thumbs-down-button", "index": MATCH},
            "gradient",
            allow_duplicate=True,
        ),
        Output(
            {"type": "thumbs-up-button", "index": MATCH},
            "gradient",
            allow_duplicate=True,
        ),
        Output({"type": "thumbs-down-button", "index": MATCH}, "n_clicks"),
    ],
    [
        Input({"type": "thumbs-down-button", "index": MATCH}, "n_clicks"),
    ],
    [State({"type": "feedback-modal", "index": MATCH}, "opened")],
    prevent_initial_call=True,
)
def thumbs_down(n_clicks, is_open):
    if n_clicks > 0:
        return (
            not is_open,
            {"from": "red", "to": "#dc143c"},
            {"from": "grey", "to": "grey"},
            0,
        )
    raise dash.exceptions.PreventUpdate


# callback for when the feedback submit button is pressed, closes the feedback modal
# and report the feedback to the backend
@app.callback(
    Output({"type": "feedback-modal", "index": MATCH}, "opened", allow_duplicate=True),
    Input({"type": "feedback-submit-button", "index": MATCH}, "n_clicks"),
    State({"type": "feedback-modal", "index": MATCH}, "opened"),
    State({"type": "feedback-modal", "index": MATCH}, "id"),
    State({"type": "feedback-text-area", "index": MATCH}, "value"),
    State({"type": "feedback-type", "index": MATCH}, "value"),
    prevent_initial_call=True,
)
def submit_feedback(
    n_clicks, is_open, current_message_index,
    feedback_text, feedback_type
):
    logger.debug(f"Feedback type: {feedback_type}")
    message_id = current_message_index["index"]
    if n_clicks:
        # ensure they provided feedback type
        if feedback_type is None or feedback_type == "":
            logger.debug("Feedback type not provided, preventing callback")
            raise dash.exceptions.PreventUpdate
        logger.debug("Negative feedback submit button clicked, do something with this...")
        return not is_open
    raise dash.exceptions.PreventUpdate

# callback to open/close the information-modal on info-button click
@app.callback(
    Output("information-modal", "opened"),
    Input("info-button", "n_clicks"),
    State("information-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_information_modal(n_clicks, is_open):
    if n_clicks:
        return not is_open
    raise dash.exceptions.PreventUpdate


@app.callback(
    Output("text-prompt", "value", allow_duplicate=True),
    Input({"type": "sample-question-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def update_text_prompt(n_clicks):
    if any(n_clicks):
        pressed_button = ctx.triggered_id
        sample_question = pressed_button["index"]

        logger.info(f"Sample question button clicked, question: {sample_question}")

        # Return the sample question text to set the value of the text-prompt element
        return sample_question
    else:
        raise dash.exceptions.PreventUpdate
