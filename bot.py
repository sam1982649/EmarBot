import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ✅ الآن الكود يقرأ التوكن من إعدادات Render بأمان
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'main_menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🎒 الصف الرابع", callback_data="grade_4"),
        InlineKeyboardButton("🎒 الصف الخامس", callback_data="grade_5"),
        InlineKeyboardButton("🎒 الصف السادس", callback_data="grade_6"),
        InlineKeyboardButton("📘 الصف السابع", callback_data="grade_7"),
        InlineKeyboardButton("📗 الصف الثامن", callback_data="grade_8"),
        InlineKeyboardButton("📙 الصف التاسع", callback_data="grade_9"),
        InlineKeyboardButton("🎓 الصف العاشر", callback_data="grade_10"),
        InlineKeyboardButton("🎓 الحادي عشر", callback_data="grade_11"),
        InlineKeyboardButton("🏆 بكالوريا", callback_data="grade_12")
    ]
    markup.add(*buttons) 
    markup.add(InlineKeyboardButton("🔑 تفعيل التطبيق", callback_data="activate_info"))
    markup.add(InlineKeyboardButton("ℹ️ معلومات حول البوت", callback_data="about_bot"))

    welcome_text = (
        "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n"
        "📚 هذا البوت مخصص لتوفير ملفات الدراسة بضغطة زر.\n\n"
        "👇 <b>الرجاء اختيار الصف الدراسي الخاص بك:</b>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    bot.answer_callback_query(call.id)

    # ✅ دالة مساعدة لتعديل الرسالة الحالية فوراً (أسرع طريقة)
    def edit_message(text, markup):
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                text=text, 
                reply_markup=markup, 
                parse_mode='HTML'
            )
        except Exception:
            bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=markup, parse_mode='HTML')

    if call.data == 'main_menu':
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [
            InlineKeyboardButton("🎒 الصف الرابع", callback_data="grade_4"),
            InlineKeyboardButton("🎒 الصف الخامس", callback_data="grade_5"),
            InlineKeyboardButton("🎒 الصف السادس", callback_data="grade_6"),
            InlineKeyboardButton("📘 الصف السابع", callback_data="grade_7"),
            InlineKeyboardButton("📗 الصف الثامن", callback_data="grade_8"),
            InlineKeyboardButton("📙 الصف التاسع", callback_data="grade_9"),
            InlineKeyboardButton("🎓 الصف العاشر", callback_data="grade_10"),
            InlineKeyboardButton("🎓 الحادي عشر", callback_data="grade_11"),
            InlineKeyboardButton("🏆 بكالوريا", callback_data="grade_12")
        ]
        markup.add(*buttons) 
        markup.add(InlineKeyboardButton("🔑 تفعيل التطبيق", callback_data="activate_info"))
        markup.add(InlineKeyboardButton("ℹ️ معلومات حول البوت", callback_data="about_bot"))
        
        welcome_text = "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n📚 هذا البوت مخصص لتوفير ملفات الدراسة بضغطة زر.\n\n👇 <b>الرجاء اختيار الصف الدراسي الخاص بك:</b>"
        edit_message(welcome_text, markup)
        
    elif call.data == 'activate_info':
        activation_text = (
            "🔑 <b>معلومات تفعيل التطبيق</b>\n\n"
            "🎁 التطبيق <b>مجاني بشكل كامل</b> لأول درسين (Unit 1 & 2).\n"
            "🔒 بقية الدروس تحتاج إلى تفعيل.\n\n"
            "💰 <b>سعر التفعيل:</b> 1500 ليرة جديدة لكل صف.\n"
            "📚 يمكنك تفعيل صف واحد أو أكثر.\n\n"
            "💳 <b>طريقة الدفع:</b> شام كاش.\n\n"
            "📱 <b>للتفعيل:</b>\n"
            "1️⃣ اذهب إلى صفحة التفعيل في التطبيق.\n"
            "2️⃣ انسخ <b>رقم المعرف (ID)</b> الخاص بك.\n"
            "3️⃣ تواصل مع المطور عبر رقم الهاتف الموجود في صفحة التفعيل، وأرسل له رقم المعرف."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu"))
        edit_message(activation_text, markup)
        
    elif call.data == 'about_bot':
        text = "👨‍🏫 <b>معلومات حول البوت:</b>\n\nتم تصميم هذا البوت لتسهيل وصول الطلاب إلى ملفات قناة إيمار."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu"))
        edit_message(text, markup)
        
    # ==========================================
    # 1. قائمة الصفوف (الأقسام الإضافية فقط)
    # ==========================================
    elif call.data.startswith('grade_'):
        grade_num = call.data.split('_')[1]
        
        # ✅ تم حذف أزرار الوحدات، والاكتفاء بالأقسام الإضافية
        extra_markup = InlineKeyboardMarkup(row_width=2)
        
        if grade_num in ['7', '8', '9']:
            app_url = "https://t.me/EmarApp/102"
        elif grade_num == '6':
            app_url = "https://t.me/EmarApp/79"
        else:
            app_url = "https://t.me/EmarApp"

        extra_markup.add(
            InlineKeyboardButton("📥 تحميل التطبيق", url=app_url),
            InlineKeyboardButton("📝 اختبارات", callback_data=f"extra_{grade_num}_tests"),
            InlineKeyboardButton("📄 أوراق عمل", callback_data=f"extra_{grade_num}_worksheets"),
            InlineKeyboardButton("🎧 استماع", callback_data=f"extra_{grade_num}_listening"),
            InlineKeyboardButton("📖 الدليل", callback_data=f"extra_{grade_num}_guide"),
            InlineKeyboardButton("📚 المواضيع", callback_data=f"extra_{grade_num}_topics")
        )
        extra_markup.add(InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_menu"))
        
        text = f"🎓 لقد اخترت <b>الصف {grade_num}</b>.\n\n👇 <b>اختر القسم المطلوب:</b>"
        edit_message(text, extra_markup)

    # ==========================================
    # 2. الأقسام الإضافية
    # ==========================================
    elif call.data.startswith('extra_'):
        parts = call.data.split('_')
        grade = parts[1]
        extra_type = parts[2]
        
        type_names = {
            "tests": "الاختبارات 📝",
            "worksheets": "أوراق عمل 📄",
            "listening": "الاستماع 🎧",
            "guide": "الدليل 📖",
            "topics": "المواضيع 📚"
        }
        
        bot.answer_callback_query(call.id, "⚠️ لم يتم رفع ملفات هذا القسم بعد. يرجى المحاولة لاحقاً.", show_alert=True)
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
        
        text = f"📚 <b>الصف {grade} - {type_names[extra_type]}</b>\n\n⚠️ <b>ملاحظة:</b> لم يتم رفع ملفات هذا القسم بعد."
        edit_message(text, markup)

    # ==========================================
    # 3. الأزرار الفارغة (متبقية من الكود القديم)
    # ==========================================
    elif call.data.startswith('nofile_') or call.data.startswith('lesson_'):
        bot.answer_callback_query(call.id, "⚠️ عذراً، لم يتم رفع هذا الملف بعد. سيتم إضافته قريباً!", show_alert=True)

# ✅ كود فتح المنفذ الوهمي لإرضاء Render (لا تحذفه)
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

print("البوت يعمل الآن بانتظار الرسائل...")
bot.infinity_polling()
