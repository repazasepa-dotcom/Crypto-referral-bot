# bot.py
import os
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- Load environment variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = os.environ.get("ADMIN_ID", "")
ADMINS = [int(x) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]

# --- In-memory user data ---
users = {}  # {user_id: {...}}

# --- Settings ---
DIRECT_BONUS = 20        # USDT per direct referral (when referral joins premium)
PAIRING_BONUS = 5        # USDT per left-right pair
PAIR_CAP = 3             # Max pairs per day per user
MIN_WITHDRAW = 20        # Minimum withdrawal threshold
PREMIUM_GROUP_LINK = "https://t.me/+ra4eSwIYWukwMjRl"
DEPOSIT_ADDRESS = "0xC6219FFBA27247937A63963E4779e33F7930d497"
DEPOSIT_LINK = f"https://bscscan.com/address/{DEPOSIT_ADDRESS}"

PREMIUM_BENEFITS = f"""
🔥 *Premium Signals Access* 🔥
🚀 Know the coin *before pump*
🎯 Guided *buy/sell targets*
📈 *2-5 daily signals*
🤖 *Auto trading by bot*

💎 *Special Signals (Premium Only)* 💎
- 1-3 coins daily
- Expected to *pump within 24 hours* ⚡
"""

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    referrer_id = int(args[0]) if args else None

    if user_id in users:
        await update.message.reply_text("🙌 You are already registered!")
        return

    users[user_id] = {
        "ref": referrer_id,
        "balance": 0,
        "left": None,
        "right": None,
        "withdraw_pending": False,
        "pairs_today": 0,
        "last_pair_date": None,
        "premium_joined": False,
        "awaiting_premium_payment": False,
        "withdraw_address": None
    }

    await update.message.reply_text(
        f"🎉 Welcome, {update.effective_user.first_name}! 🎉\n\n"
        f"🆔 Your referral ID: {user_id}\n"
        f"Share your link to earn rewards! 💰"
    )

# --- /balance ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = users.get(user_id, {"balance": 0})["balance"]
    await update.message.reply_text(f"💵 Your current balance: {bal} USDT")

# --- /referral ---
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(
        f"🔗 Your referral link:\n{ref_link}\n\n"
        f"Share with friends and earn referral bonuses! 💎"
    )

# --- /joinpremium ---
async def join_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = users.get(user_id)
    if not user:
        await update.message.reply_text("⚠️ Use /start first.")
        return
    if user.get("premium_joined"):
        await update.message.reply_text("✅ You are already premium.")
        return
    user["awaiting_premium_payment"] = True
    await update.message.reply_markdown_v2(
        f"🚀 To join *Premium Signals*:\n"
        f"Send *50 USDT* to this BSC address:\n[{DEPOSIT_ADDRESS}]({DEPOSIT_LINK})\n\n"
        f"Then reply here with your wallet address to confirm payment. ✅"
    )

# --- /withdraw ---
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = users.get(user_id)
    if not user:
        await update.message.reply_text("⚠️ Use /start first.")
        return

    balance = user.get("balance", 0)
    if balance < MIN_WITHDRAW:
        await update.message.reply_text(f"⚠️ Minimum withdrawal is {MIN_WITHDRAW} USDT. Your balance: {balance} USDT")
        return

    user["withdraw_pending"] = True
    await update.message.reply_text("💸 Please enter your **USDT BSC (BEP-20)** wallet address to withdraw your referral rewards:")

# --- Credit referral and pairing bonuses ---
def credit_referral_bonuses(user_id):
    current_user = users[user_id]
    ref_id = current_user.get("ref")
    if ref_id and ref_id in users:
        # direct bonus
        users[ref_id]["balance"] += DIRECT_BONUS

        # pairing logic
        ref_user = users[ref_id]
        if not ref_user["left"]:
            ref_user["left"] = user_id
        elif not ref_user["right"]:
            ref_user["right"] = user_id

        today = datetime.date.today()
        if ref_user["left"] and ref_user["right"]:
            if ref_user["last_pair_date"] != today:
                ref_user["pairs_today"] = 0
                ref_user["last_pair_date"] = today
            if ref_user["pairs_today"] < PAIR_CAP:
                ref_user["balance"] += PAIRING_BONUS
                ref_user["pairs_today"] += 1

# --- Handle messages (payment confirm / withdraw address) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = users.get(user_id)
    if not user:
        return

    text = update.message.text.strip()

    # Confirm premium payment
    if user.get("awaiting_premium_payment"):
        if text.startswith("0x") and len(text) == 42:
            user["premium_joined"] = True
            user["awaiting_premium_payment"] = False

            # credit referrer
            credit_referral_bonuses(user_id)

            await update.message.reply_text(f"✅ Payment received! You are now premium.\nJoin the premium group:\n{PREMIUM_GROUP_LINK}")
            await update.message.reply_markdown_v2(PREMIUM_BENEFITS)
            return
        else:
            await update.message.reply_text("⚠️ Invalid BSC address. Must start with 0x and be 42 characters long.")
            return

    # Handle withdrawal address
    if user.get("withdraw_pending"):
        if text.startswith("0x") and len(text) == 42:
            user["withdraw_address"] = text
            amount = user["balance"]
            user["balance"] = 0
            user["withdraw_pending"] = False

            await update.message.reply_text(f"✅ Withdrawal of {amount} USDT recorded. Admin will send to:\n{text} 🏦")

            for admin_id in ADMINS:
                try:
                    await context.bot.send_message(admin_id, f"💰 User {user_id} requested withdrawal of {amount} USDT to {text}")
                except Exception:
                    pass
        else:
            await update.message.reply_text("⚠️ Invalid BSC address. Must start with 0x and be 42 characters long.")
        return

# --- /payout (admin only) ---
async def payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        return
    msg = "\n".join([f"👤 {uid}: {data['balance']} USDT" for uid, data in users.items()])
    await update.message.reply_text(msg or "No users yet.")

# --- Main ---
def main():
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not set in environment")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("joinpremium", join_premium))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("payout", payout))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
