import json
import sys
import websockets
import requests
import logging
from functools import wraps
from typing import Final
from telegram import Update, helpers
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction

import credentials
import mdconvert

print('Starting up bot...')

TOKEN: Final = credentials.TOKEN
BOT_USERNAME: Final = credentials.BOT_USERNAME
API_URL: Final = credentials.API_URL
HOST: Final = credentials.HOST
URI: Final = credentials.URI
chat_responses = {} # initialize the dictionary for chat responses
debug = False # set to True to enable debugging
database_debug = False
codeblock_debug = False

# Declaration of the instruction style
instruction_base = { "Alpaca" : 
                        [
                        "Below is an instruction that describes a task. Write a response that appropriately completes the request.", 
                        "\n### Instruction:\n",
                        "\n### Response:\n"
                        ],
                    "VicunaV2" : []}

# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        text = """```bash this is a bash codeblock``` you have pressed the `/start` command. You can now type anything and I will do my best to respond!"""
        print(mdconvert.escape(text),"\n", mdconvert.has_open_code_block(text), "\n", mdconvert.has_open_inline_code(text))
        await update.message.reply_text(mdconvert.escape(text), parse_mode=ParseMode.MARKDOWN_V2)


# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text('Try typing anything and I will do my best to respond!')


# Lets us use the /custom command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text('This is a custom command, you can add whatever text you want here.')

# Let use use the retry command

# Lets us use the /wipe command
async def wipe_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is None
    if update.message:
        # Get the user ID
        user_id = update.message.chat.id

        # Check if the user has chat history
        if user_id in chat_responses:
            # Delete the user's chat history
            del chat_responses[user_id]
            print('\nChat history wiped.\n')
            await update.message.reply_text('Your chat history has been wiped.')
        else:
            await update.message.reply_text('You have no chat history to wipe.')

def handle_response(text: str) -> str:
    # Create your own response logic
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I\'m good!'

    if 'sup' in processed:
        return 'nothing!'

    # Add a default response in case none of the conditions are met
    return 'I didn\'t understand what you said.'

async def stream_text(context: str):
    # Passed parameters, llama-precise
    request = {
        'prompt': context,
        'max_new_tokens': 2048,
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.1,
        'typical_p': 1,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': True,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': False,
        'stopping_strings': []
    }

    async with websockets.connect(URI) as websocket:
        await websocket.send(json.dumps(request))

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['text']
                case 'stream_end':
                    yield None
                    return

# Function to handle typing status, placeholder message interferes with bot typing
def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

@send_action(ChatAction.TYPING)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is None
    if update.message is not None:
        
        # Send placeholder message while waiting for the response
        placeholder_message = await update.message.reply_text("...")
        
        # Send a typing action while waiting for the response
        await update.message.chat.send_action(action="typing")

        # Get basic info of the incoming message
        message_type: str = update.message.chat.type
        chat_id: int = update.message.chat.id

        # Create a database for messages
        message = update.message.text or ""
        
        # Print a log for debugging if debugging is enabled
        if debug: print(f'User ({chat_id}) in {message_type}: "{message}"')

        # Save the responses to the database
        if chat_id not in chat_responses:
            message = instruction_base['Alpaca'][0]+instruction_base['Alpaca'][1]+ message.replace(BOT_USERNAME, "", 1).lstrip() + instruction_base['Alpaca'][2]
        else:
            message = chat_responses[chat_id][-2048:] + instruction_base['Alpaca'][1] + message.replace(BOT_USERNAME, "", 1).lstrip() + instruction_base['Alpaca'][2]

        # Make a generator for the response
        response_generator = stream_text(message)

        # Make a string placeholder for the final response
        response_string = ""
        response_cache = ""

        # Iterate through the generator and send the response
        async for response in response_generator:
            if response != None:
                response_cache += response
                if debug:
                    print(response, end='')
                    sys.stdout.flush()
            
            # If the response is too short, continue the loop, continue caching
            if len(response_cache) < 75 and response != None:
                continue
            
            # Debugging if there is any problems with code blocks
            if codeblock_debug: print(response_cache, "\t\topen block: ", mdconvert.has_open_code_block(response_string), "open inline: ", mdconvert.has_open_inline_code(response_string))
            
            # Cache the response
            response_string += response_cache
            response_cache = "" 
            
            # Handling incomlete code blocks while streaming text
            if mdconvert.has_open_code_block(response_string):
                await context.bot.edit_message_text(mdconvert.escape(response_string)+"```", chat_id=placeholder_message.chat_id, 
                                            message_id=placeholder_message.message_id, parse_mode=ParseMode.MARKDOWN_V2)
            elif mdconvert.has_open_inline_code(response_string):
                await context.bot.edit_message_text(mdconvert.escape(response_string)+"`", chat_id=placeholder_message.chat_id, 
                                            message_id=placeholder_message.message_id, parse_mode=ParseMode.MARKDOWN_V2)
            else:
                await context.bot.edit_message_text(mdconvert.escape(response_string), chat_id=placeholder_message.chat_id, 
                                            message_id=placeholder_message.message_id, parse_mode=ParseMode.MARKDOWN_V2)

        # First check if the chat_id is already in the database, and save the response
        chat_responses[chat_id] = chat_responses.setdefault(chat_id, '') + message + response_string

        # Print the database to the console for debugging if enabled
        if database_debug: print(chat_responses[chat_id])
        

@send_action(ChatAction.TYPING)
async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message is not None:
        chat_id = update.edited_message.chat.id
        edited_message = update.edited_message.text.replace(BOT_USERNAME, '').strip() if update.edited_message.text else None
        print(f'User ({chat_id}) in an edited message: "{edited_message}"')
        if edited_message is None:
            return
        response = generate_text(edited_message)
        print('Bot:', response)
        if update.edited_message:
            await update.edited_message.reply_text("I saw that you edited a message! Here is my new response:\n" + response)

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log the error message
    logging.exception(context.error)

    # Send an error message to the user
    try:
        if update.message:
            await update.message.reply_text('An error occurred. Please try again later.')
        elif update.edited_message:
            await update.edited_message.reply_text('An error occurred. Please try again later.')
    except Exception as e:
        logging.error(f'Error sending error message: {str(e)}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('wipe', wipe_history_command))

    # Messages
    app.add_handler(MessageHandler(filters.UpdateType.MESSAGE, handle_message))

    # Edited messages
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_edited_message))
    
    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=1)