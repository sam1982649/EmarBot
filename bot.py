import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ============================================================
# ⚙️ الإعدادات الأساسية
# ============================================================
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ✅ اسم المستخدم الخاص بك (تم وضعه هنا)
MY_PERSONAL_USERNAME = "Samer_H_Ibrahim" 

# ============================================================
# 🎨 القوائم والأزرار
# ============================================================
def main_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("🎒 الصف السادس", callback_data="grade_6"),
        InlineKeyboardButton("📘 الصف السابع", callback_data="grade_7"),
        InlineKeyboardButton("📗 الصف الثامن", callback_data="grade_8"),
        InlineKeyboardButton("📙 الصف التاسع", callback_data="grade_9"),
    )
    m.add(InlineKeyboardButton("📞 تواصل مع المطور", url=f"https://t.me/{MY_PERSONAL_USERNAME}"))
    m.add(InlineKeyboardButton("🔑 معلومات التفعيل", callback_data="activate_info"))
    m.add(InlineKeyboardButton("📤 شارك البوت", callback_data="share_bot"))
    return m

def grade_menu(grade):
    m = InlineKeyboardMarkup(row_width=1)
    
    # روابط التحميل
    if grade in ["7", "8", "9"]:
        app_url = "https://t.me/EmarApp/102"
    elif grade == "6":
        app_url = "https://t.me/EmarApp/79"
    else:
        app_url = "https://t.me/EmarApp"
        
    m.add(InlineKeyboardButton("📥 تحميل التطبيق", url=app_url))
    
    # ✅ إضافة الأزرار الخاصة بكل صف
    if grade == "6":
        m.add(InlineKeyboardButton("📝 اختبارات (مذاكرة فصل أول)", url="https://t.me/EmarApp/129"))
    elif grade == "7":
        m.add(InlineKeyboardButton("📚 مواضيع الكتابة", url="https://t.me/EmarApp/123"))
    elif grade == "8":
        m.add(InlineKeyboardButton("📚 مواضيع الكتابة", url="https://t.me/EmarApp/124"))
    elif grade == "9":
        m.add(InlineKeyboardButton("📄 أوراق عمل (Unit 1,2,3)", url="https://t.me/EmarApp/128"))
        m.add(InlineKeyboardButton("🎧 ملفات الاستماع", callback_data="listen_9"))
    
    # زر التفعيل
    m.add(InlineKeyboardButton("🔑 التفعيل والاشتراك", callback_data="activate_info"))
    
    # زر العودة
    m.add(InlineKeyboardButton("🔙 العودة للقائمة", callback_data="main_menu"))
    return m

# ============================================================
# 🚀 أوامر البداية
# ============================================================
@bot.message_handler(commands=['start', 'main_menu'])
def cmd_start(message):
    text = (
        "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n"
        "📚 هذا البوت مخصص لتسهيل وصول الطلاب إلى تطبيق اللغة الإنجليزية.\n\n"
        "👇 <b>الرجاء اختيار الصف الدراسي:</b>"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode='HTML')

# ============================================================
# 🎯 معالجة الأزرار
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    data = call.data

    def safe_edit(text, markup):
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='HTML')
        except Exception:
            bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='HTML')

    # ===== القائمة الرئيسية =====
    if data == "main_menu":
        text = (
            "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n"
            "📚 هذا البوت مخصص لتسهيل وصول الطلاب إلى تطبيق اللغة الإنجليزية.\n\n"
            "👇 <b>الرجاء اختيار الصف الدراسي:</b>"
        )
        safe_edit(text, main_menu())

    # ===== اختيار الصف =====
    elif data.startswith("grade_"):
        grade = data.split("_")[1]
        grade_names = {"6": "السادس", "7": "السابع", "8": "الثامن", "9": "التاسع"}
        text = f"🎓 لقد اخترت <b>الصف {grade_names.get(grade, '')}</b>.\n\n👇 <b>اختر ما تريد:</b>"
        safe_edit(text, grade_menu(grade))

    # ===== معلومات التفعيل =====
    elif data == "activate_info":
        activation_text = (
            "أهلاً وسهلاً بك 🌟\n\n"
            "كل صف يفتح وحدتين مجانيتين. 🎁\n\n"
            "🔑 <b>التفعيل:</b>\n"
            "• كل صف بـ 1500 ليرة جديدة.\n"
            "• الدفع عبر شام كاش.\n"
            "• يعمل التفعيل لمدة سنة كاملة.\n"
            "• يمكن تفعيل صف واحد أو أكثر.\n\n"
            "📚 <b>الصفوف المتوفرة حالياً:</b>\n"
            "سادس، سابع، ثامن، تاسع.\n\n"
            "🚧 <i>يجري العمل على بقية الصفوف قريباً.</i>"
        )
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("📞 تواصل معي للتفعيل", url=f"https://t.me/{MY_PERSONAL_USERNAME}"))
        m.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit(activation_text, m)

    # ===== زر المشاركة =====
    elif data == "share_bot":
        url = "https://t.me/share/url?url=https://t.me/Emar_English_App_bot&text=انضم لبوت إيمار!"
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("📤 مشاركة", url=url))
        m.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit("📤 <b>شارك البوت مع أصدقائك:</b>", m)

    # ===== قسم الاستماع للصف التاسع =====
    elif data == "listen_9":
        m = InlineKeyboardMarkup(row_width=1)
        m.add(
            InlineKeyboardButton("📘 استماع - كتاب الطالب", url="https://t.me/EmarApp/121"),
            InlineKeyboardButton("📗 استماع - كتاب النشاط", url="https://t.me/EmarApp/122"),
            InlineKeyboardButton("🔙 العودة", callback_data="grade_9")
        )
        safe_edit("🎧 <b>ملفات الاستماع للصف التاسع</b>\n\n👇 <b>اختر الكتاب:</b>", m)

# ============================================================
# 💬 الردود التلقائية (الرسائل النصية)
# ============================================================
@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    text = (message.text or "").lower()
    
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    if "تحميل" in text or "حمل" in text or "تطبيق" in text:
        m = InlineKeyboardMarkup(row_width=2)
        m.add(
            InlineKeyboardButton("📥 تطبيق (6)", url="https://t.me/EmarApp/79"),
            InlineKeyboardButton("📥 تطبيق (7-8-9)", url="https://t.me/EmarApp/102"),
        )
        bot.send_message(message.chat.id, "📥 <b>لتحميل التطبيق:</b>", reply_markup=m, parse_mode='HTML')
        
    elif "تفعيل" in text or "فعل" in text or "اشتراك" in text:
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("📞 تواصل معي للتفعيل", url=f"https://t.me/{MY_PERSONAL_USERNAME}"))
        bot.send_message(
            message.chat.id,
            "🔑 <b>التفعيل:</b>\n\n💰 1500 ليرة/صف\n💳 شام كاش\n\nاضغط على الزر أدناه للتواصل معي:",
            reply_markup=m, parse_mode='HTML'
        )
        
    else:
        bot.send_message(
            message.chat.id,
            "🌟 أهلاً بك!\n\nيرجى استخدام الأزرار أدناه للتنقل، أو كتابة كلمة (تحميل) أو (تفعيل) للمساعدة.",
            reply_markup=main_menu(), parse_mode='HTML'
        )

# ============================================================
# 🌐 خادم ويب لإبقاء Render مستيقظاً
# ============================================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    def log_message(self, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ============================================================
# 🚀 التشغيل
# ============================================================
if __name__ == "__main__":
    print("✅ البوت يعمل — الإصدار المحدث مع الروابط")
    bot.infinity_polling()
