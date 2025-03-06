from typing import AsyncGenerator, Optional, List
import time
import logging
import openai
import datetime
from typing import Dict
from telegram import Update, Message

logger = logging.getLogger(__name__)

from telegram.ext import (
    ContextTypes,
)

from telegram.constants import (
    ParseMode,
)

from .helpers.formatting_helper import TextFormatter
from .streamer import Stream
from .helpers.message_helper import MessageHelper


class MyMessageHandler:
    def __init__(
        self,
        template: Dict,
        instruction_templates: Dict[str, str],
        BOT_USERNAME: str,
        DEV_ID: int,
        MODEL: str,
        URI: str,
        stream_generator: Stream = None,
        streaming: bool = False,
        api_key: Optional[str] = "0",
    ):
        self.template = template
        self.DEV_ID = DEV_ID
        self.stream_generator = stream_generator
        self.instruction_templates = instruction_templates
        self.streaming = streaming
        self.BOT_USERNAME = BOT_USERNAME
        self.MODEL = MODEL
        self.URI = URI

        # Initialize OpanAI compatible client
        self.client = openai.OpenAI(base_url=URI, api_key=api_key)

        # Memory: each int is a userID which contains a list of dicts
        self.conversation_memory: Dict[int, List[Dict[str, str]]] = {}

        self.logger = logging.getLogger(__name__)

    def update_client_settings(self, uri: str, model: str):
        """Update API client with new settings"""
        self.URI = uri
        self.MODEL = model
        self.client = openai.OpenAI(base_url=uri, api_key="0")  # Reinitialize client

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Send placeholder message while waiting for the response
        last_message = await MessageHelper.send_placeholder_message(update)

        # Send a typing action while waiting for the response
        await MessageHelper.send_typing_action(update)

        # Get basic info of the incoming message
        message_type, chat_id, message = MessageHelper.get_message_info(update)

        # Print a log for debugging if debugging is enabled
        logger.debug(f'User ({chat_id}) in {message_type}: "{message}"')

        self.update_conversation_memory(chat_id, message=message)

        response_generator = self.client.chat.completions.create(
            model=self.MODEL,
            messages=self.conversation_memory[chat_id]["messages"],
            stream=True,
        )

        # Make a generator for the response
        # response_generator: AsyncGenerator = self.stream_text(messages)

        # Make a string placeholder for the final response
        response_string: str = ""
        response_cache: str = ""

        # saving the time of the last update which is now for the first iteration
        last_update_time: float = time.time()

        # Iterate through the generator and send the response
        for chunk in response_generator:
            response = chunk.choices[0].delta.content or ""
            if not self.streaming:
                response_string = response
                await self._edit_response_text(context, response_string, last_message)
            else:
                response_cache: str = ""
                # If the response is a string, add it to the cache
                response_cache += (
                    response if response is not None else ""
                )  # if isinstance(response, str) else ""

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

                logger.debug(
                    f"Response Cache: {response_cache}, Open Block: {TextFormatter.has_open_code_block(response_string)}, Open Inline: {TextFormatter.has_open_inline_code(response_string)}"
                )

        # edit the message if its not identical to the already sent message
        if last_message.text != response_string and self.streaming:
            await self._edit_response_text(context, response_string, last_message)

        logger.debug(f'Sent ({chat_id}) in {message_type}: "{response_string}"')

        # First check if the chat_id is already in the database, and save the response
        self.update_conversation_memory(chat_id, response_string=response_string)

        # Print the database to the console for debugging if enabled
        logger.debug(self.conversation_memory[chat_id])

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

    def update_conversation_memory(
        self,
        chat_id: int,
        message: str = None,
        response_string: str = None,
    ) -> None:
        """
        Manage the conversation memory by saving a user's message and/or updating with the assistant's response.

        Args:
            chat_id (int): The unique chat ID.
            message (str, optional): The user's current message to be saved. Defaults to None.
            response_string (str, optional): The assistant's response to the user's input. Defaults to None.
        """
        # Initialize conversation memory for this chat_id if it doesn't exist
        if chat_id not in self.conversation_memory:

            template_data = self.instruction_templates.get(self.template)
            if not template_data:
                raise ValueError(f"Template '{self.template}' not found.")

            # Extract the system prompt and prompt template from the template data
            system_prompt = template_data["system_prompt"]
            
            self.conversation_memory[chat_id] = {
                "messages": [{"role": "system", "content": system_prompt}],
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "model": self.MODEL,
                    "endpoint": self.URI,
                    "chat_id": chat_id,
                },
            }

        messages = self.conversation_memory[chat_id]["messages"]

        # Add user message (always append as a new entry)
        if message is not None:
            messages.append({"role": "user", "content": message})

        # Handle assistant response (append new or update last entry for streaming)
        if response_string is not None:
            if messages and messages[-1]["role"] == "assistant":
                # Update existing assistant message (streaming use case)
                messages[-1]["content"] = response_string
            else:
                # Append new assistant message after user input
                messages.append({"role": "assistant", "content": response_string})

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
            self.logger.debug(
                f'User {chat_id} in an edited message: "{edited_message}"'
            )
        await update.edited_message.reply_text(
            "Message edited, currently I dont support this feature."
        )


class StreamGenerator:
    def __init__(
        self, backend: str, uri: str, max_new_tokens: int, model: str, streaming: bool
    ):
        self.backend = backend
        self.uri = uri
        self.model = model
        self.max_new_tokens = max_new_tokens
        self.streaming = streaming

    async def generate_stream(self, prompt: str):
        stream = Stream(
            self.backend, self.uri, self.max_new_tokens, self.model, self.streaming
        )

        if self.backend == "openai":
            for token in stream.openai(prompt):
                yield token
