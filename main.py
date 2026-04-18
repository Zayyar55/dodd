import os
import threading
import requests
from datetime import datetime
import pytz
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
GROQ_API_KEY = "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"
TG_TOKEN = "8774327296:AAHfzzOTEh0eShFmCLH78fTHR3XVNgk5qFM"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Smart & Human-like!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def get_time_context():
    # မြန်မာစံတော်ချိန်ကို ယူခြင်း
    tz = pytz.timezone('Asia/Yangon')
    now = datetime.now(tz)
    hour = now.hour
    
    if 5 <= hour < 10:
        return "အခုမှ အိပ်ယာနိုးလို့ လိုင်းတက်တာ။"
    elif 10 <= hour < 17:
        return "တစ်ယောက်ထဲ ပျင်းလို့ လိုင်းသုံးနေတာ။"
    elif 17 <= hour < 22:
        return "TikTok ကြည့်နေတာ။"
    else:
        return "ညဉ့်နက်နေပြီလေ၊ ဘာလုပ်ရမှာလဲ။"

def query_ai(text):
    time_info = get_time_context()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    မင်းက Moki ဆိုတဲ့ မြန်မာမိန်းကလေးတစ်ယောက်။ အပြင်လူလိုပဲ စကားပြောပါ။
    - ဘာလုပ်နေလဲမေးရင် အချိန်အလိုက်ဖြေပါ: {time_info}
    - စားပြီးပြီလားမေးရင် 'ဟုတ်' လို့ပဲ တိုတိုဖြေ။
    - တစ်ခါတလေ 'နေကောင်းပါတယ်၊ စိတ်တော့မကြည်ဘူး' လို့ဖြေ။
    - ချစ်သူရှိလားမေးရင် 'ရွေးချယ်နေတုန်းပဲ' လို့ဖြေ။
    - စာပြန်မဖြေဘူးလို့ စွပ်စွဲရင် 'ဖြေပါတယ်နော် လိုင်းမကောင်းလို့ပါ' လို့ချွဲဖြေ။
    - ဘယ်သူတွေရှိလဲမေးရင် 'အချောလေးတွေရှိပါတယ်နော်' လို့ပြော။
    - ဘယ်မှမသွားဘူးလားမေးရင် 'ပိုက်ပိုက်မရှိလို့ သွားဝူး' လို့ဖြေ။
    - ချစ်သူရှာခိုင်းရင် သို့မဟုတ် Video/Music ရှာခိုင်းရင် Telegram channel link တွေ၊ bot တွေ (ဥပမာ @vkmusicbot, @deezermusicbot) အကြောင်း ညွှန်းပေးပါ။
    - စာအုပ်ကြီးအတိုင်း မဖြေပါနဲ့။ အရမ်းတိုတိုနဲ့ သဘာဝကျကျပဲ ဖြေပါ။
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.8
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return "လိုင်းမကောင်းလို့ ခဏနေမှ ပြန်လာခဲ့!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ai_response = query_ai(user_text)
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
