import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# বটের টোকেন (Render-এ এনভায়রনমেন্ট ভেরিয়েবল হিসেবে সেট করবেন)
TOKEN = os.getenv('BOT_TOKEN', '7774816424:AAG4o-aPDsQbDBf5-W7MNIwIbF4zEwcOUKA')

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যবহারকারী /start কমান্ড দিলে এই বার্তা পাঠাবে"""
    user = update.effective_user
    await update.message.reply_html(
        rf"হ্যালো {user.mention_html()}! আমি একটি ইকো বট। আপনি যা লিখবেন আমি তাই আপনাকে ফিরিয়ে দেব।"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যবহারকারী /help কমান্ড দিলে এই বার্তা পাঠাবে"""
    help_text = (
        "এই বটটি খুবই সহজ:\n"
        "/start - বট শুরু করতে\n"
        "/help - এই সাহায্য বার্তা দেখতে\n\n"
        "আপনি যে কোনও লেখা পাঠালে, বটটি সেটা হুবহু আপনার কাছে ফিরিয়ে দেবে।"
    )
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যবহারকারীর পাঠানো যেকোনো টেক্সট মেসেজ ইকো (প্রতিধ্বনি) করবে"""
    user_message = update.message.text
    logger.info(f"User {update.effective_user.id} wrote: {user_message}")
    
    # ইউজারের মেসেজটি ঠিক যেমন আছে তেমনই ফেরত পাঠানো
    await update.message.reply_text(f"আপনি লিখেছেন:\n{user_message}")

def main():
    """বট শুরু করার প্রধান ফাংশন"""
    # টেলিগ্রাম অ্যাপ্লিকেশন তৈরি করা
    application = Application.builder().token(TOKEN).build()

    # কমান্ড হ্যান্ডলার রেজিস্টার করা
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # টেক্সট মেসেজের জন্য হ্যান্ডলার (ছবি, অডিও ইত্যাদি বাদ)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # বট শুরু করা (Render-এ এটি কাজ করবে)
    port = int(os.environ.get('PORT', 8443))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://your-render-app-name.onrender.com/{TOKEN}"
    )

if __name__ == '__main__':
    main()
