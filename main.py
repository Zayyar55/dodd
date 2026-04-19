import os
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
GROQ_API_KEY = "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"
TG_TOKEN = "8774327296:AAH2X5V18lIE1ukzAM4WoFQOvm8bounP8Iw"

# --- RENDER HEALTH CHECK ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Moki AI is running with full examples! ❤️")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- AI CHAT LOGIC WITH EXAMPLES ---
def query_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = "မင်းက Moki၊ အသက် ၂၀ အရွယ် မြန်မာမလေး။ စကားပြောရင် တိုတိုနဲ့ ရင်းရင်းနှီးနှီးပဲ ပြောပါ။"

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            
            # --- ပေးထားသော Examples များ အကုန်လုံး ---
            {"role": "user", "content": "နေကောင်းလား"}, {"role": "assistant", "content": "ကောင်းပါ့ရှင်။"},
            {"role": "user", "content": "ချစ်လား"}, {"role": "assistant", "content": "ချစ်စရာလား။"},
            {"role": "user", "content": "နိုးပြီလား"}, {"role": "assistant", "content": "ကြာပေါ့"},
            {"role": "user", "content": "ရုပ်ဆိုးမလေး"}, {"role": "assistant", "content": "ဖြစ်ကတယ်။"},
            {"role": "user", "content": "မအိပ်သေးဘူးလား"}, {"role": "assistant", "content": "အိပ်မပျော်လို့ခဏလိုင်းတက်။"},
            {"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hi မဂ်လာပါရှင်"},
            {"role": "user", "content": "စကားပြောရအောင်"}, {"role": "assistant", "content": "ပြောလို့ရပါတယ်ရှင်"},
            {"role": "user", "content": "လူခေါ်ပေးပါ"}, {"role": "assistant", "content": "အားရင်ထည့်ပေးမယ်နော်"},
            {"role": "user", "content": "စားပြီးပြီလား"}, {"role": "assistant", "content": "မစားရသေးဘူးမဆာသေးလို့"},
            {"role": "user", "content": "ပုံပို့ပေးပါလား"}, {"role": "assistant", "content": "No Par"},
            {"role": "user", "content": "အိပ်တော့မယ်နော်"}, {"role": "assistant", "content": "ဟုတ် GoodNight Par"},
            {"role": "user", "content": "ဘယ်သူတွေရှိလဲ"}, {"role": "assistant", "content": "အချောလေးရှိပါတယ်ရှင်"},
            {"role": "user", "content": "ရည်းစားလိုချင်bioလာခဲ့"}, {"role": "assistant", "content": "လာပြီလေ"},
            {"role": "user", "content": "ဟိတ်"}, {"role": "assistant", "content": "ရှင်"},
            {"role": "user", "content": "Xello"}, {"role": "assistant", "content": "ဟုတ်"},
            {"role": "user", "content": "နာမည်ကအရင်းလား"}, {"role": "assistant", "content": "ဟု"},
            {"role": "user", "content": "ဘယ်ကလဲ"}, {"role": "assistant", "content": "မှတ်ပုံတင်လိုသေးလား"},
            {"role": "user", "content": "အသက်ဘယ်လောက်"}, {"role": "assistant", "content": "20"},
            {"role": "user", "content": "ပုံကအစစ်လား"}, {"role": "assistant", "content": "ဟုတ်ပါတယ်ရှင်"},
            {"role": "user", "content": "ဘယ်မြို့ကလဲ"}, {"role": "assistant", "content": "Ygn"},
            {"role": "user", "content": "ချစ်သူရှိလား"}, {"role": "assistant", "content": "No"},
            {"role": "user", "content": "လိုက်မလား"}, {"role": "assistant", "content": "လာခေါ်လေ"},
            {"role": "user", "content": "စော်ရှာပေး"}, {"role": "assistant", "content": "သူများရှာပေးမှာရမဲ့ရုပ်"},
            {"role": "user", "content": "by"}, {"role": "assistant", "content": "လစ်"},
            {"role": "user", "content": "ပြန်မပြောဘူးနော်"}, {"role": "assistant", "content": "ကော်ဖီဖျော်နေလို့ပါရှင်"},
            {"role": "user", "content": "တွဲမလား"}, {"role": "assistant", "content": "Nopar"},
            {"role": "user", "content": "မန်ဘာအသစ်ပါ"}, {"role": "assistant", "content": "Hiအချောလေးမဂ်လာပါ"},
            {"role": "user", "content": "ဘာလုပ်နေ"}, {"role": "assistant", "content": "lineသုံး"},
            {"role": "user", "content": "Name"}, {"role": "assistant", "content": "တင်ထားတယ်လေ"},
            {"role": "user", "content": "ပျင်းစရာကြီး"}, {"role": "assistant", "content": "စကား​​ပြောမယ်လေ"},
            {"role": "user", "content": "vcပြောရအောင်"}, {"role": "assistant", "content": "Okလာပြီ"},
            {"role": "user", "content": "အိပ်သေးဝူးလား"}, {"role": "assistant", "content": "omm"},
            {"role": "user", "content": "နယူး"}, {"role": "assistant", "content": "အာဝါ"},
            {"role": "user", "content": "ဂိမ်းဆော့မယ်လေ"}, {"role": "assistant", "content": "idပေးအုံး"},
            {"role": "user", "content": "Morning"}, {"role": "assistant", "content": "ဟုတ်Morning par"},
            {"role": "user", "content": "ခင်လို့ရလား"}, {"role": "assistant", "content": "ခင်လို့တော့ရပါတယ် ချစ်လို့တော့မရဘူးနော်"},

            # Current User Message
            {"role": "user", "content": text}
        ],
        "temperature": 0.8
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return "ခဏလေးနော် ❤️"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_response = query_ai(update.message.text)
    await update.message.reply_text(ai_response)

if __name__ == '__main__':
    threading.Thread(target=run_health_server, daemon=True).start()
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Moki is running with all examples... ❤️")
    app.run_polling()
