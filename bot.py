import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# -----------------------------
# COMMAND HANDLERS
# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref = context.args[0] if context.args else None
    msg = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to the Premium Signals Bot 🚀\n\n"
        "🔥 Send /joinpremium to become a member.\n"
        "💸 Invite friends using your referral link: "
        f"`https://t.me/{context.bot.username}?start={user.id}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def joinpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = "0xC6219FFBA27247937A63963E4779e33F7930d497"
    msg = (
        "💎 *Join Premium Membership (50 USDT)* 💎\n\n"
        "Send *50 USDT (BEP20)* to this address:\n"
        f"`{address}`\n\n"
        "Once payment is confirmed, your account will be activated ✅\n\n"
        "🔥 Benefits:\n"
        "🚀 Know coins *before pump*\n"
        "🚀 Buy & Sell targets\n"
        "🚀 2–5 daily signals\n"
        "🚀 Auto trading by bot\n"
        "🚀 1–3 special premium signals daily (fast pumps!)"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def myref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
    await update.message.reply_text(f"🔗 Your referral link:\n{ref_link}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Commands:\n"
        "/start - Begin\n"
        "/joinpremium - Join premium\n"
        "/myref - Get your referral link\n"
        "/help - Show this menu"
    )

# -----------------------------
# MAIN FUNCTION
# -----------------------------
async def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joinpremium", joinpremium))
    app.add_handler(CommandHandler("myref", myref))
    app.add_handler(CommandHandler("help", help_command))

    print("✅ Bot started successfully!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
