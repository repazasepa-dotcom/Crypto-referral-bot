# referral_bot_complete.py
import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os
from datetime import datetime

# -----------------------
# Logging
# -----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------
# Storage files
# -----------------------
DATA_FILE = "users.json"
META_FILE = "meta.json"

# -----------------------
# Load storage
# -----------------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

if os.path.exists(META_FILE):
    with open(META_FILE, "r") as f:
        meta = json.load(f)
else:
    meta = {"last_reset": None}

# -----------------------
# Constants
# -----------------------
ADMIN_ID = 8150987682  # Your Telegram ID as admin
DIRECT_BONUS = 20
PAIRING_BONUS = 5
MAX_PAIRS_PER_DAY = 10
MEMBERSHIP_FEE = 50
BNB_ADDRESS = "0xC6219FFBA27247937A63963E4779e33F7930d497"
PREMIUM_GROUP = "https://t.me/+ra4eSwIYWukwMjRl"
MIN_WITHDRAW = 20  # USDT

# -----------------------
# Helper functions
# -----------------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def save_meta():
    with open(META_FILE, "w") as f:
        json.dump(meta, f)

def reset_pairing_if_needed():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if meta.get("last_reset") != today:
        for user in users.values():
            user["left"] = 0
            user["right"] = 0
        meta["last_reset"] = today
        save_data()
        save_meta()
        logger.info("Daily pairing counts reset.")

# -----------------------
# Command handlers
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_pairing_if_needed()
    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {
            "referrer": None,
            "balance": 0,
            "left": 0,
            "right": 0,
            "referrals": [],
            "paid": False
        }

        # Handle referral link
        if context.args:
            ref_id = context.args[0]
            if ref_id in users and ref_id != user_id:
                users[user_id]["referrer"] = ref_id
                users[ref_id].setdefault("referrals", []).append(user_id)

    save_data()

    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    benefits_text = (
        "🔥 **Premium Membership Benefits** 🔥\n\n"
        "🚀 Get Coin names **before pump**\n"
        "🚀 Guidance on **buy & sell targets**\n"
        "🚀 Receive **2-5 daily signals**\n"
        "🚀 **Auto trading by bot**\n"
        "🚀 **1-3 special signals daily** in premium channel\n"
        "   (these coins will pump within 24 hours or very short duration)\n\n"
    )

    await update.message.reply_text(
        f"{benefits_text}"
        f"💰 To access, pay {MEMBERSHIP_FEE} USDT (BNB Smart Chain BEP20) to:\n"
        f"[Click to copy BNB address]({BNB_ADDRESS})\n\n"
        f"Share your referral link to earn bonuses after your friends pay:\n{referral_link}",
        parse_mode="Markdown"
    )

# Admin-only payment confirmation
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /confirm <user_id>")
        return

    target_user_id = context.args[0]
    user = users.get(target_user_id)
    if not user:
        await update.message.reply_text("User not found.")
        return

    if user["paid"]:
        await update.message.reply_text("User is already marked as paid.")
        return

    user["paid"] = True

    # Credit referrer bonuses
    ref_id = user.get("referrer")
    if ref_id:
        users[ref_id]["balance"] += DIRECT_BONUS
        if users[ref_id]["left"] <= users[ref_id]["right"]:
            side = "left"
        else:
            side = "right"
        if users[ref_id][side] < MAX_PAIRS_PER_DAY:
            users[ref_id][side] += 1
            users[ref_id]["balance"] += PAIRING_BONUS

    save_data()

    # Send premium group link to user
    await update.message.reply_text(
        f"✅ User {target_user_id} confirmed as paid. Bonuses credited to referrer.\n\n"
        f"Here is your premium signals channel link:\n{PREMIUM_GROUP}"
    )

# Check balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_pairing_if_needed()
    user_id = str(update.effective_user.id)
    bal = users.get(user_id, {}).get("balance", 0)
    await update.message.reply_text(f"Your balance: {bal} USDT")

# Show user stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_pairing_if_needed()
    user_id = str(update.effective_user.id)
    user = users.get(user_id)
    if not user:
        await update.message.reply_text("You are not registered yet. Use /start first.")
        return

    num_referrals = len(user.get("referrals", []))
    left = user.get("left", 0)
    right = user.get("right", 0)
    balance_amount = user.get("balance", 0)
    paid = user.get("paid", False)

    msg = (
        f"📊 **Your Stats:**\n"
        f"Balance: {balance_amount} USDT\n"
        f"Direct referrals: {num_referrals}\n"
        f"Left pairs today: {left}\n"
        f"Right pairs today: {right}\n"
        f"Membership paid: {'✅' if paid else '❌'}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# User withdrawal request
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = users.get(user_id)
    if not user:
        await update.message.reply_text("You are not registered yet. Use /start first.")
        return

    balance_amount = user.get("balance", 0)
    if balance_amount < MIN_WITHDRAW:
        await update.message.reply_text(
            f"Your balance is {balance_amount} USDT. Minimum withdrawal is {MIN_WITHDRAW} USDT."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Please provide your BEP20 wallet address. Usage:\n/withdraw <wallet_address>"
        )
        return

    wallet_address = context.args[0]

    # Deduct balance
    user["balance"] -= balance_amount
    save_data()

    # Notify user
    await update.message.reply_text(
        f"✅ Withdrawal request received!\n"
        f"Amount: {balance_amount} USDT\n"
        f"Wallet: {wallet_address}\n\n"
        "You will receive your USDT soon (manual processing required)."
    )

    # Notify admin automatically
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"💰 New withdrawal request!\n"
                f"User ID: {user_id}\n"
                f"Amount: {balance_amount} USDT\n"
                f"Wallet: {wallet_address}"
            )
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

# Admin processes withdrawal and notifies user
async def process_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args or len(context.args) != 2:
        await update.message.reply_text("Usage: /processwithdraw <user_id> <amount>")
        return

    target_user_id = context.args[0]
    amount = context.args[1]

    user = users.get(target_user_id)
    if not user:
        await update.message.reply_text("User not found.")
        return

    try:
        await context.bot.send_message(
            chat_id=int(target_user_id),
            text=(
                f"✅ Your withdrawal request has been processed!\n"
                f"Amount: {amount} USDT\n"
                "Funds will arrive in your BEP20 wallet shortly."
            )
        )
        await update.message.reply_text(f"✅ User {target_user_id} has been notified.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to notify user: {e}")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_ID

    help_text = (
        "📌 **Available Commands:**\n\n"
        "/start - Register and see referral link & benefits\n"
        "/balance - Check your current balance\n"
        "/stats - View your referral stats\n"
        "/withdraw <BEP20_wallet> - Request withdrawal (min 20 USDT)\n"
    )

    if is_admin:
        help_text += (
            "\n--- Admin Commands ---\n"
            "/confirm <user_id> - Confirm user payment & give premium access\n"
            "/processwithdraw <user_id> <amount> - Process a withdrawal request\n"
        )

    await update.message.reply_text(help_text, parse_mode="Markdown")

# Unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command.")

# -----------------------
# Main
# -----------------------
async def main():
    TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token

    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("processwithdraw", process_withdraw))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler(None, unknown))  # fallback

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
