from typing import AsyncGenerator, Generator, Tuple, List
import time
import logging
from typing import Dict
from telegram import Update, Message
from telegram.ext import (
    ContextTypes,
)

from telegram.constants import (
    ParseMode,
)

from .helpers.formatting_helper import TextFormatter
from .streamer import Stream
from .helpers.debug_helper import DebugHelper
from .helpers.message_helper import MessageHelper
from .helpers.prompt_helper import PromptHelper


class MyMessageHandler:
    def __init__(
        self,
        template: Dict,
        instruction_templates: Dict[str, str],
        BOT_USERNAME: str,
        DEV_ID: int,
        debug: bool = False,
        database_debug: bool = False,
        codeblock_debug: bool = False,
        stream_generator: Stream = None,
        streaming: bool = False,
    ):
        self.template = template
        self.debug = debug
        self.DEV_ID = DEV_ID
        self.database_debug = database_debug
        self.codeblock_debug = codeblock_debug
        self.stream_generator = stream_generator
        self.instruction_templates = instruction_templates
        self.streaming = streaming
        self.BOT_USERNAME = BOT_USERNAME

        # Initialized variables that are not passed as arguments
        self.conversation_memory: Dict[int, List[Dict[str, str]]] = {}
        self.logger = logging.getLogger(__name__)

    def get_dev_id(self):
        return self.DEV_ID

    def get_logger(self):
        return self.logger

    async def handle_static_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        # DEPRECATED. DO NOT USE
        # Send a typing action while waiting for the response
        await MessageHelper.send_typing_action(update)

        # Get basic info of the incoming message
        message_type, chat_id, message = MessageHelper.get_message_info(update)

        # Print a log for debugging if debugging is enabled
        DebugHelper.log_user_message(chat_id, message_type, message, self.debug)

        # Save the responses to the database
        prompt = self.save_responses(chat_id, message)

        # Make a generator for the response
        response_generator: AsyncGenerator or Generator = self.stream_text(prompt)

        # Iterate through the generator and send the response
        response_string: str = response_generator

        DebugHelper.log_response(chat_id, message_type, response_string, self.debug)

        # First check if the chat_id is already in the database, and save the response
        self.update_conversation_memory(chat_id, response_string)

        # Print the database to the console for debugging if enabled
        DebugHelper.log_chat_database(
            chat_id, self.conversation_memory, self.database_debug
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Send placeholder message while waiting for the response
        last_message = await MessageHelper.send_placeholder_message(update)

        # Send a typing action while waiting for the response
        await MessageHelper.send_typing_action(update)

        # Get basic info of the incoming message
        message_type, chat_id, message = MessageHelper.get_message_info(update)

        # Print a log for debugging if debugging is enabled
        DebugHelper.log_user_message(chat_id, message_type, message, self.debug)

        # Save the user's message to the database
        # self.save_responses(chat_id, message)

        self.update_conversation_memory(chat_id, message=message)

        prompt = await PromptHelper.generate_prompt(
            template_name="llama3-instruct",
            user_input=message,
            templates=self.instruction_templates,  # Assuming templates are loaded in the class
            conversation_memory=self.conversation_memory,
            chat_id=chat_id,
        )

        # Make a generator for the response
        response_generator: AsyncGenerator or Generator = self.stream_text(prompt)

        # Make a string placeholder for the final response
        response_string: str = ""
        response_cache: str = ""

        # saving the time of the last update which is now for the first iteration
        last_update_time: float = time.time()

        # Iterate through the generator and send the response
        async for response in response_generator:
            if not self.streaming:
                response_string = response
                await self._edit_response_text(context, response_string, last_message)
            else:
                response_cache: str = ""
                # If the response is a string, add it to the cache
                response_cache += response  # if isinstance(response, str) else ""

                # Cache the response
                response_string += response_cache

                # If not enough time elapsed, continue caching
                if time.time() - last_update_time > 0.5:
                    # the _edit_response_text alters the place holder message with the real output
                    last_message = await self._edit_response_text(
                        context, response_string, last_message
                    )

                    # Update the last update time
                    last_update_time = time.time()

        # edit the message if its not identical to the already sent message
        if last_message.text != response_string and self.streaming:
            await self._edit_response_text(context, response_string, last_message)

        DebugHelper.log_response(chat_id, message_type, response_string, self.debug)

        # First check if the chat_id is already in the database, and save the response
        self.update_conversation_memory(chat_id, response_string=response_string)

        # Print the database to the console for debugging if enabled
        DebugHelper.log_chat_database(
            chat_id, self.conversation_memory, self.database_debug
        )

    async def _edit_response_text(
        self, context: str, response_string: str, placeholder_message
    ) -> Message:
        if TextFormatter.has_open_code_block(response_string):
            text = TextFormatter.escape(response_string) + "```"
        elif TextFormatter.has_open_inline_code(response_string):
            text = TextFormatter.escape(response_string) + "`"
        else:
            text = TextFormatter.escape(response_string)

        return await context.bot.edit_message_text(
            text,
            chat_id=placeholder_message.chat_id,
            message_id=placeholder_message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    async def send_placeholder_message(self, update):
        placeholder_message = await update.message.reply_text("...")
        return placeholder_message

    async def send_typing_action(self, update):
        await update.message.chat.send_action(action="typing")

    def get_message_info(self, update):
        message_type = update.message.chat.type
        chat_id = update.message.chat.id
        message = update.message.text or ""
        return message_type, chat_id, message

    def save_responses(self, chat_id: int, message: str) -> List[Dict[str, str]]:
        """
        Save the user's message to conversation_memory and return the conversation memory.

        Args:
            chat_id (int): The unique chat ID.
            message (str): The user's current message.

        Returns:
            str: The constructed prompt to be sent to the model.
            List[Dict[str, str]]: The conversation memory for the given chat.
        """
        # Get previous conversation history for the chat_id, or initialize it if not present
        conversation_memory = self.conversation_memory.get(chat_id, [])

        # Save the user's message as part of the conversation
        conversation_memory.append(
            {
                "input": f"{message}",
                "output": "",
            }
        )

        # Update conversation_memory for this chat_id
        self.conversation_memory[chat_id] = conversation_memory

    def update_conversation_memory(
        self,
        chat_id: int,
        message: str = None,
        prompt: str = None,
        response_string: str = None,
    ) -> List[Dict[str, str]]:
        """
        Manage the conversation memory by saving a user's message and/or updating with the assistant's response.

        Args:
            chat_id (int): The unique chat ID.
            message (str, optional): The user's current message to be saved. Defaults to None.
            response_string (str, optional): The assistant's response to the user's input. Defaults to None.

        Returns:
            List[Dict[str, str]]: The updated conversation memory for the given chat.
        """
        # Get the previous conversation history for the chat_id, or initialize it if not present
        conversation_memory = self.conversation_memory.get(chat_id, [])

        # keeping the memory implementation since its not needed ATM

        # Save the user's message, if provided
        if message:
            conversation_memory.append(
                {
                    "input": message,
                    "output": "",  # Placeholder for the assistant's response
                }
            )

        # Update the assistant's response, if provided
        if response_string:
            if conversation_memory:
                # Update the 'output' field of the most recent message
                conversation_memory[-1]["output"] = response_string
            else:
                # If no previous message exists, create a new entry with just the response
                conversation_memory.append({"input": "", "output": response_string})

        # Update conversation memory for this chat_id
        self.conversation_memory[chat_id] = conversation_memory

        return conversation_memory

    async def stream_text(self, prompt: str):
        async for token in self.stream_generator.generate_stream(prompt):
            yield token

    async def handle_edited_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        chat_id = update.edited_message.chat.id
        edited_message = update.edited_message.text.replace(
            self.BOT_USERNAME, ""
        ).strip()
        if self.debug:
            print(f'User {chat_id} in an edited message: "{edited_message}"')
        await update.edited_message.reply_text(
            "Message edited, currently I dont support this feature."
        )


class StreamGenerator:
    def __init__(self, backend: str, uri: str, max_new_tokens: int, streaming: bool):
        self.backend = backend
        self.uri = uri
        self.max_new_tokens = max_new_tokens
        self.streaming = streaming

    async def generate_stream(self, prompt: str):
        stream = Stream(self.backend, self.uri, self.max_new_tokens, self.streaming)

        if self.backend == "ooba":
            async for token in stream.ooba(prompt):
                yield token

        if self.backend == "aphrodite":
            for token in stream.aphrodite(prompt):
                yield token

        elif self.backend == "sglang":
            for token in stream.sglang(prompt):
                yield token

        elif self.backend == "exllama":
            for token in stream.exllama(prompt):
                yield token
