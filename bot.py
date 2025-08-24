import logging
import openai
import streamlit_app.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API Key
openai.api_key = "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"

# --------------------------
# AI Response Function
# --------------------------
def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",   # Or "gpt-4"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# --------------------------
# Start Command
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to *AI Trading Mentor Bot*!\n\n"
        "Ask me about any stock/index.\n\n"
        "Example: 'Nifty ka support batao' or 'BankNifty trend future me kaisa hoga?'\n\n"
        "Main AI + Technical Analysis dono use karta hoon 📊",
        parse_mode="Markdown"
    )

# --------------------------
# Handle User Message
# --------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # AI se intelligent reply
    ai_reply = ask_ai(user_text)

    # Telegram Button Options
    keyboard = [
        [
            InlineKeyboardButton("Support/Resistance", callback_data="levels"),
            InlineKeyboardButton("Breakout", callback_data="breakout"),
        ],
        [
            InlineKeyboardButton("Trend Report", callback_data="trend"),
            InlineKeyboardButton("Full Analysis", callback_data="full"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🤔 *AI Suggestion:*\n{ai_reply}\n\n"
        "👇 Choose technical analysis option:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# --------------------------
# Handle Buttons
# --------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "levels":
        msg = "📊 Support: 12,750 | Resistance: 13,250"
    elif query.data == "breakout":
        msg = "🚀 Breakout detected: Bullish momentum forming."
    elif query.data == "trend":
        msg = "📈 Trend: Sideways to Bullish"
    else:
        msg = "📑 Full Analysis: Support 12,750 | Resistance 13,250 | Trend: Bullish"

    await query.edit_message_text(msg)

# --------------------------
# Main Function
# --------------------------
def main():
    TOKEN = "8131089767:AAGCq2zeHR-sCv9moT6kHT6s-Kpwp9SgcSM"

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 AI Trading Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

