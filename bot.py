import os
import logging
import threading
import time

import streamlit as st
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------- Secrets ----------
# Streamlit Cloud: Settings -> Secrets me set karo:
# TELEGRAM_BOT_TOKEN = "123:ABC..."
# OPENAI_API_KEY = "sk-...."
TELEGRAM_BOT_TOKEN = st.secrets.get("8131089767:AAGCq2zeHR-sCv9moT6kHT6s-Kpwp9SgcSM") or os.getenv("8131089767:AAGCq2zeHR-sCv9moT6kHT6s-Kpwp9SgcSM")
OPENAI_API_KEY = st.secrets.get("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") or os.getenv("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")

# ---------- OpenAI Client (optional) ----------
# openai==1.x style
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception as e:
    openai_client = None
    logger.warning("OpenAI client init failed or not installed: %s", e)


def ask_ai(prompt: str) -> str:
    """Return AI text or a fallback suggestion if key/client missing."""
    if not openai_client:
        return "AI is temporarily offline (missing OpenAI key). Technical analysis options niche se choose karo."
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # lightweight, sasta & fast
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        # SDK 1.x returns .choices[0].message.content
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("OpenAI error")
        return f"⚠️ AI Error: {e}"


# ======================= Telegram Handlers =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to *AI Trading Mentor Bot*!\n\n"
        "Mujhse stock/index ke baare me pucho.\n"
        "Example: 'Nifty ka support?' ya 'BankNifty trend?'\n\n"
        "Main AI + Technical Analysis dono use karta hoon. 📊",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    ai_reply = ask_ai(user_text)

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
        f"🤔 *AI Suggestion:*\n{ai_reply}\n\n👇 Choose technical analysis option:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


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


def run_telegram_bot():
    """Run Telegram bot in a background daemon thread to avoid Streamlit event loop clash."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN missing. Bot will not start.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Starting Telegram bot polling...")
    # This call blocks; but we're in a separate daemon thread
    app.run_polling(allowed_updates=Update.ALL_TYPES)


# ======================= Streamlit UI =======================

st.set_page_config(page_title="My Algo Trading App", page_icon="🚀")
st.title("My Algo Trading App 🚀")

# Start bot exactly once per session/server
if "bot_started" not in st.session_state:
    thread = threading.Thread(target=run_telegram_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True

st.success("Telegram bot background me run ho raha hai. ✅")
st.write("**Status**")
st.write(f"- Telegram Token set: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
st.write(f"- OpenAI Key set: {'✅' if OPENAI_API_KEY else '❌'}")

with st.expander("Quick Test (AI)"):
    prompt = st.text_input("Kuch bhi pucho (test):", value="Nifty outlook next week?")
    if st.button("Ask AI"):
        st.write(ask_ai(prompt))

st.caption("Tip: Streamlit Secrets me `` & `` add karo.")


