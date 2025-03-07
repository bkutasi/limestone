from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from telegram.constants import (
    ParseMode,
)

from .helpers.formatting_helper import TextFormatter
from .message_handler import MyMessageHandler

import logging

logger = logging.getLogger(__name__)


class Commands:
    """
    A class used to handle commands in a chat application.

    Methods
    -------
    start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None
        Handles the /start command.

    help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None
        Handles the /help command.

    custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None
        Handles the /custom command.

    wipe_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None
        Handles the /wipe command.
    """

    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /start command.

        Parameters
        ----------
        update : Update
            The update object containing the message.
        context : ContextTypes.DEFAULT_TYPE
            The context object.
        """
        if update.message:
            text = "You have pressed the `/start` command."
            logger.debug(
                f"Start command output: text={text}, has_code_block={TextFormatter.has_open_code_block(text)}, has_inline_code={TextFormatter.has_open_inline_code(text)}"
            )
            await update.message.reply_text(
                TextFormatter.escape(text), parse_mode=ParseMode.MARKDOWN_V2
            )

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles the /help command.

        Parameters
        ----------
        update : Update
            The update object containing the message.
        context : ContextTypes.DEFAULT_TYPE
            The context object.
        """
        if update.message:
            await update.message.reply_text(
                text=f"Your chat id is <code>{update.message.chat.id}</code>",
                parse_mode=ParseMode.HTML,
            )

    @staticmethod
    async def custom_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles the /custom command.

        Parameters
        ----------
        update : Update
            The update object containing the message.
        context : ContextTypes.DEFAULT_TYPE
            The context object.
        """
        if update.message:
            await update.message.reply_text(
                "This is a custom command, you can add whatever text you want here."
            )

    @staticmethod
    async def wipe_history_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message_handling: MyMessageHandler,
    ) -> None:
        """
        Handles the /wipe command.

        Parameters
        ----------
        update : Update
            The update object containing the message.
        context : ContextTypes.DEFAULT_TYPE
            The context object.
        """
        # Get the user ID
        user_id = update.message.chat.id

        # Check if the user has chat history
        if user_id in message_handling.conversation_memory:
            # Delete the user's chat history
            del message_handling.conversation_memory[user_id]
            logger.info("Chat history wiped.")
            await update.message.reply_text("Your chat history has been wiped.")
        else:
            await update.message.reply_text("You have no chat history to wipe.")
