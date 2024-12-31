import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Global settings to store group-topic mappings and contest information
group_settings = {}

# Command: /start (triggered when the bot is added to a group)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    group_name = update.message.chat.title  # Get group name
    topic_id = None  # Initially, no specific topic is set for this group

    if group_id not in group_settings:
        group_settings[group_id] = {'topic_id': None}

    await update.message.reply_text(f"✅ Bot started in group: {group_name} ({group_id}).\nUse /usethistopic to activate the bot in the current topic.")

# Command: /usethistopic (activated in the current topic where the command is issued)
async def use_this_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    group_name = update.message.chat.title  # Get group name
    topic_id = update.message.message_id  # Using message ID as a unique topic ID (this is a placeholder)

    # Store the topic ID as the active topic for this group
    group_settings[group_id]['topic_id'] = topic_id

    # Send feedback to the user
    await update.message.reply_text(f"✅ Bot is now activated in the topic with ID {topic_id} in group {group_name}.")

# Command: /setquestion (allows to set the question in the group)
async def set_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    question = ' '.join(context.args)

    if len(question) == 0:
        await update.message.reply_text("❌ Please provide a question to be answered.")
        return

    # Store the question for this group
    if group_id not in group_settings:
        group_settings[group_id] = {}

    group_settings[group_id]['question'] = question
    await update.message.reply_text(f"✅ Question set: {question}")

# Command: /setanswer (set the correct answer and erase the message from the chat)
async def set_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    correct_answer = ' '.join(context.args)

    if len(correct_answer) == 0:
        await update.message.reply_text("❌ Please provide a valid answer for the contest.")
        return

    # Store the correct answer for this group
    if group_id not in group_settings:
        group_settings[group_id] = {}

    group_settings[group_id]['correct_answer'] = correct_answer

    # Delete the /setanswer message to hide it from other users
    await update.message.delete()

    await update.message.reply_text("✅ Correct answer has been set (this message is now hidden).")

# Command: /choosewinners (choose winners based on the correct answer and number of winners)
async def choose_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id

    # Check if the correct answer is set
    if group_id not in group_settings or 'correct_answer' not in group_settings[group_id]:
        await update.message.reply_text("❌ No correct answer has been set yet. Use /setanswer to set it.")
        return

    correct_answer = group_settings[group_id]['correct_answer']
    
    # Parse the number of winners from the command arguments
    if len(context.args) == 0 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Please specify the number of winners.")
        return

    num_winners = int(context.args[0])

    # If no winners are to be selected
    if num_winners <= 0:
        await update.message.reply_text("❌ The number of winners must be greater than 0.")
        return

    # Find users who answered correctly
    correct_users = []
    for msg in update.message.chat.get_messages():
        if correct_answer.lower() in msg.text.lower():  # Case-insensitive comparison
            correct_users.append(msg.from_user.username)

    # If no one answered correctly
    if not correct_users:
        await update.message.reply_text("❌ No one answered correctly.")
        return

    # Check if the number of winners exceeds the number of users with correct answers
    if num_winners > len(correct_users):
        await update.message.reply_text(f"❌ There are only {len(correct_users)} users who answered correctly. The number of winners has been adjusted.")
        num_winners = len(correct_users)

    # Randomly select winners
    winners = random.sample(correct_users, num_winners)

    # Announce the winners
    winners_list = "\n".join(winners)
    await update.message.reply_text(f"🎉 The winners are:\n{winners_list}")

# Message Handler: Bot only responds to messages in a specific topic
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat_id
    group_name = update.message.chat.title
    message_topic_id = update.message.message_id  # Using message ID as a unique topic ID (this is a placeholder)

    # Get topic_id from group settings
    topic_id = group_settings.get(group_id, {}).get('topic_id', None)

    if topic_id and message_topic_id == topic_id:
        # This is where you can process the message, e.g., answer a question in the contest
        await update.message.reply_text(f"✅ Message received in topic {topic_id}. Proceeding with contest task...")
    else:
        # Ignore messages not in the correct topic
        pass

# Create the application and add handlers
def main():
    # Create the bot application (replace 'your-bot-token' with your bot's token)
    application = Application.builder().token('7697911594:AAG3GVGFn1ZUMgdIqQ7Rr3QNNz21xtkzvYY').build()

    # Add handlers for different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setquestion", set_question))
    application.add_handler(CommandHandler("setanswer", set_answer))
    application.add_handler(CommandHandler("usethistopic", use_this_topic))
    application.add_handler(CommandHandler("choosewinners", choose_winners))
    application.add_handler(MessageHandler(filters.Text(), handle_message))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
