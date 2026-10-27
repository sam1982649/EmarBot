import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import json
import random

# ✅ الآن الكود يقرأ التوكن من إعدادات Render بأمان
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ✅ رابط ملف JSON المباشر (Raw Link)
QUESTIONS_URL = "https://raw.githubusercontent.com/sam1982649/Emar7-8_data/main/grade7/lesson1/grammar.json"

# متغير لحفظ الأسئلة بعد تحميلها (لتجنب تحميلها في كل مرة)
cached_questions = []

def load_questions():
    global cached_questions
    if cached_questions:  # إذا كانت محملة مسبقاً، نستخدمها
        return cached_questions
    
    try:
        req = urllib.request.Request(QUESTIONS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            cached_questions = data.get("questions", [])
            return cached_questions
    except Exception as e:
        print(f"Error loading questions: {e}")
        return []

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
        
        extra_markup = InlineKeyboardMarkup(row_width=2)
        
        if grade_num in ['7', '8', '9']:
            app_url = "https://t.me/EmarApp/102"
        elif grade_num == '6':
            app_url = "https://t.me/EmarApp/79"
        else:
            app_url = "https://t.me/EmarApp"

        if grade_num == '9':
            extra_markup.add(
                InlineKeyboardButton("📘 الشرح", callback_data=f"explain_{grade_num}"),
                InlineKeyboardButton("📚 المفردات", callback_data=f"vocab_{grade_num}"),
                InlineKeyboardButton("📥 تحميل التطبيق", url=app_url),
                InlineKeyboardButton("📝 اختبارات", callback_data=f"extra_{grade_num}_tests"),
                InlineKeyboardButton("📄 أوراق عمل", callback_data=f"extra_{grade_num}_worksheets"),
                InlineKeyboardButton("🎧 استماع", callback_data=f"listen_{grade_num}"), 
                InlineKeyboardButton("📖 الدليل", callback_data=f"extra_{grade_num}_guide"),
                InlineKeyboardButton("📚 المواضيع", callback_data=f"extra_{grade_num}_topics")
            )
        else:
            extra_markup.add(
                InlineKeyboardButton("📘 الشرح", callback_data=f"explain_{grade_num}"),
                InlineKeyboardButton("📚 المفردات", callback_data=f"vocab_{grade_num}"),
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
    # 2. قسم الاستماع للصف التاسع (قائمة فرعية)
    # ==========================================
    elif call.data.startswith('listen_'):
        grade = call.data.split('_')[1]
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📘 استماع - كتاب الطالب", url="https://t.me/EmarApp/121"),
            InlineKeyboardButton("📗 استماع - كتاب النشاط", url="https://t.me/EmarApp/122")
        )
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
        
        text = f"🎧 <b>الصف {grade} - ملفات الاستماع</b>\n\n👇 <b>اختر الكتاب:</b>"
        edit_message(text, markup)

    # ==========================================
    # 3. الأقسام (اختبارات، شرح، الخ)
    # ==========================================
    elif call.data.startswith('extra_') or call.data.startswith('explain_') or call.data.startswith('vocab_'):
        parts = call.data.split('_')
        action = parts[0]
        grade = parts[1]
        
        if action == 'extra':
            extra_type = parts[2]
            if extra_type == 'tests':
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(InlineKeyboardButton("🚀 ابدأ الاختبار التفاعلي", callback_data="start_quiz_0"))
                markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
                text = f"📝 <b>الصف {grade} - الاختبارات</b>\n\n👇 <b>اضغط لبدء الاختبار:</b>"
                edit_message(text, markup)
                return
            
            type_names = {
                "worksheets": "أوراق عمل 📄",
                "listening": "الاستماع 🎧",
                "guide": "الدليل 📖",
                "topics": "المواضيع 📚"
            }
            bot.answer_callback_query(call.id, "⚠️ لم يتم رفع ملفات هذا القسم بعد.", show_alert=True)
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
            text = f"📚 <b>الصف {grade} - {type_names.get(extra_type, '')}</b>\n\n⚠️ <b>ملاحظة:</b> لم يتم رفع ملفات هذا القسم بعد."
            edit_message(text, markup)

        elif action == 'explain':
            bot.answer_callback_query(call.id, "⚠️ لم يتم رفع ملفات الشرح بعد.", show_alert=True)
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
            text = f"📘 <b>الصف {grade} - الشرح</b>\n\n⚠️ <b>ملاحظة:</b> لم يتم رفع ملفات الشرح بعد."
            edit_message(text, markup)

        elif action == 'vocab':
            bot.answer_callback_query(call.id, "⚠️ لم يتم رفع ملفات المفردات بعد.", show_alert=True)
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
            text = f"📚 <b>الصف {grade} - المفردات</b>\n\n⚠️ <b>ملاحظة:</b> لم يتم رفع ملفات المفردات بعد."
            edit_message(text, markup)

    # ==========================================
    # 4. منطق الاختبار التفاعلي (الخلط الآمن لكل طالب)
    # ==========================================
    elif call.data.startswith('start_quiz_'):
        q_index = int(call.data.split('_')[2])
        
        questions = load_questions()
        
        if not questions:
            bot.answer_callback_query(call.id, "⚠️ عذراً، لم نتمكن من تحميل الأسئلة. يرجى المحاولة لاحقاً.", show_alert=True)
            return
            
        if q_index >= len(questions):
            edit_message("🎉 <b>مبروك! لقد أكملت الاختبار بنجاح.</b>", None)
            return

        q = questions[q_index]
        markup = InlineKeyboardMarkup(row_width=2)
        
        # ✅ الخلط العشوائي للعرض فقط
        shuffled_indices = list(range(len(q["o"])))
        random.shuffle(shuffled_indices)
        
        for display_idx, original_idx in enumerate(shuffled_indices):
            letter = chr(97 + display_idx)
            option_text = q["o"][original_idx]
            # نرسل رقم الخيار الأصلي في الـ callback_data لكي نتحقق منه لاحقاً
            markup.add(InlineKeyboardButton(f"{letter}. {option_text}", callback_data=f"ans_{q_index}_{original_idx}"))

        text = f"❓ <b>السؤال {q_index + 1}:</b>\n\n{q['q']}"
        edit_message(text, markup)

    elif call.data.startswith('ans_'):
        parts = call.data.split('_')
        q_index = int(parts[1])
        selected_original_index = int(parts[2]) # هذا هو الخيار الأصلي (0,1,2,3)
        
        questions = load_questions()
        q = questions[q_index]
        
        # ✅ التحقق من الإجابة
        if selected_original_index == q["c"]:
            # إجابة صحيحة
            bot.answer_callback_query(call.id, "✅ إجابة صحيحة!", show_alert=True)
            explanation = q.get("exp", "إجابة صحيحة!")
        else:
            # إجابة خاطئة
            bot.answer_callback_query(call.id, "❌ إجابة خاطئة.", show_alert=True)
            correct_text = q["o"][q["c"]]
            explanation = f"❌ إجابة خاطئة.\n\n✅ الإجابة الصحيحة هي: <b>{correct_text}</b>\n\n{q.get('exp', '')}"

        # ✅ في كلتا الحالتين، ننتقل للسؤال التالي
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            pass

        next_q_index = q_index + 1
        if next_q_index >= len(questions):
             bot.send_message(
                chat_id=call.message.chat.id, 
                text=f"{explanation}\n\n🎉 <b>مبروك! لقد أكملت جميع الأسئلة.</b>", 
                parse_mode='HTML'
            )
        else:
            next_q = questions[next_q_index]
            markup = InlineKeyboardMarkup(row_width=2)
            
            # ✅ خلط خيارات السؤال التالي
            next_shuffled = list(range(len(next_q["o"])))
            random.shuffle(next_shuffled)
            
            for display_idx, original_idx in enumerate(next_shuffled):
                letter = chr(97 + display_idx)
                option_text = next_q["o"][original_idx]
                markup.add(InlineKeyboardButton(f"{letter}. {option_text}", callback_data=f"ans_{next_q_index}_{original_idx}"))
            
            text = f"{explanation}\n\n❓ <b>السؤال {next_q_index + 1}:</b>\n\n{next_q['q']}"
            bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=markup, parse_mode='HTML')

    # ==========================================
    # 5. الأزرار الفارغة
    # ==========================================
    elif call.data.startswith('nofile_') or call.data.startswith('lesson_'):
        bot.answer_callback_query(call.id, "⚠️ عذراً، لم يتم رفع هذا الملف بعد. سيتم إضافته قريباً!", show_alert=True)

# ==========================================
# 6. الرد التلقائي على استفسارات الطلاب
# ==========================================
@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    text = message.text.lower()
    
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass 
    
    if "تحميل" in text or "حمل" in text or "نزل" in text or "تطبيق" in text:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📥 تطبيق (6)", url="https://t.me/EmarApp/79"),
            InlineKeyboardButton("📥 تطبيق (7-8-9)", url="https://t.me/EmarApp/102")
        )
        bot.send_message(message.chat.id, 
            "📥 <b>لتحميل التطبيق:</b>\n\n"
            "يرجى اختيار التطبيق الخاص بصفك من الأزرار أدناه:\n\n"
            "• زر <b>(6)</b> مخصص للصف السادس.\n"
            "• زر <b>(7-8-9)</b> مخصص للصفوف السابع والثامن والتاسع.", 
            reply_markup=markup, parse_mode='HTML')
    
    elif "تفعيل" in text or "فعل" in text or "مفعل" in text:
        activation_text = (
            "🔑 <b>طريقة تفعيل التطبيق:</b>\n\n"
            "1️⃣ اذهب إلى صفحة التفعيل في التطبيق.\n"
            "2️⃣ انسخ <b>رقم المعرف (ID)</b> الخاص بك.\n"
            "3️⃣ تواصل مع المطور عبر رقم الهاتف الموجود في صفحة التفعيل، وأرسل له رقم المعرف.\n\n"
            "💰 <b>سعر التفعيل:</b> 1500 ليرة جديدة لكل صف.\n"
            "💳 <b>طريقة الدفع:</b> شام كاش."
        )
        bot.send_message(message.chat.id, activation_text, parse_mode='HTML')

    elif "كيف" in text and ("اشتغل" in text or "يعمل" in text):
         bot.send_message(message.chat.id, "💡 <b>لبدء استخدام البوت:</b>\n\nاضغط على زر /start أو اكتب /main_menu لاختيار الصف الدراسي الخاص بك.", parse_mode='HTML')

    else:
        bot.send_message(message.chat.id, "أهلاً وسهلاً بك 🌟\n\nسنرد عليك بأقرب فرصة ممكنة. يرجى الانتظار قليلاً.", parse_mode='HTML')

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
