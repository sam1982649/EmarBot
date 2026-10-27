# ============================================================
# 🤖 بوت إيمار التعليمي — النسخة المحسّنة
# ============================================================
# الصفوف الفعّالة حالياً: 7، 8، 9 (الدرسان 1 و 2)
# الصفوف قيد التطوير: 4، 5، 6، 10، 11، 12
# ============================================================

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

# ============================================================
# ⚙️ الإعدادات الأساسية
# ============================================================

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

BASE_URL = "https://raw.githubusercontent.com/sam1982649/Emar7-8_data/main"

# الصفوف الفعّالة (تعمل بالكامل)
ACTIVE_GRADES = ["7", "8", "9"]

# الصفوف قيد التطوير (تظهر في القائمة لكن لا تعمل)
INACTIVE_GRADES = ["4", "5", "6", "10", "11", "12"]

# أسماء الصفوف
GRADE_NAMES = {
    "4": "الرابع",
    "5": "الخامس",
    "6": "السادس",
    "7": "السابع",
    "8": "الثامن",
    "9": "التاسع",
    "10": "العاشر",
    "11": "الحادي عشر",
    "12": "بكالوريا",
}

# أسماء الدروس (يمكن تعديلها لاحقاً بسهولة)
LESSON_NAMES = {
    "7": {"1": "الدرس 1", "2": "الدرس 2"},
    "8": {"1": "الدرس 1", "2": "الدرس 2"},
    "9": {"1": "الدرس 1", "2": "الدرس 2"},
}

# مسارات المجلدات لكل درس
LESSON_PATHS = {
    "7": {"1": "grade7/lesson1", "2": "grade7/lesson2"},
    "8": {"1": "grade8/lesson1", "2": "grade8/lesson2"},
    "9": {"1": "grade9/lesson1", "2": "grade9/lesson2"},
}

# أنواع الملفات المتاحة
FILE_TYPES = {
    "grammar":           "grammar.json",
    "convert":           "convert_data.json",
    "free_answer":       "free_answer_data.json",
    "explain":           "explain_data.json",
    "match":             "match_data.json",
    "texts":             "texts_data.json",
    "topics":            "topics.json",
}

# ============================================================
# 💾 نظام الكاش الذكي
# ============================================================

_data_cache = {}

def load_json(grade, lesson, file_type):
    """تحميل ملف JSON مع كاش ذكي"""
    key = f"{grade}_{lesson}_{file_type}"
    if key in _data_cache:
        return _data_cache[key]
    
    if file_type not in FILE_TYPES:
        return None
    
    path = LESSON_PATHS.get(grade, {}).get(lesson)
    if not path:
        return None
    
    url = f"{BASE_URL}/{path}/{FILE_TYPES[file_type]}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            _data_cache[key] = data
            return data
    except Exception as e:
        print(f"[خطأ تحميل] {url} → {e}")
        return None

# ============================================================
# 🧹 دوال مساعدة
# ============================================================

def clean_text(text):
    """تنظيف النص للمقارنة"""
    text = text.lower().strip()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def safe_edit_or_send(call, text, markup=None):
    """تعديل رسالة موجودة أو إرسال جديدة عند الفشل"""
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='HTML')

def dev_alert(call, msg="🚧 قيد التطوير"):
    """تنبيه سريع للمستخدم"""
    try:
        bot.answer_callback_query(call.id, msg, show_alert=True)
    except Exception:
        pass

# ============================================================
# 🧠 جلسات المستخدمين
# ============================================================

user_quiz_sessions = {}       # جلسات MCQ
user_convert_sessions = {}    # جلسات التحويل
user_free_sessions = {}       # جلسات الإجابة الحرة
user_match_sessions = {}      # جلسات المطابقة
user_texts_sessions = {}      # جلسات فهم القراءة

# ============================================================
# 🎨 القوائم الرئيسية
# ============================================================

def main_menu_markup():
    """القائمة الرئيسية — كل الصفوف"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎒 الصف الرابع", callback_data="grade_4"),
        InlineKeyboardButton("🎒 الصف الخامس", callback_data="grade_5"),
        InlineKeyboardButton("🎒 الصف السادس", callback_data="grade_6"),
        InlineKeyboardButton("📘 الصف السابع", callback_data="grade_7"),
        InlineKeyboardButton("📗 الصف الثامن", callback_data="grade_8"),
        InlineKeyboardButton("📙 الصف التاسع", callback_data="grade_9"),
        InlineKeyboardButton("🎓 الصف العاشر", callback_data="grade_10"),
        InlineKeyboardButton("🎓 الحادي عشر", callback_data="grade_11"),
        InlineKeyboardButton("🏆 بكالوريا", callback_data="grade_12"),
    )
    markup.add(InlineKeyboardButton("🔑 تفعيل التطبيق", callback_data="activate_info"))
    markup.add(InlineKeyboardButton("📤 شارك البوت", callback_data="share_bot"))
    markup.add(InlineKeyboardButton("ℹ️ معلومات حول البوت", callback_data="about_bot"))
    return markup

def grade_menu_markup(grade):
    """قائمة الصف — تظهر الدروس والمراجعات"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    if grade in ACTIVE_GRADES:
        markup.add(InlineKeyboardButton(f"📖 {LESSON_NAMES[grade]['1']}", callback_data=f"lesson_{grade}_1"))
        markup.add(InlineKeyboardButton(f"📖 {LESSON_NAMES[grade]['2']}", callback_data=f"lesson_{grade}_2"))
        markup.add(InlineKeyboardButton("📝 المراجعة 1 (قريباً)", callback_data=f"review_{grade}_1"))
        markup.add(InlineKeyboardButton("📝 المراجعة 2 (قريباً)", callback_data=f"review_{grade}_2"))
        markup.add(InlineKeyboardButton("📥 تحميل التطبيق", callback_data=f"download_{grade}"))
    else:
        markup.add(InlineKeyboardButton("🚧 قيد التطوير", callback_data="main_menu"))
    
    markup.add(InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_menu"))
    return markup

def lesson_menu_markup(grade, lesson):
    """قائمة الدرس — 8 أقسام"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📘 الشرح", callback_data=f"act_explain_{grade}_{lesson}"),
        InlineKeyboardButton("📚 المفردات", callback_data=f"act_vocab_{grade}_{lesson}"),
        InlineKeyboardButton("✍️ تحويل", callback_data=f"act_convert_{grade}_{lesson}"),
        InlineKeyboardButton("🔗 مطابقة", callback_data=f"act_match_{grade}_{lesson}"),
        InlineKeyboardButton("💬 إجابة حرة", callback_data=f"act_free_{grade}_{lesson}"),
        InlineKeyboardButton("📖 فهم قراءة", callback_data=f"act_texts_{grade}_{lesson}"),
        InlineKeyboardButton("📝 مواضيع كتابة", callback_data=f"act_topics_{grade}_{lesson}"),
        InlineKeyboardButton("📝 اختبار شامل", callback_data=f"act_quiz_{grade}_{lesson}"),
    )
    markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
    return markup

# ============================================================
# 🚀 /start
# ============================================================

@bot.message_handler(commands=['start', 'main_menu'])
def cmd_start(message):
    text = (
        "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n"
        "📚 بوتك الشامل لدراسة اللغة الإنجليزية بسهولة.\n"
        "اختر صفك الدراسي للبدء 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu_markup(), parse_mode='HTML')

# ============================================================
# 🎯 معالج الأزرار الرئيسي
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass
    
    data = call.data
    
    # ----- القائمة الرئيسية -----
    if data == "main_menu":
        text = (
            "🌟 <b>أهلاً بك في بوت إيمار التعليمي</b> 🌟\n\n"
            "📚 بوتك الشامل لدراسة اللغة الإنجليزية بسهولة.\n"
            "اختر صفك الدراسي للبدء 👇"
        )
        safe_edit_or_send(call, text, main_menu_markup())
    
    elif data == "share_bot":
        share_url = "https://t.me/share/url?url=https://t.me/Emar_English_App_bot&text=انضم إلى بوت إيمار التعليمي!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 مشاركة", url=share_url))
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit_or_send(call, "📤 <b>شارك البوت مع أصدقائك!</b>", markup)
    
    elif data == "activate_info":
        text = (
            "🔑 <b>تفعيل التطبيق</b>\n\n"
            "🎁 التطبيق مجاني لأول درسين.\n"
            "🔒 بقية الدروس تحتاج تفعيل.\n\n"
            "💰 السعر: 1500 ليرة جديدة لكل صف.\n"
            "💳 الدفع: شام كاش.\n\n"
            "📱 للتفعيل: افتح صفحة التفعيل في التطبيق وانسخ رقم المعرف، ثم تواصل مع المطور."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit_or_send(call, text, markup)
    
    elif data == "about_bot":
        text = "👨‍🏫 <b>بوت إيمار التعليمي</b>\n\nبوت لمساعدة طلاب الصفوف 7-9 على تعلم الإنجليزية بسهولة."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit_or_send(call, text, markup)
    
    # ----- اختيار صف -----
    elif data.startswith("grade_"):
        grade = data.split("_")[1]
        grade_name = GRADE_NAMES.get(grade, grade)
        
        if grade in ACTIVE_GRADES:
            text = f"🎓 <b>الصف {grade_name}</b>\n\n👇 اختر الدرس:"
        else:
            text = f"🎓 <b>الصف {grade_name}</b>\n\n🚧 هذا الصف قيد التطوير."
        
        safe_edit_or_send(call, text, grade_menu_markup(grade))
    
    # ----- اختيار درس -----
    elif data.startswith("lesson_"):
        parts = data.split("_")
        grade, lesson = parts[1], parts[2]
        lesson_name = LESSON_NAMES[grade][lesson]
        text = f"📖 <b>{lesson_name} — الصف {GRADE_NAMES[grade]}</b>\n\n👇 اختر القسم:"
        safe_edit_or_send(call, text, lesson_menu_markup(grade, lesson))
    
    # ----- مراجعة (قيد التطوير) -----
    elif data.startswith("review_"):
        dev_alert(call, "🚧 المراجعات قيد التطوير")
    
    # ----- تحميل التطبيق -----
    elif data.startswith("download_"):
        grade = data.split("_")[1]
        if grade in ["7", "8", "9"]:
            url = "https://t.me/EmarApp/102"
        elif grade == "6":
            url = "https://t.me/EmarApp/79"
        else:
            url = "https://t.me/EmarApp"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📥 تحميل التطبيق", url=url))
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
        safe_edit_or_send(call, "📥 <b>اضغط للتحميل:</b>", markup)
    
    # ============ الأقسام الثمانية ============
    
    elif data.startswith("act_explain_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        show_explain(call, grade, lesson)
    
    elif data.startswith("act_vocab_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        show_vocab(call, grade, lesson)
    
    elif data.startswith("act_convert_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        start_convert(call, grade, lesson)
    
    elif data.startswith("act_match_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        start_match(call, grade, lesson)
    
    elif data.startswith("act_free_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        start_free(call, grade, lesson)
    
    elif data.startswith("act_texts_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        start_texts(call, grade, lesson)
    
    elif data.startswith("act_topics_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        show_topics(call, grade, lesson)
    
    elif data.startswith("act_quiz_"):
        parts = data.split("_")
        grade, lesson = parts[2], parts[3]
        start_quiz(call, grade, lesson)
    
    # ============ إجابات التمارين ============
    
    elif data.startswith("qans_"):
        # إجابة MCQ (اختبار شامل)
        parts = data.split("_")
        grade, lesson, q_idx, orig_idx = parts[1], parts[2], int(parts[3]), int(parts[4])
        handle_quiz_answer(call, grade, lesson, q_idx, orig_idx)
    
    elif data.startswith("cans_"):
        # إجابة التحويل (اختيار من أزرار؟ لا، التحويل نصي)
        pass
    
    elif data.startswith("mans_"):
        # إجابة المطابقة
        parts = data.split("_")
        grade, lesson, grp_idx, sent_idx, opt_letter = parts[1], parts[2], int(parts[3]), int(parts[4]), parts[5]
        handle_match_answer(call, grade, lesson, grp_idx, sent_idx, opt_letter)
    
    elif data.startswith("tans_"):
        # إجابة فهم القراءة (MCQ أو TF)
        parts = data.split("_")
        grade, lesson, text_idx, q_idx, choice = parts[1], parts[2], int(parts[3]), int(parts[4]), parts[5]
        handle_texts_answer(call, grade, lesson, text_idx, q_idx, choice)

# ============================================================
# 📘 قسم الشرح
# ============================================================

def show_explain(call, grade, lesson):
    data = load_json(grade, lesson, "explain")
    if not data or "tables" not in data:
        dev_alert(call, "⚠️ تعذر تحميل الشرح")
        return
    
    tables = data["tables"]
    if not tables:
        dev_alert(call, "⚠️ لا يوجد شرح متاح")
        return
    
    # عرض كل جدول كرسالة منفصلة
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    
    bot.send_message(chat_id, f"📘 <b>شرح {LESSON_NAMES[grade][lesson]}</b>", parse_mode='HTML')
    
    for i, table in enumerate(tables, 1):
        title = table.get("title", f"جدول {i}")
        explanation = table.get("explanation", "")
        examples = table.get("examples", "")
        
        text = f"<b>{i}. {title}</b>\n\n"
        if explanation:
            text += f"💡 {explanation}\n\n"
        if examples:
            text += f"📝 <b>أمثلة:</b>\n{examples}"
        
        # تقسيم إذا طويل
        if len(text) > 4000:
            text = text[:3900] + "..."
        
        try:
            bot.send_message(chat_id, text, parse_mode='HTML')
        except Exception as e:
            print(f"[خطأ إرسال جدول] {e}")
    
    # زر العودة
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))
    bot.send_message(chat_id, "✅ انتهى الشرح", reply_markup=markup)

# ============================================================
# 📚 قسم المفردات
# ============================================================

def show_vocab(call, grade, lesson):
    data = load_json(grade, lesson, "explain")
    if not data or "vocabulary" not in data:
        dev_alert(call, "⚠️ تعذر تحميل المفردات")
        return
    
    vocab = data["vocabulary"]
    if not vocab:
        dev_alert(call, "⚠️ لا توجد مفردات")
        return
    
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    
    # تقسيم المفردات على دفعات (كل 30 كلمة)
    header = f"📚 <b>مفردات {LESSON_NAMES[grade][lesson]}</b>\n\n"
    chunks = [vocab[i:i+30] for i in range(0, len(vocab), 30)]
    
    for chunk in chunks:
        text = header
        for v in chunk:
            text += f"• <b>{v['word']}</b> → {v['translation']}\n"
        try:
            bot.send_message(chat_id, text, parse_mode='HTML')
        except Exception as e:
            print(f"[خطأ إرسال مفردات] {e}")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))
    bot.send_message(chat_id, "✅ انتهت المفردات", reply_markup=markup)

# ============================================================
# ✍️ قسم التحويل
# ============================================================

def start_convert(call, grade, lesson):
    data = load_json(grade, lesson, "convert")
    if not data or "questions" not in data or not data["questions"]:
        dev_alert(call, "⚠️ تعذر تحميل أسئلة التحويل")
        return
    
    questions = data["questions"]
    random.shuffle(questions)
    user_convert_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "questions": questions, "index": 0
    }
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    send_convert_question(call.message.chat.id)

def send_convert_question(chat_id):
    sess = user_convert_sessions.get(chat_id)
    if not sess:
        return
    
    if sess["index"] >= len(sess["questions"]):
        bot.send_message(chat_id, "🎉 <b>أكملت جميع أسئلة التحويل!</b>", parse_mode='HTML')
        del user_convert_sessions[chat_id]
        return
    
    q = sess["questions"][sess["index"]]
    text = (
        f"✍️ <b>سؤال {sess['index'] + 1} / {len(sess['questions'])}</b>\n\n"
        f"<b>الجملة:</b> {q['original']}\n"
        f"<b>الكلمة المستهدفة:</b> <u>{q['targetWord']}</u>\n\n"
        f"<i>اكتب السؤال المناسب:</i>"
    )
    bot.send_message(chat_id, text, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.chat.id in user_convert_sessions)
def handle_convert_reply(message):
    chat_id = message.chat.id
    sess = user_convert_sessions[chat_id]
    q = sess["questions"][sess["index"]]
    
    user_ans = clean_text(message.text or "")
    correct_list = []
    if q.get("correctQuestion"):
        correct_list.append(clean_text(q["correctQuestion"]))
    for c in q.get("correctQuestions", []):
        correct_list.append(clean_text(c))
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass
    
    if user_ans in correct_list:
        bot.send_message(chat_id, "✅ <b>إجابة صحيحة! أحسنت.</b>", parse_mode='HTML')
    else:
        correct = q.get("correctQuestion", "")
        bot.send_message(
            chat_id,
            f"❌ <b>إجابة غير صحيحة.</b>\n\n✅ <b>الصحيحة:</b>\n{correct}",
            parse_mode='HTML'
        )
    
    sess["index"] += 1
    send_convert_question(chat_id)

# ============================================================
# 🔗 قسم المطابقة
# ============================================================

def start_match(call, grade, lesson):
    data = load_json(grade, lesson, "match")
    if not data or "groups" not in data or not data["groups"]:
        dev_alert(call, "⚠️ تعذر تحميل المطابقة")
        return
    
    groups = data["groups"]
    user_match_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "groups": groups,
        "group_idx": 0, "sent_idx": 0
    }
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    send_match_question(call.message.chat.id)

def send_match_question(chat_id):
    sess = user_match_sessions.get(chat_id)
    if not sess:
        return
    
    groups = sess["groups"]
    if sess["group_idx"] >= len(groups):
        bot.send_message(chat_id, "🎉 <b>أكملت جميع أسئلة المطابقة!</b>", parse_mode='HTML')
        del user_match_sessions[chat_id]
        return
    
    group = groups[sess["group_idx"]]
    if sess["sent_idx"] >= len(group["sentences"]):
        sess["group_idx"] += 1
        sess["sent_idx"] = 0
        send_match_question(chat_id)
        return
    
    sent = group["sentences"][sess["sent_idx"]]
    options = group["options"]
    
    text = (
        f"🔗 <b>المطابقة — المجموعة {sess['group_idx'] + 1}</b>\n"
        f"<b>الجملة {sess['sent_idx'] + 1} / {len(group['sentences'])}</b>\n\n"
        f"<b>{sent['start']}</b> ...\n\n"
        f"اختر النهاية الصحيحة:"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    for opt in options:
        cb = f"mans_{sess['grade']}_{sess['lesson']}_{sess['group_idx']}_{sess['sent_idx']}_{opt['letter']}"
        markup.add(InlineKeyboardButton(f"{opt['letter']}. {opt['text']}", callback_data=cb))
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

def handle_match_answer(call, grade, lesson, grp_idx, sent_idx, opt_letter):
    chat_id = call.message.chat.id
    sess = user_match_sessions.get(chat_id)
    if not sess:
        dev_alert(call, "⚠️ انتهت الجلسة")
        return
    
    group = sess["groups"][sess["group_idx"]]
    sent = group["sentences"][sess["sent_idx"]]
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    
    if opt_letter == sent["correct"]:
        bot.send_message(chat_id, f"✅ <b>صحيح!</b>\n\n{sent['full_sentence']}\n\n<i>{sent.get('translation','')}</i>", parse_mode='HTML')
    else:
        correct_opt = next((o for o in group["options"] if o["letter"] == sent["correct"]), None)
        correct_text = correct_opt["text"] if correct_opt else "?"
        bot.send_message(
            chat_id,
            f"❌ <b>خطأ.</b>\n\n✅ الصحيحة: <b>{sent['correct']}. {correct_text}</b>\n\n{sent['full_sentence']}\n\n<i>{sent.get('translation','')}</i>",
            parse_mode='HTML'
        )
    
    sess["sent_idx"] += 1
    send_match_question(chat_id)

# ============================================================
# 💬 قسم الإجابة الحرة
# ============================================================

def start_free(call, grade, lesson):
    data = load_json(grade, lesson, "free_answer")
    if not data or "questions" not in data or not data["questions"]:
        dev_alert(call, "⚠️ تعذر تحميل الإجابة الحرة")
        return
    
    questions = data["questions"]
    random.shuffle(questions)
    user_free_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "questions": questions, "index": 0
    }
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    send_free_question(call.message.chat.id)

def send_free_question(chat_id):
    sess = user_free_sessions.get(chat_id)
    if not sess:
        return
    
    if sess["index"] >= len(sess["questions"]):
        bot.send_message(chat_id, "🎉 <b>أكملت جميع أسئلة الإجابة الحرة!</b>", parse_mode='HTML')
        del user_free_sessions[chat_id]
        return
    
    q = sess["questions"][sess["index"]]
    text = (
        f"💬 <b>سؤال {sess['index'] + 1} / {len(sess['questions'])}</b>\n\n"
        f"<b>{q['question']}</b>\n\n"
        f"<i>{q.get('translation','')}</i>\n\n"
        f"<i>اكتب إجابتك:</i>"
    )
    bot.send_message(chat_id, text, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.chat.id in user_free_sessions)
def handle_free_reply(message):
    chat_id = message.chat.id
    sess = user_free_sessions[chat_id]
    q = sess["questions"][sess["index"]]
    
    user_ans = clean_text(message.text or "")
    keywords = [clean_text(k) for k in q.get("keywords", [])]
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass
    
    # تحقق: هل تحتوي الإجابة على أي كلمة مفتاحية؟
    is_correct = any(kw in user_ans for kw in keywords) if keywords else False
    
    if is_correct:
        bot.send_message(chat_id, "✅ <b>إجابة صحيحة!</b>", parse_mode='HTML')
    else:
        suggested = q.get("suggested_answers", [])
        hint = "\n".join(f"• {s}" for s in suggested[:3])
        bot.send_message(
            chat_id,
            f"❌ <b>إجابة غير صحيحة.</b>\n\n💡 <b>أمثلة على الإجابات الصحيحة:</b>\n{hint}",
            parse_mode='HTML'
        )
    
    sess["index"] += 1
    send_free_question(chat_id)

# ============================================================
# 📖 قسم فهم القراءة
# ============================================================

def start_texts(call, grade, lesson):
    data = load_json(grade, lesson, "texts")
    if not data or "texts" not in data or not data["texts"]:
        dev_alert(call, "⚠️ تعذر تحميل نصوص القراءة")
        return
    
    texts = data["texts"]
    user_texts_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "texts": texts,
        "text_idx": 0, "q_idx": 0, "awaiting_text": True
    }
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    send_text_passage(call.message.chat.id)

def send_text_passage(chat_id):
    sess = user_texts_sessions.get(chat_id)
    if not sess:
        return
    
    if sess["text_idx"] >= len(sess["texts"]):
        bot.send_message(chat_id, "🎉 <b>أكملت جميع نصوص القراءة!</b>", parse_mode='HTML')
        del user_texts_sessions[chat_id]
        return
    
    text_data = sess["texts"][sess["text_idx"]]
    content = text_data.get("content_exam", "")
    title = text_data.get("source_text", f"نص {sess['text_idx']+1}")
    
    # تقسيم النص الطويل
    header = f"📖 <b>{title}</b>\n\n"
    full = header + content
    
    if len(full) > 4000:
        chunks = [full[i:i+3900] for i in range(0, len(full), 3900)]
        for ch in chunks:
            bot.send_message(chat_id, ch, parse_mode='HTML')
    else:
        bot.send_message(chat_id, full, parse_mode='HTML')
    
    sess["q_idx"] = 0
    sess["awaiting_text"] = False
    send_text_question(chat_id)

def send_text_question(chat_id):
    sess = user_texts_sessions.get(chat_id)
    if not sess:
        return
    
    text_data = sess["texts"][sess["text_idx"]]
    questions = text_data.get("questions", [])
    
    if sess["q_idx"] >= len(questions):
        sess["text_idx"] += 1
        if sess["text_idx"] >= len(sess["texts"]):
            bot.send_message(chat_id, "🎉 <b>أكملت جميع نصوص القراءة!</b>", parse_mode='HTML')
            del user_texts_sessions[chat_id]
            return
        send_text_passage(chat_id)
        return
    
    q = questions[sess["q_idx"]]
    q_type = q.get("type", "choice")
    
    header = f"❓ <b>سؤال {sess['q_idx']+1} / {len(questions)}</b>\n\n<b>{q['question']}</b>\n"
    
    if q_type == "choice":
        markup = InlineKeyboardMarkup(row_width=1)
        for i, opt in enumerate(q["options"]):
            cb = f"tans_{sess['grade']}_{sess['lesson']}_{sess['text_idx']}_{sess['q_idx']}_{i}"
            markup.add(InlineKeyboardButton(opt, callback_data=cb))
        bot.send_message(chat_id, header, reply_markup=markup, parse_mode='HTML')
    
    elif q_type in ("truefalse", "tf_answer"):
        markup = InlineKeyboardMarkup(row_width=2)
        cb_t = f"tans_{sess['grade']}_{sess['lesson']}_{sess['text_idx']}_{sess['q_idx']}_T"
        cb_f = f"tans_{sess['grade']}_{sess['lesson']}_{sess['text_idx']}_{sess['q_idx']}_F"
        markup.add(
            InlineKeyboardButton("✅ صح", callback_data=cb_t),
            InlineKeyboardButton("❌ خطأ", callback_data=cb_f)
        )
        bot.send_message(chat_id, header, reply_markup=markup, parse_mode='HTML')
    
    elif q_type == "answer":
        bot.send_message(chat_id, header + "\n<i>اكتب إجابتك:</i>", parse_mode='HTML')

def handle_texts_answer(call, grade, lesson, text_idx, q_idx, choice):
    chat_id = call.message.chat.id
    sess = user_texts_sessions.get(chat_id)
    if not sess:
        dev_alert(call, "⚠️ انتهت الجلسة")
        return
    
    text_data = sess["texts"][sess["text_idx"]]
    q = text_data["questions"][sess["q_idx"]]
    q_type = q.get("type", "choice")
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    
    is_correct = False
    if q_type == "choice":
        is_correct = (int(choice) == q["correct"])
    elif q_type in ("truefalse", "tf_answer"):
        ans_bool = (choice == "T")
        is_correct = (ans_bool == q["correct"])
    
    explanation = q.get("explanation", "")
    if is_correct:
        bot.send_message(chat_id, f"✅ <b>صحيح!</b>\n\n{explanation}", parse_mode='HTML')
    else:
        bot.send_message(chat_id, f"❌ <b>خطأ.</b>\n\n{explanation}", parse_mode='HTML')
    
    sess["q_idx"] += 1
    send_text_question(chat_id)

# ============================================================
# 📝 قسم مواضيع الكتابة
# ============================================================

def show_topics(call, grade, lesson):
    data = load_json(grade, lesson, "topics")
    if not data or "topics" not in data or not data["topics"]:
        dev_alert(call, "⚠️ تعذر تحميل المواضيع")
        return
    
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    
    topics = data["topics"]
    bot.send_message(chat_id, f"📝 <b>مواضيع الكتابة — {LESSON_NAMES[grade][lesson]}</b>", parse_mode='HTML')
    
    for i, topic in enumerate(topics, 1):
        text = f"<b>{i}. {topic['title']}</b>\n\n"
        if topic.get("guiding_questions"):
            text += "💡 <b>أسئلة مساعدة:</b>\n"
            for gq in topic["guiding_questions"]:
                text += f"• {gq}\n"
            text += "\n"
        if topic.get("sample_essay"):
            text += f"📄 <b>نموذج:</b>\n<i>{topic['sample_essay']}</i>"
        
        if len(text) > 4000:
            text = text[:3900] + "..."
        
        try:
            bot.send_message(chat_id, text, parse_mode='HTML')
        except Exception as e:
            print(f"[خطأ إرسال موضوع] {e}")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))
    bot.send_message(chat_id, "✅ انتهت المواضيع", reply_markup=markup)

# ============================================================
# 📝 قسم الاختبار الشامل (MCQ)
# ============================================================

def start_quiz(call, grade, lesson):
    data = load_json(grade, lesson, "grammar")
    if not data or "questions" not in data or not data["questions"]:
        dev_alert(call, "⚠️ تعذر تحميل الأسئلة")
        return
    
    all_q = data["questions"]
    num = min(10, len(all_q))
    selected = random.sample(all_q, num)
    
    user_quiz_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "questions": selected, "index": 0
    }
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    send_quiz_question(call.message.chat.id)

def send_quiz_question(chat_id):
    sess = user_quiz_sessions.get(chat_id)
    if not sess:
        return
    
    if sess["index"] >= len(sess["questions"]):
        bot.send_message(chat_id, "🎉 <b>أكملت الاختبار!</b>", parse_mode='HTML')
        del user_quiz_sessions[chat_id]
        return
    
    q = sess["questions"][sess["index"]]
    options = q["o"]
    
    # خلط الخيارات
    indices = list(range(len(options)))
    random.shuffle(indices)
    
    markup = InlineKeyboardMarkup(row_width=2)
    for display_i, orig_i in enumerate(indices):
        letter = chr(97 + display_i)
        cb = f"qans_{sess['grade']}_{sess['lesson']}_{sess['index']}_{orig_i}"
        markup.add(InlineKeyboardButton(f"{letter}. {options[orig_i]}", callback_data=cb))
    
    text = f"❓ <b>سؤال {sess['index']+1} / {len(sess['questions'])}</b>\n\n{q['q']}"
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

def handle_quiz_answer(call, grade, lesson, q_idx, orig_idx):
    chat_id = call.message.chat.id
    sess = user_quiz_sessions.get(chat_id)
    if not sess:
        dev_alert(call, "⚠️ انتهت الجلسة")
        return
    
    q = sess["questions"][q_idx]
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    
    explanation = q.get("exp", "")
    if orig_idx == q["c"]:
        bot.send_message(chat_id, f"✅ <b>صحيح!</b>\n\n{explanation}", parse_mode='HTML')
    else:
        bot.send_message(chat_id, f"❌ <b>خطأ.</b>\n\n{explanation}", parse_mode='HTML')
    
    sess["index"] = q_idx + 1
    
    if sess["index"] >= len(sess["questions"]):
        bot.send_message(chat_id, "🎉 <b>أكملت الاختبار!</b>", parse_mode='HTML')
        del user_quiz_sessions[chat_id]
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("➡️ السؤال التالي", callback_data=f"act_quiz_{grade}_{lesson}"))
        # لا نحتاج هذا الزر — سنرسل السؤال مباشرة
        send_quiz_question(chat_id)

# ============================================================
# 💬 الردود التلقائية
# ============================================================

@bot.message_handler(func=lambda m: m.chat.id not in user_convert_sessions 
                     and m.chat.id not in user_free_sessions
                     and m.chat.id not in user_texts_sessions)
def auto_reply(message):
    text = (message.text or "").lower()
    
    if "تحميل" in text or "حمل" in text or "تطبيق" in text:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📥 تطبيق (6)", url="https://t.me/EmarApp/79"),
            InlineKeyboardButton("📥 تطبيق (7-8-9)", url="https://t.me/EmarApp/102")
        )
        bot.send_message(
            message.chat.id,
            "📥 <b>تحميل التطبيق:</b>\n\nاختر صفك:",
            reply_markup=markup,
            parse_mode='HTML'
        )
    elif "تفعيل" in text or "فعل" in text:
        bot.send_message(
            message.chat.id,
            "🔑 <b>التفعيل:</b>\n\n"
            "1️⃣ افتح صفحة التفعيل في التطبيق\n"
            "2️⃣ انسخ رقم المعرف\n"
            "3️⃣ تواصل مع المطور\n\n"
            "💰 السعر: 1500 ليرة لكل صف",
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            message.chat.id,
            "🌟 أهلاً بك!\n\n"
            "استخدم /start لفتح القائمة الرئيسية.",
            parse_mode='HTML'
        )

# ============================================================
# 🌐 سيرفر HTTP وهمي لـ Render
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    def log_message(self, *args):
        pass  # تجاهل السجلات

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ============================================================
# 🚀 التشغيل
# ============================================================

if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.infinity_polling()
