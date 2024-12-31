from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import random

# Your Bot's token here
API_TOKEN = '7697911594:AAG3GVGFn1ZUMgdIqQ7Rr3QNNz21xtkzvYY'

# Store for topic data, answers, and participants
topic_chat_id = None
correct_answer = None
correct_answer_users = []

# Helper function to check if the bot is in the right topic
def is_in_topic(update: Update) -> bool:
    global topic_chat_id
    return topic_chat_id and update.message.chat.id == topic_chat_id

# Command handler for '/usethistopic'
async def usethistopic(update: Update, context: CallbackContext) -> None:
    global topic_chat_id
    if update.message.chat.type == 'supergroup':
        topic_chat_id = update.message.chat.id
        await update.message.reply_text(
            "Bot is now active in this group's topic. Use /setanswer to configure the answer."
        )
    else:
        await update.message.reply_text(
            "Please use /usethistopic in a supergroup to set the bot's topic."
        )

# Command handler for '/setanswer'
async def setanswer(update: Update, context: CallbackContext) -> None:
    global correct_answer
    if is_in_topic(update):
        if context.args:
            correct_answer = ' '.join(context.args)
            try:
                # Delete the command message and the previous message
                await update.message.delete()
                if update.message.reply_to_message:
                    await update.message.reply_to_message.delete()
            except Exception as e:
                print(f"Error deleting messages: {e}")
        else:
            await update.message.reply_text("Please provide an answer after the command.")
    else:
        await update.message.reply_text(
            "You must use this command in the correct topic. Please use /usethistopic to set the topic."
        )

# Message handler to handle answers
async def handle_messages(update: Update, context: CallbackContext) -> None:
    global correct_answer, correct_answer_users
    if is_in_topic(update):
        user = update.message.from_user
        username = user.username

        # Acknowledge the submitted answer
        await update.message.reply_text(f"{username} has submitted an answer.")

        # Check if the answer is correct and add the user to the list
        if correct_answer and update.message.text.strip().lower() == correct_answer.strip().lower():
            if username not in correct_answer_users:
                correct_answer_users.append(username)

# Command handler for '/correctanswers'
async def correctanswers(update: Update, context: CallbackContext) -> None:
    if is_in_topic(update):
        if correct_answer_users:
            await update.message.reply_text(f"Users who answered correctly: {', '.join(correct_answer_users)}")
        else:
            await update.message.reply_text("No one has answered correctly yet.")
    else:
        await update.message.reply_text(
            "You must use this command in the correct topic."
        )

# Command handler for '/winners'
async def winners(update: Update, context: CallbackContext) -> None:
    global correct_answer_users, correct_answer, topic_chat_id
    if is_in_topic(update):
        if correct_answer_users:
            if context.args and context.args[0].isdigit():
                num_winners = int(context.args[0])
                if num_winners <= len(correct_answer_users):
                    selected_winners = random.sample(correct_answer_users, num_winners)
                    await update.message.reply_text(f"Random winners: {', '.join(selected_winners)}")
                    # Reset the bot state
                    correct_answer_users.clear()
                    correct_answer = None
                else:
                    await update.message.reply_text(f"There are not enough users who answered correctly.")
            else:
                await update.message.reply_text("Please provide a valid number of winners.")
        else:
            await update.message.reply_text("No one has answered correctly yet.")
    else:
        await update.message.reply_text("You must use this command in the correct topic.")

# Command handler for '/help'
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Available commands:\n"
        "/usethistopic - Set the bot's topic.\n"
        "/setanswer [answer] - Set the correct answer (message and previous message are deleted).\n"
        "/correctanswers - List all users who answered correctly.\n"
        "/winners [number] - Select a random number of winners from correct answers and reset.\n"
        "/help - Show this help message."
    )
    await update.message.reply_text(help_text)

# Main function to set up the bot
def main():
    # Initialize the bot with your API token
    application = Application.builder().token(API_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler('usethistopic', usethistopic))
    application.add_handler(CommandHandler('setanswer', setanswer))
    application.add_handler(CommandHandler('correctanswers', correctanswers))
    application.add_handler(CommandHandler('winners', winners))
    application.add_handler(CommandHandler('help', help_command))

    # Register message handler to monitor all messages in the topic
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
