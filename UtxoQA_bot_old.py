import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Dictionary to store answers per chat topic
answers = {}

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello! I'm your Contest Bot! 🎉\n"
        "Use /help to see all the available commands.\n"
        "Let's get started!"
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 Available Commands:\n"
        "/start - Start the bot and see a welcome message.\n"
        "/help - Show this help message.\n"
        "/setanswer <answer> - Set the correct answer for the contest.\n"
        "/choosewinners <number> - Choose a random number of winners from those who answered correctly."
    )

# Command: /setanswer
async def set_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setanswer <correct_answer>")
        return
    correct_answer = context.args[0].strip().lower()
    topic_id = update.message.message_thread_id
    context.chat_data[topic_id] = {'correct_answer': correct_answer, 'participants': {}}
    await update.message.reply_text(f"✅ Correct answer set to: {correct_answer}")

# Message Handler: Collect answers
async def collect_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_id = update.message.message_thread_id
    if topic_id not in context.chat_data:
        return  # Ignore if no contest is set for this topic
    correct_answer = context.chat_data[topic_id]['correct_answer']
    user = update.message.from_user
    user_answer = update.message.text.strip().lower()
    if user_answer == correct_answer:
        context.chat_data[topic_id]['participants'][user.id] = user.full_name
        await update.message.reply_text(f"🎉 Correct answer recorded for {user.full_name}!")
    else:
        await update.message.reply_text(f"❌ Sorry, {user.full_name}, that's not the correct answer.")

# Command: /choosewinners
async def choose_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: /choosewinners <number_of_winners>")
        return
    num_winners = int(context.args[0])
    topic_id = update.message.message_thread_id
    if topic_id not in context.chat_data or not context.chat_data[topic_id]['participants']:
        await update.message.reply_text("😔 No participants with correct answers to choose from!")
        return
    participants = list(context.chat_data[topic_id]['participants'].items())
    winners = random.sample(participants, min(num_winners, len(participants)))
    winner_names = ", ".join(name for _, name in winners)
    await update.message.reply_text(f"🏆 Winners: {winner_names}\n🎉 Congratulations!")

# Main Function
def main():
    # Set up the application
    application = Application.builder().token("7697911594:AAG3GVGFn1ZUMgdIqQ7Rr3QNNz21xtkzvYY").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setanswer", set_answer))
    application.add_handler(CommandHandler("choosewinners", choose_winners))

    # Add message handler for answers
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, collect_answer))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
