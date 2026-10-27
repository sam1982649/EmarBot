import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import json
import random
import re
import string

# ✅ الآن الكود يقرأ التوكن من إعدادات Render بأمان
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ✅ روابط ملفات JSON المباشرة (Raw Links)
GRAMMAR_URL = "https://raw.githubusercontent.com/sam1982649/Emar7-8_data/main/grade7/lesson1/grammar.json"
CONVERT_URL = "https://raw.githubusercontent.com/sam1982649/Emar7-8_data/main/grade7/lesson1/convert_data.json"

# متغيرات لحفظ البيانات بعد تحميلها
cached_grammar = []
cached_convert = []

# قاموس لحفظ أسئلة الاختبار لكل طالب
user_quiz_sessions = {}
# قاموس لحفظ حالة "التحويل" لكل طالب
user_convert_sessions = {}

def load_json_data(url, cache_var_name):
    global_vars = globals()
    if global_vars[cache_var_name]:
        return global_vars[cache_var_name]
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            global_vars[cache_var_name] = data.get("questions", [])
            return global_vars[cache_var_name]
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return []

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_main_menu_markup():
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
    markup.add(InlineKeyboardButton("📤 شارك البوت مع أصدقائك", callback_data="share_bot"))
    markup.add(InlineKeyboardButton("ℹ️ معلومات حول البوت", callback_data="about_bot"))
    return markup

def send_quiz_question(chat_id, q_index):
    if chat_id not in user_quiz_sessions:
        bot.send_message(chat_id, "⚠️ انتهت جلسة الاختبار. يرجى البدء من جديد.")
        return

    user_questions = user_quiz_sessions[chat_id]
    
    if q_index >= len(user_questions):
        bot.send_message(chat_id, "🎉 <b>مبروك! لقد أكملت جميع الأسئلة.</b>", parse_mode='HTML')
        del user_quiz_sessions[chat_id]
        return

    q = user_questions[q_index]
    markup = InlineKeyboardMarkup(row_width=2)
    shuffled_indices = list(range(len(q["o"])))
    random.shuffle(shuffled_indices)
    
    for display_idx, original_idx in enumerate(shuffled_indices):
        letter = chr(97 + display_idx)
        option_text = q["o"][original_idx]
        markup.add(InlineKeyboardButton(f"{letter}. {option_text}", callback_data=f"ans_{q_index}_{original_idx}"))

    text = f"❓ <b>السؤال {q_index + 1}:</b>\n\n{q['q']}"
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

def send_convert_question(chat_id, q_index):
    questions = load_json_data(CONVERT_URL, 'cached_convert')
    if q_index >= len(questions):
        bot.send_message(chat_id, "🎉 <b>مبروك! لقد أكملت جميع أسئلة التحويل.</b>", parse_mode='HTML')
        if chat_id in user_convert_sessions:
            del user_convert_sessions[chat_id]
        return

    user_convert_sessions[chat_id] = q_index
    q = questions[q_index]
    
    text = (
        f"✍️ <b>سؤال التحويل {q_index + 1}:</b>\n\n"
        f"<b>الجملة:</b> {q['original']}\n"
        f"<b>الكلمة المستهدفة:</b> <u>{q['targetWord']}</u>\n\n"
        f"<i>اكتب السؤال المناسب في المحادثة الآن:</i>"
    )
    bot.send_message(chat_id, text, parse_mode='HTML')

@bot.message_handler(commands=['start', 'main_menu'])
def send_welcome(message):
    welcome_text = (
        "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n"
        "📚 هذا البوت مخصص لتوفير ملفات الدراسة بضغطة زر.\n\n"
        "👇 <b>الرجاء اختيار الصف الدراسي الخاص بك:</b>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu_markup(), parse_mode='HTML')

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
        welcome_text = "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n📚 هذا البوت مخصص لتوفير ملفات الدراسة بضغطة زر.\n\n👇 <b>الرجاء اختيار الصف الدراسي الخاص بك:</b>"
        edit_message(welcome_text, get_main_menu_markup())

    # ✅ زر مشاركة البوت
    elif call.data == 'share_bot':
        # هذا الكود يفتح قائمة مشاركة تلغرام
        share_url = f"https://t.me/share/url?url=https://t.me/Emar_English_bot&text=انضم إلى بوت إيمار التعليمي لتعلم اللغة الإنجليزية بسهولة!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 اضغط هنا للمشاركة", url=share_url))
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        
        text = "📤 <b>شارك البوت مع أصدقائك!</b>\n\nاضغط على الزر أدناه لاختيار أصدقائك ومشاركة البوت معهم."
        edit_message(text, markup)
        
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
                InlineKeyboardButton("✍️ تحويل إلى سؤال", callback_data=f"convert_{grade_num}"),
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
                InlineKeyboardButton("✍️ تحويل إلى سؤال", callback_data=f"convert_{grade_num}"),
                InlineKeyboardButton("📄 أوراق عمل", callback_data=f"extra_{grade_num}_worksheets"),
                InlineKeyboardButton("🎧 استماع", callback_data=f"extra_{grade_num}_listening"),
                InlineKeyboardButton("📖 الدليل", callback_data=f"extra_{grade_num}_guide"),
                InlineKeyboardButton("📚 المواضيع", callback_data=f"extra_{grade_num}_topics")
            )
        
        extra_markup.add(InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_menu"))
        text = f"🎓 لقد اخترت <b>الصف {grade_num}</b>.\n\n👇 <b>اختر القسم المطلوب:</b>"
        edit_message(text, extra_markup)

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
            bot.answer_callback_query(call.id, "⚠️ هذا القسم قيد التطوير.", show_alert=True)
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
            text = f"📚 <b>الصف {grade} - {type_names.get(extra_type, '')}</b>\n\n🚧 <b>ملاحظة:</b> هذا القسم قيد التطوير، سيتم إضافته قريباً."
            edit_message(text, markup)

        elif action == 'explain':
            bot.answer_callback_query(call.id, "⚠️ هذا القسم قيد التطوير.", show_alert=True)
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
            text = f"📘 <b>الصف {grade} - الشرح</b>\n\n🚧 <b>ملاحظة:</b> هذا القسم قيد التطوير، سيتم إضافته قريباً."
            edit_message(text, markup)

        elif action == 'vocab':
            bot.answer_callback_query(call.id, "⚠️ هذا القسم قيد التطوير.", show_alert=True)
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
            text = f"📚 <b>الصف {grade} - المفردات</b>\n\n🚧 <b>ملاحظة:</b> هذا القسم قيد التطوير، سيتم إضافته قريباً."
            edit_message(text, markup)

    elif call.data.startswith('convert_'):
        grade = call.data.split('_')[1]
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            pass
        send_convert_question(call.message.chat.id, 0)

    elif call.data.startswith('start_quiz_'):
        q_index = int(call.data.split('_')[2])
        
        if q_index == 0:
            all_questions = load_json_data(GRAMMAR_URL, 'cached_grammar')
            if not all_questions:
                bot.answer_callback_query(call.id, "⚠️ عذراً، لم نتمكن من تحميل الأسئلة. يرجى المحاولة لاحقاً.", show_alert=True)
                return
            
            num_questions = min(10, len(all_questions))
            selected_questions = random.sample(all_questions, num_questions)
            user_quiz_sessions[call.message.chat.id] = selected_questions

        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            pass
        send_quiz_question(call.message.chat.id, q_index)

    elif call.data.startswith('ans_'):
        parts = call.data.split('_')
        q_index = int(parts[1])
        selected_original_index = int(parts[2])
        
        if call.message.chat.id not in user_quiz_sessions:
            bot.answer_callback_query(call.id, "⚠️ انتهت الجلسة. ابدأ من جديد.", show_alert=True)
            return

        user_questions = user_quiz_sessions[call.message.chat.id]
        q = user_questions[q_index]
        
        if selected_original_index == q["c"]:
            bot.answer_callback_query(call.id, "✅ إجابة صحيحة!", show_alert=True)
            explanation = q.get("exp", "إجابة صحيحة!")
        else:
            bot.answer_callback_query(call.id, "❌ إجابة خاطئة.", show_alert=True)
            correct_text = q["o"][q["c"]]
            explanation = f"❌ إجابة خاطئة.\n\n✅ الإجابة الصحيحة هي: <b>{correct_text}</b>\n\n{q.get('exp', '')}"

        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            pass

        next_q_index = q_index + 1
        markup = InlineKeyboardMarkup(row_width=1)
        
        if next_q_index >= len(user_questions):
            bot.send_message(chat_id=call.message.chat.id, text=f"{explanation}\n\n🎉 <b>مبروك! لقد أكملت جميع الأسئلة.</b>", parse_mode='HTML')
        else:
            markup.add(InlineKeyboardButton("➡️ السؤال التالي", callback_data=f"start_quiz_{next_q_index}"))
            bot.send_message(chat_id=call.message.chat.id, text=f"{explanation}", reply_markup=markup, parse_mode='HTML')

    elif call.data.startswith('nofile_') or call.data.startswith('lesson_'):
        bot.answer_callback_query(call.id, "⚠️ عذراً، لم يتم رفع هذا الملف بعد. سيتم إضافته قريباً!", show_alert=True)

@bot.message_handler(func=lambda message: message.chat.id in user_convert_sessions)
def handle_convert_answer(message):
    chat_id = message.chat.id
    q_index = user_convert_sessions[chat_id]
    
    questions = load_json_data(CONVERT_URL, 'cached_convert')
    q = questions[q_index]
    
    user_answer = message.text
    cleaned_user_answer = clean_text(user_answer)
    
    correct_answers = []
    if "correctQuestion" in q:
        correct_answers.append(clean_text(q["correctQuestion"]))
    if "correctQuestions" in q:
        for ans in q["correctQuestions"]:
            correct_answers.append(clean_text(ans))
            
    is_correct = False
    for correct in correct_answers:
        if cleaned_user_answer == correct:
            is_correct = True
            break
            
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    except Exception:
        pass

    if is_correct:
        bot.send_message(chat_id, "✅ <b>إجابة صحيحة! أحسنت.</b>", parse_mode='HTML')
    else:
        correct_text = q.get("correctQuestion", "")
        bot.send_message(chat_id, f"❌ <b>إجابة غير صحيحة.</b>\n\n✅ <b>الإجابة الصحيحة:</b>\n{correct_text}", parse_mode='HTML')

    next_q_index = q_index + 1
    if next_q_index < len(questions):
        send_convert_question(chat_id, next_q_index)
    else:
        bot.send_message(chat_id, "🎉 <b>مبروك! لقد أكملت جميع أسئلة التحويل.</b>", parse_mode='HTML')
        del user_convert_sessions[chat_id]

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
