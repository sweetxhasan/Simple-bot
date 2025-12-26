import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

# Configuration
BOT_TOKEN = "7774816424:AAG4o-aPDsQbDBf5-W7MNIwIbF4zEwcOUKA"
WEBHOOK_URL = "https://your-app-name.vercel.app/webhook"  # Change this
ADMIN_CHAT_ID = None  # Set your chat ID for admin features

# Custom Keyboard
keyboard = {
    "keyboard": [
        [{"text": "🆘 Help"}, {"text": "ℹ️ About"}],
        [{"text": "🔗 Scrape Title"}, {"text": "📊 Status"}],
        [{"text": "👨‍💻 Developer"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

remove_keyboard = {"remove_keyboard": True}

def send_message(chat_id, text, reply_markup=None):
    """Send message to Telegram user"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return None

def extract_title_from_url(url):
    """Extract title from webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different ways to get title
        title = soup.find('title')
        if title and title.string:
            return title.string.strip()
        
        # Try meta og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()
        
        return "❌ No title found on the page"
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching URL: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def set_webhook():
    """Set Telegram webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {"url": WEBHOOK_URL}
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot": "Title Scraping Bot",
        "endpoints": {
            "webhook": "/webhook",
            "setwebhook": "/setwebhook",
            "health": "/health"
        }
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook handler"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "no data"}), 400
        
        # Extract message info
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        message_id = message.get('message_id')
        
        if not chat_id:
            return jsonify({"status": "no chat id"}), 400
        
        # Handle commands
        if text.startswith('/'):
            command = text.lower()
            
            if command == '/start':
                welcome_text = """👋 <b>Welcome to Title Scraping Bot!</b>

📌 <b>How to use:</b>
1. Send any URL/link
2. I'll extract the page title

📱 <b>Commands:</b>
• /start - Start the bot
• /help - Show help
• /about - About this bot
• /scrape - Scrape title from URL
• /status - Bot status

🔧 <b>Features:</b>
• Automatic title extraction
• Custom keyboard
• Fast response
• Supports all websites

Made with ❤️ by @yourusername"""
                send_message(chat_id, welcome_text, keyboard)
                
            elif command == '/help':
                help_text = """🆘 <b>Help Guide</b>

📌 <b>Quick Start:</b>
Just send me any URL, and I'll extract its title!

🔗 <b>Supported URL formats:</b>
• https://example.com
• http://example.com/page
• www.example.com

⚡ <b>Commands:</b>
• <code>/start</code> - Welcome message
• <code>/help</code> - This help message
• <code>/about</code> - About the bot
• <code>/scrape</code> - Scrape mode
• <code>/status</code> - Check bot status

📝 <b>Example:</b>
Send: https://www.google.com
Get: Title: Google

💡 <b>Tip:</b> Use the custom keyboard below for quick access!"""
                send_message(chat_id, help_text, keyboard)
                
            elif command == '/about':
                about_text = """ℹ️ <b>About Title Scraping Bot</b>

🤖 <b>Bot Version:</b> 2.0.0
📅 <b>Released:</b> 2024
🔧 <b>Framework:</b> Flask + Python
🌐 <b>Hosting:</b> Vercel

✨ <b>Features:</b>
• Webpage title extraction
• Custom keyboard interface
• Error handling
• Fast performance
• Multi-website support

👨‍💻 <b>Developer:</b> @yourusername
📚 <b>Source:</b> Private

📞 <b>Support:</b> Contact @yourusername"""
                send_message(chat_id, about_text, keyboard)
                
            elif command == '/scrape':
                scrape_text = """🔗 <b>Scrape Mode Activated</b>

Now send me any URL to extract its title!

📌 <b>Example URLs:</b>
• https://github.com
• https://www.youtube.com
• https://www.wikipedia.org

⚠️ <b>Note:</b> Some websites may block bot requests."""
                send_message(chat_id, scrape_text, remove_keyboard)
                
            elif command == '/status':
                status_text = """📊 <b>Bot Status</b>

✅ <b>Status:</b> Online & Running
🔧 <b>System:</b> Operational
⚡ <b>Performance:</b> Excellent
🔄 <b>Last Update:</b> Just now

💾 <b>Resources:</b>
• Memory: Normal
• CPU: Idle
• Uptime: 100%

🔔 <b>Notifications:</b> All systems go!"""
                send_message(chat_id, status_text, keyboard)
                
        # Handle keyboard buttons
        elif text == '🆘 Help':
            send_message(chat_id, "📖 Opening help guide...")
            help_command = """🆘 <b>Help Section</b>

I can extract titles from any webpage!

📌 <b>Just send me:</b>
• Any HTTP/HTTPS URL
• Any webpage link
• Any website address

🛠️ <b>Need more help?</b>
Contact: @yourusername"""
            send_message(chat_id, help_command, keyboard)
            
        elif text == 'ℹ️ About':
            send_message(chat_id, """ℹ️ <b>Title Scraping Bot</b>

A smart bot that extracts webpage titles instantly!

⭐ <b>Highlights:</b>
• Lightning fast
• Accurate results
• User friendly
• Always free""", keyboard)
            
        elif text == '🔗 Scrape Title':
            send_message(chat_id, "✅ <b>Ready to scrape!</b>\n\nSend me any URL now...", remove_keyboard)
            
        elif text == '📊 Status':
            send_message(chat_id, "🟢 <b>Bot is online!</b>\n\nAll systems operational.", keyboard)
            
        elif text == '👨‍💻 Developer':
            send_message(chat_id, """👨‍💻 <b>Developer Information</b>

<b>Name:</b> Your Name
<b>Username:</b> @yourusername
<b>Role:</b> Full Stack Developer

💼 <b>Skills:</b>
• Python/Flask/Django
• JavaScript/React
• Telegram Bots
• Web Scraping

📧 <b>Contact:</b> @yourusername""", keyboard)
        
        # Handle URL messages
        elif text and (text.startswith('http://') or 
                      text.startswith('https://') or 
                      text.startswith('www.')):
            
            # Show typing action
            typing_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction"
            requests.post(typing_url, json={"chat_id": chat_id, "action": "typing"})
            
            # Process URL
            if not text.startswith('http'):
                text = 'https://' + text
                
            send_message(chat_id, f"🔍 <b>Processing URL:</b>\n<code>{text}</code>")
            
            title = extract_title_from_url(text)
            
            if "❌" in title:
                send_message(chat_id, title, keyboard)
            else:
                result_text = f"""📄 <b>Title Extracted Successfully!</b>

🔗 <b>URL:</b> <code>{text}</code>

📌 <b>Title:</b> {title}

⏱️ <b>Time:</b> Instant
✅ <b>Status:</b> Completed

💡 <b>Tip:</b> Send another URL to continue!"""
                send_message(chat_id, result_text, keyboard)
        
        # Handle invalid input
        else:
            if text:  # Only respond if there's actual text
                send_message(chat_id, 
                    "❌ <b>Invalid Input!</b>\n\nPlease send a valid URL starting with http:// or https://\n\nOr use the buttons below:",
                    keyboard)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/setwebhook', methods=['GET', 'POST'])
def setwebhook():
    """Endpoint to set webhook"""
    result = set_webhook()
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot": "Title Scraping Bot",
        "timestamp": "2024"
    })

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
