import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ----------------------------
# ⚙️ SIMULATED DATABASE
# ----------------------------
users = {}  # user_id: {"ref": ref_id, "balance": 0, "premium": False, "left": None, "right": None}
pairings_today = 0

# ----------------------------
# 🧠 HELPER FUNCTIONS
# ----------------------------
def get_ref_link(user_id):
    return f"https://t.me/{os.getenv('BOT_USERNAME', 'YourBotUsername')}?start={user_id}"

async def credit_direct_bonus(ref_id):
    if ref_id in users:
        users[ref_id]["balance"] += 20  # 💰 Direct bonus 20 USDT

async def credit_pairing_bonus():
    global pairings_today
    pairings_today += 1
    if pairings_today <= 10:  # limit 10 pairs per day
        for uid, data in users.items():
            if data.get("left") and data.get("right"):
                data["balance"] += 5  # 🤝 Pairing bonus 5 USDT

# ----------------------------
# 🚀 COMMAND HANDLERS
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_id = None
    if context.args:
        try:
            ref_id = int(context.args[0])
        except ValueError:
            pass

    if user.id not in users:
        users[user.id] = {"ref": ref_id, "balance": 0, "premium": False, "left": None, "right": None}

        # assign left/right leg if ref exists
        if ref_id and ref_id in users:
            if users[ref_id]["left"] is None:
                users[ref_id]["left"] = user.id
            elif users[ref_id]["right"] is None:
                users[ref_id]["right"] = user.id

    msg = (
        f"👋 Welcome {user.first_name}!\n\n"
        f"🎯 To join Premium, deposit **50 USDT (BEP-20)** to the admin address.\n\n"
        f"Your referral link:\n{get_ref_link(user.id)}"
    )
    await update.message.reply_text(msg)

async def join_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users:
        await update.message.reply_text("❌ Please start with /start first.")
        return

    users[user.id]["premium"] = True
    await update.message.reply_text("✅ Premium activated! You can now earn rewards.")
    ref_id = users[user.id].get("ref")
    if ref_id:
        await credit_direct_bonus(ref_id)
        await credit_pairing_bonus()

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal = users.get(user.id, {}).get("balance", 0)
    await update.message.reply_text(f"💰 Your referral balance: {bal:.2f} USDT")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users:
        await update.message.reply_text("❌ Please start first with /start.")
        return

    bal = users[user.id]["balance"]
    if bal < 20:
        await update.message.reply_text("⚠️ Minimum withdrawal is 20 USDT.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("💳 Usage: /withdraw <your BEP-20 USDT address>")
        return

    address = context.args[0]
    msg = f"💸 Withdrawal request from {user.first_name} ({user.id})\nAmount: {bal:.2f} USDT\nAddress: `{address}`"
    if ADMIN_ID:
        await context.bot.send_message(ADMIN_ID, msg)
    await update.message.reply_text("✅ Withdrawal request sent to admin. Please wait for processing.")
    users[user.id]["balance"] = 0

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = " ".join(context.args)
    for uid in users:
        try:
            await context.bot.send_message(uid, f"📢 Admin Broadcast:\n{text}")
        except Exception:
            continue
    await update.message.reply_text("✅ Message sent to all users.")

# ----------------------------
# 🧩 MAIN
# ----------------------------
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join_premium))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))

    print("✅ Bot started successfully! Polling for updates...")
    await app.run_polling()

# ----------------------------
# 🔁 EVENT LOOP FIX (Render)
# ----------------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
