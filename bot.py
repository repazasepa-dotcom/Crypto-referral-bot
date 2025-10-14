import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ----------------------------
# 🔹 BOT COMMANDS
# ----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to the *Premium Signals Bot* 🚀\n\n"
        "🔥 Send /joinpremium to become a member.\n"
        "💸 Invite friends using your referral link:\n"
        f"`https://t.me/{context.bot.username}?start={user.id}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def joinpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = "0xC6219FFBA27247937A63963E4779e33F7930d497"
    msg = (
        "💎 *Join Premium Membership (50 USDT)* 💎\n\n"
        "Send *50 USDT (BEP-20)* to this address:\n"
        f"`{address}`\n\n"
        "Once payment is confirmed, your account will be activated ✅\n\n"
        "🔥 *Benefits* 🔥\n"
        "🚀 Know coins *before pump*\n"
        "🎯 Buy / Sell targets\n"
        "📈 2–5 daily signals\n"
        "🤖 Auto trading by bot\n"
        "⚡ 1–3 special premium signals daily"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def myref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
    await update.message.reply_text(f"🔗 Your referral link:\n{ref_link}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Commands*\n"
        "/start — Begin\n"
        "/joinpremium — Join premium\n"
        "/myref — Get referral link\n"
        "/help — Show this menu",
        parse_mode="Markdown"
    )

# ----------------------------
# 🔹 KEEP-ALIVE WEB SERVER
# ----------------------------

async def handle(request):
    return web.Response(text="✅ Bot is running!")

async def run_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server running on port {port}")

# ----------------------------
# 🔹 MAIN
# ----------------------------

async def main():
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("joinpremium", joinpremium))
    bot_app.add_handler(CommandHandler("myref", myref))
    bot_app.add_handler(CommandHandler("help", help_command))

    # Start both Telegram bot + web server together
    await asyncio.gather(
        run_web_server(),
        bot_app.run_polling(stop_signals=None)
    )

if __name__ == "__main__":
    asyncio.run(main())
