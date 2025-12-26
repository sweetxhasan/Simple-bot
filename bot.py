import os
import requests
import json
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

# Bot Configuration
BOT_TOKEN = "7774816424:AAG4o-aPDsQbDBf5-W7MNIwIbF4zEwcOUKA"

# Custom Keyboard Markup
def get_keyboard():
    return {
        "keyboard": [
            [{"text": "🆘 Help"}, {"text": "ℹ️ About"}],
            [{"text": "🔗 Scrape Title"}, {"text": "📊 Status"}],
            [{"text": "👨‍💻 Developer"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def remove_keyboard():
    return {"remove_keyboard": True}

def send_telegram_message(chat_id, text, reply_markup=None):
    """Send message via Telegram Bot API"""
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
        print(f"Error sending message: {e}")
        return None

def extract_page_title(url):
    """Extract title from webpage"""
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15, verify=True)
        response.raise_for_status()
        
        # Detect encoding
        if response.encoding is None:
            response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to get title in multiple ways
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            if title:
                return title
        
        # Try Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()
            if title:
                return title
        
        # Try Twitter card title
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            title = twitter_title['content'].strip()
            if title:
                return title
        
        # Try h1
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text(strip=True)
            if title and len(title) > 10:  # Avoid short h1s
                return title
        
        return "❌ Title not found on the page"
        
    except requests.exceptions.RequestException as e:
        return f"❌ Failed to fetch URL: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "service": "Telegram Title Scraping Bot",
        "endpoint": "/webhook",
        "instructions": "Set webhook to: https://your-app.vercel.app/webhook"
    })

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Main webhook endpoint for Telegram"""
    if request.method == 'GET':
        return jsonify({"status": "Webhook is ready for POST requests"})
    
    try:
        data = request.get_json()
        print("Received data:", json.dumps(data, indent=2)[:500])
        
        if not data:
            return jsonify({"status": "no data received"}), 400
        
        # Check if it's a message or callback query
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            username = message['chat'].get('username', 'User')
            
            print(f"Message from {username} ({chat_id}): {text}")
            
            # Handle /start command
            if text == '/start':
                welcome_msg = f"""👋 <b>Hello {username}!</b>

🤖 <b>Welcome to Title Scraping Bot</b>

📌 <b>I can extract titles from any webpage!</b>

🔗 <b>Just send me:</b>
• Any URL (https://example.com)
• Any webpage link
• Any website address

⚡ <b>Features:</b>
• Instant title extraction
• Custom keyboard
• Fast & reliable
• Free forever

📱 <b>Use buttons below or type /help</b>"""
                
                send_telegram_message(chat_id, welcome_msg, get_keyboard())
            
            # Handle /help command
            elif text == '/help':
                help_msg = """🆘 <b>Help & Instructions</b>

📌 <b>How to use:</b>
1. Send any URL (http/https)
2. I'll extract the page title
3. Get instant results

🔗 <b>Example URLs:</b>
• https://www.google.com
• https://github.com
• https://www.wikipedia.org

📋 <b>Commands:</b>
/start - Start bot
/help - This help message
/about - About bot
/scrape - Enter scrape mode
/status - Check bot status

❓ <b>Need help?</b> Contact developer"""
                
                send_telegram_message(chat_id, help_msg, get_keyboard())
            
            # Handle /about command
            elif text == '/about':
                about_msg = """ℹ️ <b>About This Bot</b>

🤖 <b>Title Scraping Bot</b>
Version: 2.0.0
Platform: Python + Flask
Host: Vercel

✨ <b>Features:</b>
• Web scraping
• Title extraction
• User-friendly interface
• Fast response

👨‍💻 <b>Developer:</b> @yourusername
🔧 <b>Framework:</b> Flask, BeautifulSoup4

⭐ <b>Enjoy using the bot!</b>"""
                
                send_telegram_message(chat_id, about_msg, get_keyboard())
            
            # Handle /scrape command
            elif text == '/scrape':
                send_telegram_message(chat_id, 
                    "🔗 <b>Scrape Mode Activated!</b>\n\nSend me any URL now...",
                    remove_keyboard())
            
            # Handle /status command
            elif text == '/status':
                send_telegram_message(chat_id,
                    "🟢 <b>Bot Status: ONLINE</b>\n\n✅ All systems operational\n⚡ Performance: Excellent\n📊 Requests: Active",
                    get_keyboard())
            
            # Handle keyboard button: Help
            elif text == '🆘 Help':
                send_telegram_message(chat_id,
                    "📚 <b>Need help?</b>\n\nSend any URL or use /help command",
                    get_keyboard())
            
            # Handle keyboard button: About
            elif text == 'ℹ️ About':
                send_telegram_message(chat_id,
                    "🤖 <b>Title Scraping Bot</b>\n\nExtract webpage titles instantly!\nFast • Accurate • Free",
                    get_keyboard())
            
            # Handle keyboard button: Scrape Title
            elif text == '🔗 Scrape Title':
                send_telegram_message(chat_id,
                    "✅ <b>Ready to scrape!</b>\n\nSend me any URL starting with http:// or https://",
                    remove_keyboard())
            
            # Handle keyboard button: Status
            elif text == '📊 Status':
                send_telegram_message(chat_id,
                    "🟢 <b>Bot is running perfectly!</b>\n\nServer: Vercel\nStatus: Active\nUptime: 100%",
                    get_keyboard())
            
            # Handle keyboard button: Developer
            elif text == '👨‍💻 Developer':
                send_telegram_message(chat_id,
                    "👨‍💻 <b>Developer Contact</b>\n\nTelegram: @yourusername\nGitHub: github.com/yourusername\nEmail: your@email.com",
                    get_keyboard())
            
            # Handle URL input
            elif text and (text.startswith('http://') or 
                          text.startswith('https://') or 
                          '://' in text or 
                          '.' in text and len(text) > 5):
                
                # Send typing action
                typing_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction"
                requests.post(typing_url, json={"chat_id": chat_id, "action": "typing"})
                
                send_telegram_message(chat_id, f"🔍 <b>Processing URL...</b>\n<code>{text[:50]}...</code>")
                
                # Extract title
                title = extract_page_title(text)
                
                # Format result
                result_msg = f"""📄 <b>TITLE EXTRACTED</b>

🔗 <b>URL:</b> <code>{text[:100]}</code>

📌 <b>Title:</b> {title}

✅ <b>Successfully extracted!</b>

💡 Send another URL or use buttons below"""
                
                send_telegram_message(chat_id, result_msg, get_keyboard())
            
            # Handle unknown text
            elif text:
                send_telegram_message(chat_id,
                    f"❓ <b>I didn't understand that</b>\n\nYou said: <code>{text}</code>\n\nPlease send a URL (like https://example.com) or use the buttons below:",
                    get_keyboard())
        
        elif 'callback_query' in data:
            # Handle inline keyboard callbacks if any
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            send_telegram_message(chat_id, "ℹ️ This is a callback response", get_keyboard())
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    """Set webhook endpoint"""
    webhook_url = "https://" + request.host + "/webhook"
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        result = response.json()
        
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url,
            "telegram_response": result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/getwebhook', methods=['GET'])
def get_webhook():
    """Get current webhook info"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot",
        "timestamp": "2024",
        "endpoints": {
            "webhook": "/webhook",
            "setwebhook": "/setwebhook",
            "getwebhook": "/getwebhook",
            "health": "/health"
        }
    })

# This is important for Vercel
if __name__ == '__main__':
    app.run(debug=True)
