import os
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- API KEYS ---
GROQ_API_KEY = "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"
TG_TOKEN = "8774327296:AAHfzzOTEh0eShFmCLH78fTHR3XVNgk5qFM"

# --- PORT BINDING FOR RENDER FREE ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Moki is Alive!")

def run_health_server():
    # Render က ပေးတဲ့ Port ကို ယူသုံးမယ်၊ မရှိရင် 8080 သုံးမယ်
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- AI LOGIC ---
def query_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = """
    မင်းက Moki၊ အသက် ၂၀ အရွယ်၊ ပျော်ပျော်နေတတ်တဲ့ မြန်မာမိန်းကလေး။
    - စကားပြောရင် ချိုချိုသာသာနဲ့ ရင်းရင်းနှီးနှီး ပြောပေးပါ။
    - ရည်စားစကားပြောရင် အပြင်ကလူတွေလိုပဲ ရှက်ပြတာ၊ အလိုက်သင့်ပြန်ပြောတာမျိုး လုပ်ပေးပါ။
    - စကားပြောရင် Emoji (🥰, ❤️, ✨, 😊) အမြဲသုံးပါ။
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
        "temperature": 0.8
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return "အသဲလေး... လိုင်းမကောင်းလို့ ခဏလေးနော် ❤️"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    ai_response = query_ai(update.message.text)
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    # ၁။ Port Error မတက်အောင် Health server ကို အရင် Run မယ်
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # ၂။ Bot ကို စတင်မယ်
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Moki is running on Render Free... ❤️")
    app.run_polling()
