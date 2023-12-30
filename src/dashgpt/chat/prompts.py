# Author: Ty Andrews
# Date: 2023-09-28

import os

from dotenv import load_dotenv, find_dotenv

from dashgpt.logs import get_logger

load_dotenv(find_dotenv())

logger = get_logger(__name__)

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
QUESTION_AUG_PROMPT = os.getenv("QUESTION_AUG_PROMPT")


def generate_user_prompt(user_prompt: str, chat_context: str, chat_history: str):
    """
    Generate a user prompt string from the user prompt, chat context, and chat history.

    Parameters
    ----------
    user_prompt : str
        The user prompt to generate the user prompt string from.
    chat_context : str
        The chat context to generate the user prompt string from.
    chat_history : str
        The chat history to generate the user prompt string from.

    Returns
    -------
    str
        The generated user prompt string.
    """

    # check each of 3 components are strings
    if not isinstance(user_prompt, str):
        raise TypeError("User prompt must be a string.")
    if not isinstance(chat_context, str):
        raise TypeError("Chat context must be a string.")
    if not isinstance(chat_history, str):
        raise TypeError("Chat history must be a string.")

    # if the user prompt is empty raise an error
    if user_prompt.strip() == "":
        raise ValueError("User prompt cannot be empty.")

    openai_user_prompt = {
        "role": "user",
        "content": f"""

        Conversation History:
        {chat_history}

        Here's context you can use to answer, don't forget to consider the conversation history in your answer:
        {chat_context}

        Question: {user_prompt}
        """,
    }

    return openai_user_prompt


def load_system_prompt(version=None):
    """
    Load the system prompt from a file located in the prompts/system folder.

    Parameters
    ----------
    prompt_name : str
        The name of the system prompt to load.

    Returns
    -------
    str
        The loaded system prompt.
    """

    if version is None:
        version = SYSTEM_PROMPT

    logger.debug(f"Loading system prompt: {version}")

    # Construct the file path using os.path.join
    file_path = os.path.join("prompts", "system", f"{version}.txt")

    # Load the system prompt from the file
    with open(file_path, "r") as f:
        system_prompt = f.read()

    return system_prompt