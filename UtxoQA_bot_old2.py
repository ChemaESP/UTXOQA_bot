import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Dictionary to store settings for each group
group_settings = {}

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello! I'm your Contest Bot! 🎉\n"
        "Use /help to see all available commands.\n"
        "Let's get started!"
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠 Available Commands:\n"
        "/start - Start the bot and see a welcome message.\n"
        "/help - Show this help message.\n"
        "/getids - Display the group ID and current topic ID.\n"
        "/settopic <group_id> [topic_id] - Restrict bot usage to a group or a specific topic.\n"
        "/setquestion <question> - Set the contest question to be answered.\n"
        "/setanswer <answer> - Set the correct answer for the contest.\n"
        "/choosewinners <number> - Choose winners who wrote the correct answer."
    )

# Command: /getids
async def get_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    topic_id = update.message.message_thread_id
    await update.message.reply_text(
        f"ℹ️ Group ID: `{group_id}`\nTopic ID: `{topic_id}`\n"
        "Use these IDs to configure the bot."
    )

# Command: /settopic
async def set_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id

    if len(context.args) < 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: /settopic <group_id> [topic_id]")
        return

    target_group_id = int(context.args[0])
    target_topic_id = int(context.args[1]) if len(context.args) > 1 else None

    if group_id != target_group_id:
        await update.message.reply_text("❌ You can only set the topic for this group.")
        return

    if group_id not in group_settings:
        group_settings[group_id] = {}

    if target_topic_id:
        group_settings[group_id]['topic_id'] = target_topic_id
        await update.message.reply_text(f"✅ Bot is now restricted to topic ID: {target_topic_id} in this group.")
    else:
        group_settings[group_id]['topic_id'] = None
        await update.message.reply_text(f"✅ Bot is now restricted to the General topic in this group.")

# Command: /setquestion
async def set_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    if group_id not in group_settings or 'topic_id' not in group_settings[group_id]:
        await update.message.reply_text("❌ You need to set a topic first using /settopic <group_id> [topic_id].")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: /setquestion <question>")
        return
    question = " ".join(context.args).strip()
    group_settings[group_id]['question'] = question
    await update.message.reply_text(f"✅ Contest question set:\n\n❓ {question}")

# Command: /setanswer
async def set_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    if group_id not in group_settings or 'topic_id' not in group_settings[group_id]:
        await update.message.reply_text("❌ You need to set a topic first using /settopic <group_id> [topic_id].")
        return
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setanswer <correct_answer>")
        return
    correct_answer = context.args[0].strip().lower()
    group_settings[group_id]['correct_answer'] = correct_answer
    group_settings[group_id]['answers'] = {}
    await update.message.reply_text(f"✅ Correct answer set to: {correct_answer}")

# Message Handler: Collect answers from messages
async def collect_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    topic_id = update.message.message_thread_id
    if group_id not in group_settings:
        return

    restricted_topic_id = group_settings[group_id].get('topic_id')
    if restricted_topic_id is not None and restricted_topic_id != topic_id:
        return  # Ignore messages from other topics

    if 'correct_answer' not in group_settings[group_id]:
        return  # Ignore if no answer is set

    correct_answer = group_settings[group_id]['correct_answer']
    user = update.message.from_user
    if correct_answer in update.message.text.lower():
        group_settings[group_id]['answers'][user.id] = {
            'name': user.full_name,
            'answer': update.message.text
        }
        await update.message.reply_text(f"🎉 Correct answer recorded for {user.full_name}!")

# Command: /choosewinners
async def choose_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    topic_id = update.message.message_thread_id
    if group_id not in group_settings:
        await update.message.reply_text("❌ The bot is not configured for this group.")
        return

    restricted_topic_id = group_settings[group_id].get('topic_id')
    if restricted_topic_id is not None and restricted_topic_id != topic_id:
        await update.message.reply_text("❌ This command can only be used in the specified topic.")
        return

    if 'answers' not in group_settings[group_id] or not group_settings[group_id]['answers']:
        await update.message.reply_text("😔 No participants with correct answers to choose from!")
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: /choosewinners <number_of_winners>")
        return

    num_winners = int(context.args[0])
    participants = list(group_settings[group_id]['answers'].items())
    winners = random.sample(participants, min(num_winners, len(participants)))

    # Prepare the winners list
    winner_messages = [
        f"🏆 {winner[1]['name']}: \"{winner[1]['answer']}\""
        for winner in winners
    ]
    winner_list = "\n".join(winner_messages)
    await update.message.reply_text(f"🎉 Winners:\n{winner_list}\nCongratulations to all the winners!")

# Main Function
def main():
    # Set up the application
    application = Application.builder().token("7697911594:AAG3GVGFn1ZUMgdIqQ7Rr3QNNz21xtkzvYY").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("getids", get_ids))
    application.add_handler(CommandHandler("settopic", set_topic))
    application.add_handler(CommandHandler("setquestion", set_question))
    application.add_handler(CommandHandler("setanswer", set_answer))
    application.add_handler(CommandHandler("choosewinners", choose_winners))

    # Add message handler for collecting answers
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, collect_answers))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()

