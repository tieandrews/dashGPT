# Author: Ty Andrews
# Date: 2023-09-17
import os

from langchain.schema import Document
import tiktoken


def convert_documents_to_dict(relevant_documents):
    """
    Convert a list of relevant documents to a list of dictionaries.

    Parameters
    ----------
    relevant_documents : list of Document objects
        The list of relevant documents to convert.

    Returns
    -------
    list of dict
        The list of dictionaries containing the page content and metadata of each document.
    """
    docs_dict = [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in relevant_documents
    ]

    return docs_dict


def convert_dict_to_documents(docs_dict):
    """
    Convert a list of dictionaries to a list of Document objects.

    Parameters
    ----------
    docs_dict : list of dict
        The list of dictionaries to convert.

    Returns
    -------
    list of Document objects
        The list of Document objects created from the dictionaries.
    """
    # take the dictionary of documents and convert them to Document objects
    docs = [Document(**doc) for doc in docs_dict]

    return docs


def count_tokens(text, model="gpt-3.5-turbo"):
    # Define the tokenizer for the specific model
    if model == "gpt-3.5-turbo":
        tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    else:
        raise ValueError("Unsupported model: " + model)

    # Tokenize the input text
    tokens = tokenizer.encode(text)

    # Count the number of tokens
    token_count = len(tokens)

    return token_count