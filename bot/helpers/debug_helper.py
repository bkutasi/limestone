from typing import Dict, List
from datetime import datetime
import time

from bot.helpers.formatting_helper import TextFormatter


class DebugHelper:
    """
    A helper class for debugging purposes.
    """

    @staticmethod
    def log_time(debug: bool) -> None:
        """
        Logs the current time in the format "dd-mm-yyyy, hh:mm:ss".
        :param debug: A boolean indicating whether to log the time or not.
        """
        if debug:
            timestamp = time.time()
            date_time = datetime.fromtimestamp(timestamp)
            str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
            print(f"[{str_date_time}]", end="")

    @staticmethod
    def log_user_message(
        chat_id: str, message_type: str, message: str, debug: bool
    ) -> None:
        """
        Logs a user's message.
        :param chat_id: The chat ID of the user.
        :param message_type: The type of message sent by the user.
        :param message: The message sent by the user.
        :param debug: A boolean indicating whether to log the message or not.
        """
        if debug:
            DebugHelper.log_time(debug)
            print(f'User ({chat_id}) in {message_type}: "{message}"')

    @staticmethod
    def log_response(
        chat_id: str, message_type: str, response: str, debug: bool
    ) -> None:
        """
        Logs a response sent to a user.
        :param chat_id: The chat ID of the user.
        :param message_type: The type of response sent to the user.
        :param response: The response sent to the user.
        :param debug: A boolean indicating whether to log the response or not.
        """
        if debug:
            DebugHelper.log_time(debug)
            print(f'Sent ({chat_id}) in {message_type}: "{response[1:]}"')

    @staticmethod
    def log_chat_database(
        chat_id: str, chat_responses: Dict[str, List[str]], database_debug: bool
    ) -> None:
        """
        Logs a chat database for a given chat ID.
        :param chat_id: The chat ID of the user.
        :param chat_responses: A dictionary containing chat responses for each chat ID.
        :param database_debug: A boolean indicating whether to log the database or not.
        """
        if database_debug:
            print(chat_responses[chat_id] + "\n\n")

    @staticmethod
    def inspect_code_blocks(
        response_string: str, response_cache: str, codeblock_debug: bool
    ) -> None:
        """
        Inspects code blocks in a given response string and cache.
        :param response_string: The response string to inspect.
        :param response_cache: The cache of previous responses to inspect.
        :param codeblock_debug: A boolean indicating to log the inspection or not.
        """
        if codeblock_debug:
            print(
                response_cache,
                "\t\topen block: ",
                TextFormatter.has_open_code_block(response_string),
                "open inline: ",
                TextFormatter.has_open_inline_code(response_string),
            )
