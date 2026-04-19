import os
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- API KEYS ---
GROQ_API_KEY = "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"
TG_TOKEN = "8774327296:AAHfzzOTEh0eShFmCLH78fTHR3XVNgk5qFM"

# --- RENDER PORT FIX ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Moki is Ready!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- AI CHAT LOGIC ---
def query_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # စရိုက်ကို ပိုပြီး သဘာဝကျအောင် ပြင်ထားပါတယ်
    system_prompt = """
    မင်းက Moki၊ အသက် ၂၀ အရွယ် မြန်မာမလေး။ 
    - စကားပြောရင် အပြင်က လူတွေပြောသလိုပဲ တိုတိုနဲ့ ရင်းရင်းနှီးနှီး ပြောပါ။
    - စာသားတွေ အရှည်ကြီး မဖြေပါနဲ့။ တစ်ခါပြန်ရင် စာကြောင်း ၂ ကြောင်း၊ ၃ ကြောင်းထက် မပိုပါစေနဲ့။
    - ရည်စားစကားပြောရင် ရှက်ပြပါ၊ အလိုက်သင့်လေး ပြန်ချွဲပါ။
    - "အသဲ"၊ "မောင်"၊ "နင်" စတဲ့ စကားလုံးတွေကို သဘာဝကျကျ သုံးပါ။
    - စကားပြောတိုင်း Emoji (🥰, ❤️, ✨, 😊) လေးတွေ တစ်ခု နှစ်ခုပဲ သုံးပါ။
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
        return "အသဲလေး... လိုင်းခဏကျသွားလို့နော် ❤️"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    # AI ဆီက အဖြေတောင်းပြီး တိုက်ရိုက်ပြန်ဖြေမယ်
    ai_response = query_ai(update.message.text)
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    # Port Error မတက်အောင် server run မယ်
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # Bot စတင်မယ်
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Moki is Live! ❤️")
    app.run_polling()
