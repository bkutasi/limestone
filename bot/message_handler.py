from typing import AsyncGenerator, Generator, Tuple
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


class MyMessageHandler:
    def __init__(
        self,
        instruction_templates: Dict[str, str],
        BOT_USERNAME: str,
        DEV_ID: int,
        debug: bool = False,
        database_debug: bool = False,
        codeblock_debug: bool = False,
        stream_generator: Stream = None,
    ):
        self.debug = debug
        self.DEV_ID = DEV_ID
        self.database_debug = database_debug
        self.codeblock_debug = codeblock_debug
        self.stream_generator = stream_generator
        self.instruction_templates = instruction_templates
        self.BOT_USERNAME = BOT_USERNAME

        # Initialized variables that are not passed as arguments
        self.chat_responses: Dict[int, str] = {}
        self.logger = logging.getLogger(__name__)

    def get_dev_id(self):
        return self.DEV_ID

    def get_logger(self):
        return self.logger

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Send placeholder message while waiting for the response
        last_message = await MessageHelper.send_placeholder_message(update)

        # Send a typing action while waiting for the response
        await MessageHelper.send_typing_action(update)

        # Get basic info of the incoming message
        message_type, chat_id, message = MessageHelper.get_message_info(update)

        # Print a log for debugging if debugging is enabled
        DebugHelper.log_user_message(chat_id, message_type, message, self.debug)

        # Save the responses to the database
        prompt, convo = self.save_responses(chat_id, message)

        # Make a generator for the response
        response_generator: AsyncGenerator or Generator = self.stream_text(prompt)

        # Make a string placeholder for the final response
        response_string: str = ""
        response_cache: str = ""

        # saving the time of the last update which is now for the first iteration
        last_update_time: float = time.time()

        # Iterate through the generator and send the response
        async for response in response_generator:
            response_cache: str = ""
            # If the response is a string, add it to the cache
            response_cache += response # if isinstance(response, str) else ""

            # Cache the response
            response_string += response_cache

            # If not enought time elapsed, continue caching
            if time.time() - last_update_time > 0.5:
                last_message = await self._edit_response_text(
                    context, response_string, last_message
                )

                # Update the last update time
                last_update_time = time.time()

        """# if there is still something in the cache, send it
        if len(response_cache) > 0:
            response_string += response_cache
            print(response_cache)
            await self._edit_response_text(
                context, response_string, placeholder_message
            )
        else:
            print("no cache")"""

        # edit the message is response string is not identical to the already sent message
        # by getting the last message sent by the bot

        if last_message.text != response_string:
            await self._edit_response_text(
                context, response_string, last_message
            )
       
        DebugHelper.log_response(chat_id, message_type, response_string, self.debug)

        # First check if the chat_id is already in the database, and save the response
        self.update_chat_responses(chat_id, convo + response_string)

        # Print the database to the console for debugging if enabled
        DebugHelper.log_chat_database(chat_id, self.chat_responses, self.database_debug)

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

    def save_responses(self, chat_id: int, message: str) -> Tuple[str, str]:
        message = message.replace(self.BOT_USERNAME, "", 1).lstrip()
        instruction = self.instruction_templates["vicunav1_1"]["instruction"]
        response = self.instruction_templates["vicunav1_1"]["response"]

        if chat_id not in self.chat_responses:
            prompt_start = self.instruction_templates["vicunav1_1"]["prompt_start"]
            prompt = convo = prompt_start + instruction + message + response
        else:
            chat_response = self.chat_responses[chat_id][-8192:]
            prompt = chat_response + instruction + message + response
            convo = instruction + message + response
        return prompt, convo

    def update_chat_responses(self, chat_id, response_string):
        self.chat_responses[chat_id] = (
            self.chat_responses.setdefault(chat_id, "") + response_string
        )

    async def stream_text(self, prompt: str):
        async for token in self.stream_generator.generate(prompt):
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
    def __init__(self, backend: str, uri: str, max_new_tokens: int):
        self.backend = backend
        self.uri = uri
        self.max_new_tokens = max_new_tokens

    async def generate(self, prompt: str):
        stream = Stream(self.backend, self.uri, self.max_new_tokens)

        if self.backend == "ooba":
            async for token in stream.ooba(prompt):
                yield token

        elif self.backend == "exllama":
            for token in stream.exllama(prompt):
                yield token
