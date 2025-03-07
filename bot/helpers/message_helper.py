from telegram import Update, Message
from typing import Tuple


class MessageHelper:
    """
    A helper class for sending basic messages and actions in a chat.
    """

    @staticmethod
    async def send_placeholder_message(update: Update) -> Message:
        """
        Sends a placeholder message to the chat.

        :param update: The update object containing the message.
        :return: The sent placeholder message object.
        """
        placeholder_message = await update.message.reply_text("...")
        return placeholder_message

    @staticmethod
    async def send_typing_action(update: Update) -> None:
        """
        Sends a typing action to the chat.

        :param update: The update object containing the message.
        """
        await update.message.chat.send_action(action="typing")

    @staticmethod
    def get_message_info(update: Update) -> Tuple[str, int, str]:
        """
        Gets the message type, chat ID, and message text from an update object.

        :param update: The update object containing the message.
        :return: A tuple containing the message type, chat ID, and message text.
        """
        message_type = update.message.chat.type
        chat_id = update.message.chat.id
        message = update.message.text or ""
        return message_type, chat_id, message
