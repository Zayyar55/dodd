import os
import threading
import requests
import random
from datetime import datetime
import pytz
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, ChatMemberHandler, filters

# --- CONFIGURATION ---
GROQ_API_KEY = "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"
TG_TOKEN = "8774327296:AAHfzzOTEh0eShFmCLH78fTHR3XVNgk5qFM"
BAD_WORDS = ["လီး", "ငါလိုးမသား", "မင်းမေစပ", "စပစား", "စောက်ကောင်", "ယီးပဲ", "မအေလိုး", "ခွေးမသား", "ဖာသယ်"]

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Moki is Ready!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def get_time_context():
    tz = pytz.timezone('Asia/Yangon')
    now = datetime.now(tz)
    hour = now.hour
    if 5 <= hour < 10: return "အခုမှ အိပ်ယာနိုးလို့ လိုင်းတက်တာ။ Morning ပါ အသဲလေးတို့ ☕"
    elif 10 <= hour < 17: return "တစ်ယောက်ထဲ ပျင်းလို့ လိုင်းသုံးနေတာ။ 🌻"
    elif 17 <= hour < 22: return "TikTok ကြည့်နေတာ။ 📱"
    else: return "ညဉ့်နက်နေပြီလေ၊ အိပ်တော့မလို့။ 😴"

def query_ai(text):
    time_info = get_time_context()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # AI ကို ပိုပြီး တည်တည်ငြိမ်ငြိမ်နဲ့ မေးခွန်းအရင်ဖြေခိုင်းတဲ့ Prompt
    system_prompt = f"""
    မင်းက Moki၊ လူမှုရေးနားလည်တဲ့ Channel Admin မိန်းကလေး။ 
    - အဓိကတာဝန်က User မေးတာကို အရင်ဆုံး တိုတိုနဲ့ မှန်မှန်ကန်ကန် ဖြေပေးဖို့ဖြစ်တယ်။
    - နေကောင်းလားမေးရင် 'ကောင်းပါတယ်ရှင်' လို့ပဲ ဖြေပါ။
    - ဘာလုပ်နေလဲမေးရင် အချိန်အလိုက်ဖြေ: {time_info}
    - စကားပြောရင် Emoji လေးတွေ (✨, ❤️, 😊) ကို စာသားနဲ့ လိုက်ဖက်အောင် ထည့်သုံးပါ။
    - User ရဲ့ စကားအပေါ် မူတည်ပြီး အလိုက်သင့် ဖြေပါ။ ကိုယ်ပြောချင်တာကြီးပဲ လျှောက်မပြောပါနဲ့။
    - Movie/Music ရှာခိုင်းရင် 'ရှာပေးမယ်နော်' လို့ ပြောပါ။
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "နေကောင်းလား"},
            {"role": "assistant", "content": "ကောင်းပါတယ်ရှင် ✨ စိတ်တော့ နည်းနည်းညစ်နေတာ ❤️"},
            {"role": "user", "content": text}
        ],
        "temperature": 0.6 # ဉာဏ်နည်းနည်း ပိုကောင်းအောင် လျှော့ထားတယ်
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except: return "လိုင်းမကောင်းလို့ ခဏလေးနော် ❤️"

async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # လူသစ်ဝင်လာမှပဲ နှုတ်ဆက်မယ်
    if update.chat_member.new_chat_member and update.chat_member.new_chat_member.status == "member":
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="အချောလေးတစ်ယောက် ရောက်နေတယ်နော် ✨ အေးဆေးကြည့်သွားပါဦးရှင် ❤️"
        )

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # ၁။ ဆဲစာ စစ်မယ် (တွေ့ရင် ချက်ချင်းဖျက်မယ်)
    if any(word in user_text for word in BAD_WORDS):
        await update.message.delete()
        await context.bot.send_message(chat_id=chat_id, text="အပြောအဆို ဆင်ခြင်ပေးပါနော် ✨")
        return

    # ၂။ Link စစ်မယ်
    if "http" in user_text or "t.me/" in user_text:
        await context.bot.send_message(chat_id=chat_id, text="Link လာချသွားတယ်နော် ⚠️ Owner ကြည့်ပြီးမှ ဆုံးဖြတ်ပါလိမ့်မယ် ✨")
        return

    # ၃။ Invite လုပ်ဖို့ နှိုးဆော်ခြင်း
    if "လူခေါ်" in user_text or "invite" in user_text.lower():
        await update.message.reply_text("သူငယ်ချင်းတွေကို Invite လုပ်ပေးကြဦးနော် ❤️ ✨")
        return

    # ၄။ AI စကားပြန်ခြင်း (ဒီအပိုင်းက မေးတာကိုပဲ အဓိကထား ဖြေမှာပါ)
    ai_response = query_ai(user_text)
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(ChatMemberHandler(welcome_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_all_messages))
    app.run_polling()
