import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive and running on Render!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands:\n/start - Check if bot is running\n/help - Help info")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # ✅ Use polling without closing Render's loop
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(app.initialize())
    loop.create_task(app.start())
    print("✅ Bot started successfully and running in background...")

    loop.run_forever()


if __name__ == "__main__":
    main()
