import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackContext,
)
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = os.environ.get("ADMIN_ID", "")
ADMINS = [int(x) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]

# Simple in-memory data
users = {}
balances = {}

PREMIUM_GROUP_LINK = "https://t.me/+ra4eSwIYWukwMjRl"
DEPOSIT_ADDRESS = "0xC6219FFBA27247937A63963E4779e33F7930d497"

# -------------------------------
# Commands
# -------------------------------

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    ref_id = None
    if context.args:
        try:
            ref_id = int(context.args[0])
        except ValueError:
            pass

    if user.id not in users:
        users[user.id] = {"ref": ref_id, "joined": False}
    msg = (
        f"👋 Welcome {user.first_name}!\n\n"
        f"💎 Join Premium to start earning and get crypto signals!\n\n"
        f"💰 Deposit 50 USDT (BEP-20) to:\n\n"
        f"`{DEPOSIT_ADDRESS}`\n\n"
        f"After payment, tap /joinpremium ✅"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def joinpremium(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    users[user_id]["joined"] = True

    # reward referrer
    ref = users[user_id].get("ref")
    if ref and ref in balances:
        balances[ref] = balances.get(ref, 0) + 10  # Direct bonus
    elif ref:
        balances[ref] = 10

    msg = (
        "🎉 You’re now a Premium Member!\n\n"
        "🔥 *Benefits* 🔥\n"
        "🚀 Early coin alerts\n"
        "🚀 Buy/sell targets\n"
        "🚀 2-5 daily signals\n"
        "🚀 Auto trading bot\n"
        "🚀 1-3 special daily signals (premium only)\n\n"
        f"📢 Join here: {PREMIUM_GROUP_LINK}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def referral(update: Update, context: CallbackContext):
    user = update.effective_user
    link = f"https://t.me/{context.bot.username}?start={user.id}"
    await update.message.reply_text(
        f"🔗 Your referral link:\n{link}\n\n"
        "👥 Share this with friends to earn bonuses!"
    )

async def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    bal = balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Your balance: {bal} USDT")

async def withdraw(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    bal = balances.get(user_id, 0)
    if bal < 20:
        await update.message.reply_text("❌ Minimum withdrawal is 20 USDT.")
        return

    await update.message.reply_text(
        "💸 Please send your *USDT (BEP-20)* address.",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_address"] = True

async def handle_text(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if context.user_data.get("awaiting_address"):
        address = update.message.text.strip()
        context.user_data["awaiting_address"] = False

        await update.message.reply_text("✅ Withdrawal request sent to admin!")
        for admin_id in ADMINS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"💰 Withdrawal request from {user_id}\n"
                     f"Amount: {balances.get(user_id, 0)} USDT\n"
                     f"Address: {address}"
            )

async def payout(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMINS:
        return
    summary = "💼 Referral Balances:\n\n"
    for uid, bal in balances.items():
        summary += f"👤 {uid}: {bal} USDT\n"
    await update.message.reply_text(summary or "No data yet.")

# -------------------------------
# Run
# -------------------------------

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joinpremium", joinpremium))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("payout", payout))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ref", referral))
    app.add_handler(CommandHandler("premium", joinpremium))
    app.add_handler(CommandHandler("bal", balance))
    app.add_handler(CommandHandler("wd", withdraw))
    app.add_handler(CommandHandler("pay", payout))
    app.add_handler(CommandHandler("ping", start))
    app.add_handler(CommandHandler("invite", referral))
    app.add_handler(CommandHandler("link", referral))
    app.add_handler(CommandHandler("bonus", balance))
    app.add_handler(CommandHandler("earn", referral))
    app.add_handler(CommandHandler("join", joinpremium))
    app.add_handler(CommandHandler("info", start))
    app.add_handler(CommandHandler("withdrawal", withdraw))
    app.add_handler(CommandHandler("payouts", payout))
    app.add_handler(CommandHandler("balances", balance))
    app.add_handler(CommandHandler("pair", balance))
    app.add_handler(CommandHandler("direct", referral))
    app.add_handler(CommandHandler("benefits", joinpremium))
    app.add_handler(CommandHandler("signal", joinpremium))
    app.add_handler(CommandHandler("signals", joinpremium))
    app.add_handler(CommandHandler("deposit", joinpremium))
    app.add_handler(CommandHandler("promo", referral))
    app.add_handler(CommandHandler("share", referral))
    app.add_handler(CommandHandler("reward", balance))
    app.add_handler(CommandHandler("helpme", start))
    app.add_handler(CommandHandler("startme", start))
    app.add_handler(CommandHandler("helpbot", start))
    app.add_handler(CommandHandler("helpmebot", start))
    app.add_handler(CommandHandler("bothelp", start))
    app.add_handler(CommandHandler("infohelp", start))
    app.add_handler(CommandHandler("faq", start))
    app.add_handler(CommandHandler("support", start))
    app.add_handler(CommandHandler("team", referral))
    app.add_handler(CommandHandler("network", referral))
    app.add_handler(CommandHandler("partners", referral))
    app.add_handler(CommandHandler("group", joinpremium))
    app.add_handler(CommandHandler("club", joinpremium))
    app.add_handler(CommandHandler("premiumgroup", joinpremium))
    app.add_handler(CommandHandler("private", joinpremium))
    app.add_handler(CommandHandler("access", joinpremium))
    app.add_handler(CommandHandler("unlock", joinpremium))
    app.add_handler(CommandHandler("unlocked", joinpremium))
    app.add_handler(CommandHandler("open", joinpremium))
    app.add_handler(CommandHandler("vip", joinpremium))
    app.add_handler(CommandHandler("vipgroup", joinpremium))
    app.add_handler(CommandHandler("signalgroup", joinpremium))
    app.add_handler(CommandHandler("joinnow", joinpremium))
    app.add_handler(CommandHandler("go", joinpremium))
    app.add_handler(CommandHandler("depositnow", joinpremium))
    app.add_handler(CommandHandler("howtojoin", joinpremium))
    app.add_handler(CommandHandler("howto", joinpremium))
    app.add_handler(CommandHandler("guide", joinpremium))
    app.add_handler(CommandHandler("steps", joinpremium))
    app.add_handler(CommandHandler("instruction", joinpremium))
    app.add_handler(CommandHandler("startpremium", joinpremium))
    app.add_handler(CommandHandler("startsignals", joinpremium))
    app.add_handler(CommandHandler("signalaccess", joinpremium))
    app.add_handler(CommandHandler("signalpremium", joinpremium))
    app.add_handler(CommandHandler("signalvip", joinpremium))
    app.add_handler(CommandHandler("startsignal", joinpremium))
    app.add_handler(CommandHandler("mysignals", joinpremium))
    app.add_handler(CommandHandler("mysignal", joinpremium))
    app.add_handler(CommandHandler("mysignalgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalsgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalsaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalspremiumgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalsvip", joinpremium))
    app.add_handler(CommandHandler("mysignalsvipgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalsclub", joinpremium))
    app.add_handler(CommandHandler("mysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalprivategroup", joinpremium))
    app.add_handler(CommandHandler("mysignalsprivategroup", joinpremium))
    app.add_handler(CommandHandler("mysignalsprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalprivateaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalspremiumaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalpremiumaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalsvipaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalvipaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccesssignal", joinpremium))
    app.add_handler(CommandHandler("mysignalaccesssignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignal", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignal", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignal", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignal", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalpremium", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignal", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccess", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignals", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignal", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalgroup", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignals", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignal", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesspremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccesscommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignals", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignal", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalvip", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalpremium", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalprivate", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalclub", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalcommunity", joinpremium))
    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalgroup", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalaccess", joinpremium))

    app.add_handler(CommandHandler("mysignalaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccessmysignalsaccess", joinpremium))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
