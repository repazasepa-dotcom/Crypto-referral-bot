import os
import asyncio
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OWNER_WALLET = "0xC6219FFBA27247937A63963E4779e33F7930d497"

# ------------------------------
# 📁 File paths
# ------------------------------
DATA_FILE = "data.json"
PAIR_FILE = "pairing.json"

# ------------------------------
# 💾 Load or Save Data
# ------------------------------
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

users = load_json(DATA_FILE).get("users", {})
referrals = load_json(DATA_FILE).get("referrals", {})
balances = load_json(DATA_FILE).get("balances", {})
pairing_count = load_json(PAIR_FILE)

def save_all():
    save_json(DATA_FILE, {"users": users, "referrals": referrals, "balances": balances})
    save_json(PAIR_FILE, pairing_count)

# --------------------------------
# 🔹 START COMMAND
# --------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    ref_id = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"referrer": ref_id}
        balances[user_id] = 0
        referrals.setdefault(ref_id, []).append(user_id)
        save_all()

    ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_id}"

    text = (
        f"👋 Welcome *{update.effective_user.first_name}!* \n\n"
        f"💸 Earn rewards by inviting your friends!\n"
        f"🔗 Your referral link:\n`{ref_link}`\n\n"
        f"💎 To join *Premium Signals Group*, send *50 USDT (BEP20)* to:\n"
        f"`{OWNER_WALLET}`\n\n"
        f"Then send /joinpremium once paid ✅"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --------------------------------
# 💰 JOIN PREMIUM
# --------------------------------
async def joinpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"💵 To join *Premium Signals*, send *50 USDT (BEP20)* to this address:\n"
        f"`{OWNER_WALLET}`\n\n"
        f"After payment, wait for admin approval.\n\n"
        f"🔥 Benefits:\n"
        f"🚀 Early coin alerts\n"
        f"🚀 2–5 daily signals\n"
        f"🚀 Auto trading by bot\n"
        f"🚀 Daily 1–3 special signals (Premium only)\n\n"
        f"➡️ After approval, you’ll be invited to:\n"
        f"https://t.me/+ra4eSwIYWukwMjRl"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --------------------------------
# 💎 BALANCE
# --------------------------------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    bal = balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Your referral balance: *{bal} USDT*", parse_mode="Markdown")

# --------------------------------
# 💸 WITHDRAW
# --------------------------------
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    msg_parts = update.message.text.split()
    if len(msg_parts) < 2:
        await update.message.reply_text("📤 Usage: /withdraw <your BEP20 wallet address>")
        return

    wallet = msg_parts[1]
    bal = balances.get(user_id, 0)

    if bal < 20:
        await update.message.reply_text("⚠️ Minimum withdrawal is *20 USDT*.", parse_mode="Markdown")
        return

    balances[user_id] = 0
    save_all()

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💸 *Withdrawal Request*\n\n👤 User: `{user_id}`\n🏦 Wallet: `{wallet}`\n💰 Amount: {bal} USDT",
        parse_mode="Markdown"
    )
    await update.message.reply_text("✅ Withdrawal request sent to admin!")

# --------------------------------
# 🧑‍💻 ADMIN — APPROVE PAYMENT
# --------------------------------
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # hidden from normal users

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /approve <user_id> <amount>")
        return

    uid = str(context.args[0])
    amt = float(context.args[1])
    balances[uid] = balances.get(uid, 0) + amt

    # Direct bonus
    referrer = users.get(uid, {}).get("referrer")
    if referrer:
        balances[referrer] = balances.get(referrer, 0) + 10

        # Pairing bonus (max 3 per day)
        today = datetime.now().strftime("%Y-%m-%d")
        user_pairs = pairing_count.get(referrer, {"date": today, "count": 0})

        if user_pairs["date"] != today:
            user_pairs = {"date": today, "count": 0}

        if user_pairs["count"] < 3:
            balances[referrer] += 5
            user_pairs["count"] += 1
            pairing_count[referrer] = user_pairs

    save_all()
    await update.message.reply_text(f"✅ Approved {amt} USDT for {uid}")

    try:
        await context.bot.send_message(
            chat_id=int(uid),
            text="🎉 Payment confirmed! You are now part of our *Premium Signals Group!* 🔥",
            parse_mode="Markdown"
        )
    except:
        pass

# --------------------------------
# 🚀 MAIN
# --------------------------------
async def main():
    print("✅ Initializing bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joinpremium", joinpremium))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("approve", approve))

    print("✅ Bot is running (with auto-save)...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
