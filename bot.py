import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OWNER_WALLET = "0xC6219FFBA27247937A63963E4779e33F7930d497"

# 🧠 In-memory user database
users = {}
referrals = {}
balances = {}

# --------------------------------
# 🔹 START COMMAND
# --------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_id = context.args[0] if context.args else None

    # Register new user
    if user_id not in users:
        users[user_id] = {"referrer": ref_id}
        balances[user_id] = 0
        referrals.setdefault(ref_id, []).append(user_id)
    else:
        ref_id = users[user_id].get("referrer")

    ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_id}"

    text = (
        f"👋 Welcome *{update.effective_user.first_name}!* \n\n"
        f"🚀 Earn rewards by inviting friends!\n"
        f"🔗 Your referral link:\n`{ref_link}`\n\n"
        f"💎 To join *Premium Signals Group*, send *50 USDT (BEP20)* to:\n"
        f"`{OWNER_WALLET}`\n\n"
        f"Once done, send /joinpremium"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --------------------------------
# 💰 JOIN PREMIUM
# --------------------------------
async def joinpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (
        f"💵 To join *Premium Signals*, send *50 USDT (BEP20)* to this address:\n"
        f"`{OWNER_WALLET}`\n\n"
        f"After payment, wait for admin approval.\n"
        f"🧠 Once approved, you’ll get this group invite:\n"
        f"https://t.me/+ra4eSwIYWukwMjRl\n\n"
        f"🔥 Benefits:\n"
        f"🚀 Early coin alerts before pumps\n"
        f"🚀 2–5 signals per day\n"
        f"🚀 Auto-trading by bot\n"
        f"🚀 Daily *exclusive premium signals!*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --------------------------------
# 💎 BALANCE
# --------------------------------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bal = balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Your referral balance: *{bal} USDT*", parse_mode="Markdown")

# --------------------------------
# 💸 WITHDRAW
# --------------------------------
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💸 *Withdrawal Request*\n\nUser: `{user_id}`\nWallet: `{wallet}`\nAmount: {bal} USDT",
        parse_mode="Markdown"
    )
    await update.message.reply_text("✅ Your withdrawal request has been sent to admin!")

# --------------------------------
# 🧑‍💻 ADMIN ONLY — APPROVE PAYMENT
# --------------------------------
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # hide from non-admins

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /approve <user_id> <amount>")
        return

    uid = int(context.args[0])
    amt = float(context.args[1])

    balances[uid] = balances.get(uid, 0) + amt

    referrer = users.get(uid, {}).get("referrer")
    if referrer:
        balances[referrer] = balances.get(referrer, 0) + 10  # 💎 Referral bonus

    await update.message.reply_text(f"✅ Approved {amt} USDT for {uid}")
    try:
        await context.bot.send_message(
            chat_id=uid,
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

    print("✅ Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
