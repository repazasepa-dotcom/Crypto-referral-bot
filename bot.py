import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# In-memory databases
USERS = {}
BALANCES = {}
REFERRALS = {}
PAIRS = {}
JOINED_PREMIUM = set()

# Your fixed USDT BEP20 address
PAYMENT_ADDRESS = "0xC6219FFBA27247937A63963E4779e33F7930d497"

# Premium link
PREMIUM_GROUP = "https://t.me/+ra4eSwIYWukwMjRl"

# ---------------------------
# 🌟 Basic Bot Commands
# ---------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    args = context.args

    if user_id not in USERS:
        USERS[user_id] = {"ref": None}
        BALANCES[user_id] = 0
        PAIRS[user_id] = 0

        if args:
            ref_id = int(args[0])
            if ref_id != user_id and ref_id in USERS:
                USERS[user_id]["ref"] = ref_id
                REFERRALS.setdefault(ref_id, []).append(user_id)

    text = (
        f"👋 Welcome *{user.first_name or 'Trader'}!* 🚀\n\n"
        "💎 Earn by referring friends and joining premium signals!\n\n"
        f"💰 To join Premium, send *50 USDT (BEP20)* to:\n`{PAYMENT_ADDRESS}`\n\n"
        "Once done, send /joined to confirm payment ✅"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Bot Commands:*\n\n"
        "💎 /start — Start or get your referral link\n"
        "👥 /referral — View your referral info\n"
        "💰 /balance — Check your earnings\n"
        "🏧 /withdraw — Withdraw your referral rewards\n"
        "⭐️ /joined — Confirm your premium payment"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ---------------------------
# 💰 Referral and Premium
# ---------------------------

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in USERS:
        await update.message.reply_text("Please use /start first.")
        return

    link = f"https://t.me/{context.bot.username}?start={user_id}"
    refs = REFERRALS.get(user_id, [])
    text = (
        f"👥 *Your Referral Info:*\n\n"
        f"🔗 Referral Link: {link}\n"
        f"👤 Direct Referrals: {len(refs)}\n"
        f"💵 Balance: {BALANCES.get(user_id, 0)} USDT\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in JOINED_PREMIUM:
        await update.message.reply_text("✅ You’re already in Premium!")
        return

    JOINED_PREMIUM.add(user_id)
    ref = USERS.get(user_id, {}).get("ref")

    # Direct referral bonus (10 USDT)
    if ref:
        BALANCES[ref] = BALANCES.get(ref, 0) + 10
        await context.bot.send_message(ref, f"🎉 Your referral joined Premium! +10 USDT")

        # Pairing bonus (5 USDT up to 3 pairs)
        PAIRS[ref] = PAIRS.get(ref, 0) + 1
        if PAIRS[ref] <= 3:
            BALANCES[ref] += 5
            await context.bot.send_message(ref, f"🤝 Pair bonus earned! +5 USDT (Pair {PAIRS[ref]}/3)")

    text = (
        "✅ *Payment Confirmed!* Welcome to Premium! 🎉\n\n"
        "🔥 *Benefits:*\n"
        "🚀 Early coin alerts\n"
        "🎯 Buy & sell targets\n"
        "📈 2–5 daily signals\n"
        "🤖 Auto trading bot\n"
        "💎 1–3 special premium signals daily\n\n"
        f"👉 Join here: {PREMIUM_GROUP}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ---------------------------
# 💵 Withdraw & Admin
# ---------------------------

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = BALANCES.get(user_id, 0)
    await update.message.reply_text(f"💰 Your balance: {bal} USDT")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = BALANCES.get(user_id, 0)

    if bal < 20:
        await update.message.reply_text("❌ Minimum withdrawal is 20 USDT.")
        return

    await update.message.reply_text(
        "💵 Enter your *USDT (BEP20)* address to withdraw:",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_withdraw"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("awaiting_withdraw"):
        address = update.message.text.strip()
        amount = BALANCES.get(user_id, 0)
        BALANCES[user_id] = 0
        context.user_data["awaiting_withdraw"] = False

        # Notify admin
        await context.bot.send_message(
            ADMIN_ID,
            f"💸 Withdrawal Request\n\nUser: {user_id}\nAmount: {amount} USDT\nAddress: `{address}`",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Withdrawal request sent to admin. Expect manual payment soon!")

# ---------------------------
# 🚀 Start the Bot (Background Worker Safe)
# ---------------------------

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("joined", joined))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot started successfully! Running as background worker...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
