# ============================================================
# 🤖 بوت إيمار التعليمي — الإصدار 3.1 (مخصص للصفوف 7، 8، 9 فقط)
# ============================================================
# ✨ الميزات:
#  • تصميم احترافي (رسالة واحدة تتحول + شريط تقدم)
#  • اختيار عدد الأسئلة (5/10/20/30/الكل)
#  • زر "إنهاء" في أي لحظة
#  • شاشة نتائج نهائية مع نسبة مئوية
#  • دعم 3 صفوف فقط (7، 8، 9) × 2 دروس × 7 أنواع تمارين
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
# ⚙️ الإعدادات
# ============================================================
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

BASE_URL = "https://raw.githubusercontent.com/sam1982649/Emar7-8_data/main"

# الصفوف النشطة فقط
ACTIVE_GRADES = ["7", "8", "9"]

GRADE_NAMES = {
    "7": "السابع", "8": "الثامن", "9": "التاسع",
}

LESSON_NAMES = {
    "7": {"1": "الدرس 1", "2": "الدرس 2"},
    "8": {"1": "الدرس 1", "2": "الدرس 2"},
    "9": {"1": "الدرس 1", "2": "الدرس 2"},
}

LESSON_PATHS = {
    "7": {"1": "grade7/lesson1", "2": "grade7/lesson2"},
    "8": {"1": "grade8/lesson1", "2": "grade8/lesson2"},
    "9": {"1": "grade9/lesson1", "2": "grade9/lesson2"},
}

FILE_TYPES = {
    "grammar": "grammar.json",
    "convert": "convert_data.json",
    "free_answer": "free_answer_data.json",
    "explain": "explain_data.json",
    "match": "match_data.json",
    "texts": "texts_data.json",
    "topics": "topics.json",
}

# ============================================================
# 💾 كاش
# ============================================================
_data_cache = {}

def load_json(grade, lesson, file_type):
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
# 🧹 أدوات
# ============================================================
def clean_text(text):
    text = text.lower().strip()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def safe_edit(call, text, markup=None):
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=text, reply_markup=markup, parse_mode='HTML'
        )
    except Exception:
        try:
            bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='HTML')
        except Exception:
            pass

def dev_alert(call, msg="🚧 قيد التطوير"):
    try:
        bot.answer_callback_query(call.id, msg, show_alert=True)
    except Exception:
        pass

def progress_bar(current, total, length=10):
    filled = int((current / total) * length) if total else 0
    return "▓" * filled + "░" * (length - filled)

# ============================================================
# 🧠 جلسات
# ============================================================
user_sessions = {}       # جلسات التمارين
user_free_sessions = {}  # جلسة الإجابة الحرة (نصية)
user_convert_sessions = {}  # جلسة التحويل (نصية)
user_texts_sessions = {}  # جلسة فهم قراءة (نصية للإجابات)

# ============================================================
# 🎨 القوائم
# ============================================================
def main_menu():
    m = InlineKeyboardMarkup(row_width=1) # جعلتها عمود واحد لتبدو مرتبة أكثر مع 3 صفوف
    m.add(
        InlineKeyboardButton("📘 الصف السابع", callback_data="grade_7"),
        InlineKeyboardButton("📗 الصف الثامن", callback_data="grade_8"),
        InlineKeyboardButton("📙 الصف التاسع", callback_data="grade_9"),
    )
    m.add(InlineKeyboardButton("🔑 تفعيل التطبيق", callback_data="activate_info"))
    m.add(InlineKeyboardButton("📤 شارك البوت", callback_data="share_bot"))
    m.add(InlineKeyboardButton("ℹ️ معلومات", callback_data="about_bot"))
    return m

def grade_menu(grade):
    m = InlineKeyboardMarkup(row_width=1)
    if grade in ACTIVE_GRADES:
        m.add(InlineKeyboardButton(f"📖 {LESSON_NAMES[grade]['1']}", callback_data=f"lesson_{grade}_1"))
        m.add(InlineKeyboardButton(f"📖 {LESSON_NAMES[grade]['2']}", callback_data=f"lesson_{grade}_2"))
        m.add(InlineKeyboardButton("📝 المراجعة 1 (قريباً)", callback_data=f"review_{grade}_1"))
        m.add(InlineKeyboardButton("📝 المراجعة 2 (قريباً)", callback_data=f"review_{grade}_2"))
        m.add(InlineKeyboardButton("📥 تحميل التطبيق", callback_data=f"download_{grade}"))
    m.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
    return m

def lesson_menu(grade, lesson):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("📘 الشرح", callback_data=f"act_explain_{grade}_{lesson}"),
        InlineKeyboardButton("📚 المفردات", callback_data=f"act_vocab_{grade}_{lesson}"),
        InlineKeyboardButton("✍️ تحويل", callback_data=f"act_convert_{grade}_{lesson}"),
        InlineKeyboardButton("🔗 مطابقة", callback_data=f"act_match_{grade}_{lesson}"),
        InlineKeyboardButton("💬 إجابة حرة", callback_data=f"act_free_{grade}_{lesson}"),
        InlineKeyboardButton("📖 فهم قراءة", callback_data=f"act_texts_{grade}_{lesson}"),
        InlineKeyboardButton("📝 مواضيع كتابة", callback_data=f"act_topics_{grade}_{lesson}"),
        InlineKeyboardButton("📝 اختبار شامل", callback_data=f"act_quiz_{grade}_{lesson}"),
    )
    m.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
    return m

# ============================================================
# 🚀 /start
# ============================================================
@bot.message_handler(commands=['start', 'main_menu'])
def cmd_start(message):
    text = "🌟 <b>بوت إيمار التعليمي</b> 🌟\n\n📚 رفيقك في دراسة الإنجليزية للصفوف (7 - 8 - 9).\nاختر صفك للبدء 👇"
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode='HTML')

# ============================================================
# 🎯 المعالج الرئيسي
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    data = call.data

    # ===== القوائم =====
    if data == "main_menu":
        safe_edit(call, "🌟 <b>بوت إيمار</b> 🌟\n\nاختر صفك:", main_menu())

    elif data == "share_bot":
        url = "https://t.me/share/url?url=https://t.me/Emar_English_App_bot&text=انضم لبوت إيمار!"
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("📤 مشاركة", url=url))
        m.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit(call, "📤 <b>شارك البوت:</b>", m)

    elif data == "activate_info":
        text = (
            "🔑 <b>تفعيل التطبيق</b>\n\n"
            "🎁 مجاني لأول درسين.\n"
            "🔒 الباقي يحتاج تفعيل.\n\n"
            "💰 السعر: 1500 ليرة/صف\n"
            "💳 شام كاش"
        )
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit(call, text, m)

    elif data == "about_bot":
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        safe_edit(call, "👨‍🏫 <b>بوت إيمار</b>\n\nمخصص لطلاب الصفوف 7-8-9.", m)

    elif data.startswith("grade_"):
        grade = data.split("_")[1]
        if grade in ACTIVE_GRADES:
            text = f"🎓 <b>الصف {GRADE_NAMES[grade]}</b>\n\n👇 اختر:"
            safe_edit(call, text, grade_menu(grade))
        else:
            dev_alert(call, "⚠️ هذا الصف غير متوفر حالياً")

    elif data.startswith("lesson_"):
        _, grade, lesson = data.split("_")
        text = f"📖 <b>{LESSON_NAMES[grade][lesson]} — الصف {GRADE_NAMES[grade]}</b>\n\n👇 اختر القسم:"
        safe_edit(call, text, lesson_menu(grade, lesson))

    elif data.startswith("review_"):
        dev_alert(call, "🚧 المراجعات قيد التطوير")

    elif data.startswith("download_"):
        grade = data.split("_")[1]
        url = "https://t.me/EmarApp/102" if grade in ["7","8","9"] else "https://t.me/EmarApp"
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton("📥 تحميل", url=url))
        m.add(InlineKeyboardButton("🔙 العودة", callback_data=f"grade_{grade}"))
        safe_edit(call, "📥 <b>تحميل التطبيق:</b>", m)

    # ===== الأقسام =====
    elif data.startswith("act_explain_"):
        _, _, grade, lesson = data.split("_")
        show_explain(call, grade, lesson)

    elif data.startswith("act_vocab_"):
        _, _, grade, lesson = data.split("_")
        show_vocab(call, grade, lesson)

    elif data.startswith("act_topics_"):
        _, _, grade, lesson = data.split("_")
        show_topics(call, grade, lesson)

    elif data.startswith("act_free_"):
        _, _, grade, lesson = data.split("_")
        start_free_answer(call, grade, lesson)

    elif data.startswith("act_texts_"):
        _, _, grade, lesson = data.split("_")
        start_texts(call, grade, lesson)

    # الأقسام التي تطلب عدد الأسئلة
    elif data.startswith("act_quiz_"):
        _, _, grade, lesson = data.split("_")
        ask_count(call, grade, lesson, "quiz")

    elif data.startswith("act_convert_"):
        _, _, grade, lesson = data.split("_")
        ask_count(call, grade, lesson, "convert")

    elif data.startswith("act_match_"):
        _, _, grade, lesson = data.split("_")
        ask_count(call, grade, lesson, "match")

    # ===== اختيار العدد =====
    elif data.startswith("count_"):
        parts = data.split("_")
        grade, lesson, ex_type, count = parts[1], parts[2], parts[3], parts[4]
        start_exercise(call, grade, lesson, ex_type, count)

    # ===== إجابات =====
    elif data.startswith("ans_"):
        parts = data.split("_")
        grade, lesson, ex_type, idx = parts[1], parts[2], parts[3], int(parts[4])
        choice = parts[5] if len(parts) > 5 else ""
        handle_answer(call, grade, lesson, ex_type, idx, choice)

    elif data.startswith("next_"):
        parts = data.split("_")
        grade, lesson, ex_type = parts[1], parts[2], parts[3]
        next_question(call, grade, lesson, ex_type)

    elif data.startswith("end_"):
        parts = data.split("_")
        grade, lesson, ex_type = parts[1], parts[2], parts[3]
        end_exercise(call, grade, lesson, ex_type)

    elif data.startswith("restart_"):
        parts = data.split("_")
        grade, lesson, ex_type = parts[1], parts[2], parts[3]
        ask_count(call, grade, lesson, ex_type)

    elif data.startswith("convert_end_") or data.startswith("free_end_") or data.startswith("texts_end_"):
        # إنهاء التمارين النصية
        parts = data.split("_")
        ex_type, grade, lesson = parts[0], parts[1], parts[3] if len(parts) > 3 else parts[2]
        end_text_exercise(call, grade, lesson, ex_type)

# ============================================================
# 📘 الشرح
# ============================================================
def show_explain(call, grade, lesson):
    data = load_json(grade, lesson, "explain")
    if not data or not data.get("tables"):
        dev_alert(call, "⚠️ تعذر التحميل")
        return
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(chat_id, f"📘 <b>شرح {LESSON_NAMES[grade][lesson]}</b>", parse_mode='HTML')
    for i, t in enumerate(data["tables"], 1):
        text = f"<b>{i}. {t.get('title','')}</b>\n\n"
        if t.get("explanation"):
            text += f"💡 {t['explanation']}\n\n"
        if t.get("examples"):
            text += f"📝 <b>أمثلة:</b>\n{t['examples']}"
        try:
            bot.send_message(chat_id, text[:4000], parse_mode='HTML')
        except Exception:
            pass
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))
    bot.send_message(chat_id, "✅ انتهى الشرح", reply_markup=m)

# ============================================================
# 📚 المفردات
# ============================================================
def show_vocab(call, grade, lesson):
    data = load_json(grade, lesson, "explain")
    if not data or not data.get("vocabulary"):
        dev_alert(call, "⚠️ تعذر التحميل")
        return
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    vocab = data["vocabulary"]
    header = f"📚 <b>مفردات {LESSON_NAMES[grade][lesson]}</b>\n\n"
    for i in range(0, len(vocab), 30):
        text = header
        for v in vocab[i:i+30]:
            text += f"• <b>{v['word']}</b> → {v['translation']}\n"
        try:
            bot.send_message(chat_id, text, parse_mode='HTML')
        except Exception:
            pass
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))
    bot.send_message(chat_id, "✅ انتهت المفردات", reply_markup=m)

# ============================================================
# 📝 مواضيع الكتابة
# ============================================================
def show_topics(call, grade, lesson):
    data = load_json(grade, lesson, "topics")
    if not data or not data.get("topics"):
        dev_alert(call, "⚠️ تعذر التحميل")
        return
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(chat_id, f"📝 <b>مواضيع الكتابة — {LESSON_NAMES[grade][lesson]}</b>", parse_mode='HTML')
    for i, topic in enumerate(data["topics"], 1):
        text = f"<b>{i}. {topic['title']}</b>\n\n"
        if topic.get("guiding_questions"):
            text += "💡 <b>أسئلة مساعدة:</b>\n"
            for gq in topic["guiding_questions"]:
                text += f"• {gq}\n"
            text += "\n"
        if topic.get("sample_essay"):
            text += f"📄 <b>نموذج:</b>\n<i>{topic['sample_essay']}</i>"
        try:
            bot.send_message(chat_id, text[:4000], parse_mode='HTML')
        except Exception:
            pass
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))
    bot.send_message(chat_id, "✅ انتهت المواضيع", reply_markup=m)

# ============================================================
# 🎯 شاشة اختيار عدد الأسئلة
# ============================================================
def ask_count(call, grade, lesson, ex_type):
    chat_id = call.message.chat.id

    file_map = {"quiz": "grammar", "convert": "convert", "match": "match"}
    data = load_json(grade, lesson, file_map[ex_type])
    if not data:
        dev_alert(call, "⚠️ تعذر التحميل")
        return

    # حساب العدد المتاح
    if ex_type == "quiz":
        available = len(data.get("questions", []))
        title = "📝 اختبار القواعد"
    elif ex_type == "convert":
        available = len(data.get("questions", []))
        title = "✍️ تحويل إلى سؤال"
    elif ex_type == "match":
        available = sum(len(g["sentences"]) for g in data.get("groups", []))
        title = "🔗 المطابقة"

    if available == 0:
        dev_alert(call, "⚠️ لا توجد أسئلة")
        return

    # بناء الأزرار الذكية
    m = InlineKeyboardMarkup(row_width=3)
    options = []
    if available >= 30:
        options = [5, 10, 20, 30]
    elif available >= 15:
        options = [5, 10, 15]
    elif available >= 10:
        options = [5, 10]
    # إذا أقل من 10 → فقط "الكل"

    for n in options:
        m.add(InlineKeyboardButton(
            f"{n} أسئلة",
            callback_data=f"count_{grade}_{lesson}_{ex_type}_{n}"
        ))
    m.add(InlineKeyboardButton(
        f"🎲 الكل ({available})",
        callback_data=f"count_{grade}_{lesson}_{ex_type}_all"
    ))
    m.add(InlineKeyboardButton("🔙 العودة", callback_data=f"lesson_{grade}_{lesson}"))

    text = (
        f"{title}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 <b>متاح:</b> {available} سؤالاً\n\n"
        f"🎯 <b>كم سؤالاً تريد؟</b>"
    )
    safe_edit(call, text, m)

# ============================================================
# 🎯 بدء التمرين بعد اختيار العدد
# ============================================================
def start_exercise(call, grade, lesson, ex_type, count_str):
    chat_id = call.message.chat.id

    file_map = {"quiz": "grammar", "convert": "convert", "match": "match"}
    data = load_json(grade, lesson, file_map[ex_type])
    if not data:
        dev_alert(call, "⚠️ تعذر التحميل")
        return

    # بناء قائمة الأسئلة
    if ex_type == "quiz":
        all_q = data.get("questions", [])
        for q in all_q:
            idx = list(range(len(q["o"])))
            random.shuffle(idx)
            q["_shuffled"] = idx
        if count_str == "all":
            questions = all_q[:]
            random.shuffle(questions)
        else:
            n = min(int(count_str), len(all_q))
            questions = random.sample(all_q, n)

    elif ex_type == "convert":
        all_q = data.get("questions", [])[:]
        random.shuffle(all_q)
        if count_str == "all":
            questions = all_q
        else:
            n = min(int(count_str), len(all_q))
            questions = all_q[:n]

    elif ex_type == "match":
        groups = data.get("groups", [])
        all_items = []
        for g in groups:
            for s in g["sentences"]:
                all_items.append({"group": g, "sent": s})
        random.shuffle(all_items)
        if count_str == "all":
            questions = all_items
        else:
            n = min(int(count_str), len(all_items))
            questions = all_items[:n]

    # حفظ الجلسة
    user_sessions[chat_id] = {
        "type": ex_type,
        "grade": grade,
        "lesson": lesson,
        "questions": questions,
        "index": 0,
        "correct": 0,
        "wrong": 0,
    }

    try:
        bot.delete_message(chat_id, call.message.message_id)
    except Exception:
        pass

    send_question(chat_id)

# ============================================================
# 🖼️ عرض السؤال
# ============================================================
def send_question(chat_id):
    sess = user_sessions.get(chat_id)
    if not sess:
        return
    ex_type = sess["type"]
    idx = sess["index"]
    total = len(sess["questions"])

    if idx >= total:
        send_results(chat_id)
        return

    q = sess["questions"][idx]
    prog = progress_bar(idx, total)
    header = f"📝 <b>سؤال {idx+1} من {total}</b>\n<code>{prog}</code>  {int((idx/total)*100)}%\n\n"
    end_btn = InlineKeyboardButton("🚪 إنهاء", callback_data=f"end_{sess['grade']}_{sess['lesson']}_{ex_type}")

    if ex_type == "quiz":
        text = header + f"❓ {q['q']}"
        m = InlineKeyboardMarkup(row_width=2)
        for display_i, orig_i in enumerate(q["_shuffled"]):
            letter = chr(97 + display_i)
            cb = f"ans_{sess['grade']}_{sess['lesson']}_quiz_{idx}_{orig_i}"
            m.add(InlineKeyboardButton(f"{letter}. {q['o'][orig_i]}", callback_data=cb))
        m.add(end_btn)
        bot.send_message(chat_id, text, reply_markup=m, parse_mode='HTML')

    elif ex_type == "convert":
        # تحويل = نصي، نحتاج جلسة نصية منفصلة
        user_convert_sessions[chat_id] = {
            "grade": sess["grade"], "lesson": sess["lesson"],
            "questions": sess["questions"], "index": 0,
            "correct": 0, "wrong": 0,
        }
        del user_sessions[chat_id]
        send_convert_question(chat_id)

    elif ex_type == "match":
        sent = q["sent"]
        grp = q["group"]
        text = header + f"🔗 <b>أكمل الجملة:</b>\n\n<b>{sent['start']} ...</b>\n\nاختر النهاية:"
        m = InlineKeyboardMarkup(row_width=1)
        for opt in grp["options"]:
            cb = f"ans_{sess['grade']}_{sess['lesson']}_match_{idx}_{opt['letter']}"
            m.add(InlineKeyboardButton(f"{opt['letter']}. {opt['text']}", callback_data=cb))
        m.add(end_btn)
        bot.send_message(chat_id, text, reply_markup=m, parse_mode='HTML')

# ============================================================
# ✍️ التحويل النصي
# ============================================================
def send_convert_question(chat_id):
    sess = user_convert_sessions.get(chat_id)
    if not sess:
        return
    idx = sess["index"]
    total = len(sess["questions"])
    if idx >= total:
        send_text_results(chat_id, sess, "convert")
        del user_convert_sessions[chat_id]
        return

    q = sess["questions"][idx]
    prog = progress_bar(idx, total)
    text = (
        f"✍️ <b>سؤال {idx+1} من {total}</b>\n<code>{prog}</code>  {int((idx/total)*100)}%\n\n"
        f"<b>الجملة:</b> {q['original']}\n"
        f"<b>الكلمة المستهدفة:</b> <u>{q['targetWord']}</u>\n\n"
        f"<i>اكتب السؤال في المحادثة:</i>"
    )
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🚪 إنهاء", callback_data=f"convert_end_{sess['grade']}_{sess['lesson']}"))
    bot.send_message(chat_id, text, reply_markup=m, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.chat.id in user_convert_sessions)
def handle_convert_reply(message):
    chat_id = message.chat.id
    sess = user_convert_sessions[chat_id]
    idx = sess["index"]
    q = sess["questions"][idx]

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
        sess["correct"] += 1
        bot.send_message(chat_id, "✅ <b>إجابة صحيحة!</b>", parse_mode='HTML')
    else:
        sess["wrong"] += 1
        correct = q.get("correctQuestion", "")
        bot.send_message(
            chat_id,
            f"❌ <b>إجابة غير صحيحة.</b>\n\n✅ <b>الصحيحة:</b>\n<code>{correct}</code>",
            parse_mode='HTML'
        )

    sess["index"] += 1
    send_convert_question(chat_id)

# ============================================================
# 💬 الإجابة الحرة
# ============================================================
def start_free_answer(call, grade, lesson):
    data = load_json(grade, lesson, "free_answer")
    if not data or not data.get("questions"):
        dev_alert(call, "⚠️ تعذر التحميل")
        return
    questions = data["questions"][:]
    random.shuffle(questions)
    user_free_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "questions": questions,
        "index": 0, "correct": 0, "wrong": 0,
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
    idx = sess["index"]
    total = len(sess["questions"])
    if idx >= total:
        send_text_results(chat_id, sess, "free")
        del user_free_sessions[chat_id]
        return
    q = sess["questions"][idx]
    prog = progress_bar(idx, total)
    text = (
        f"💬 <b>سؤال {idx+1} من {total}</b>\n<code>{prog}</code>  {int((idx/total)*100)}%\n\n"
        f"<b>{q['question']}</b>\n\n"
        f"<i>{q.get('translation','')}</i>\n\n"
        f"<i>اكتب إجابتك:</i>"
    )
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("🚪 إنهاء", callback_data=f"free_end_{sess['grade']}_{sess['lesson']}"))
    bot.send_message(chat_id, text, reply_markup=m, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.chat.id in user_free_sessions)
def handle_free_reply(message):
    chat_id = message.chat.id
    sess = user_free_sessions[chat_id]
    idx = sess["index"]
    q = sess["questions"][idx]

    user_ans = clean_text(message.text or "")
    keywords = [clean_text(k) for k in q.get("keywords", [])]
    is_correct = any(kw in user_ans for kw in keywords) if keywords else False

    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass

    if is_correct:
        sess["correct"] += 1
        bot.send_message(chat_id, "✅ <b>إجابة صحيحة!</b>", parse_mode='HTML')
    else:
        sess["wrong"] += 1
        suggested = q.get("suggested_answers", [])
        hint = "\n".join(f"• {s}" for s in suggested[:3])
        bot.send_message(chat_id, f"❌ <b>إجابة غير صحيحة.</b>\n\n💡 <b>أمثلة:</b>\n{hint}", parse_mode='HTML')

    sess["index"] += 1
    send_free_question(chat_id)

# ============================================================
# 📖 فهم القراءة
# ============================================================
def start_texts(call, grade, lesson):
    data = load_json(grade, lesson, "texts")
    if not data or not data.get("texts"):
        dev_alert(call, "⚠️ تعذر التحميل")
        return
    texts = data["texts"]
    # بناء قائمة مسطحة من (نص، سؤال)
    all_q = []
    for t in texts:
        for q in t.get("questions", []):
            all_q.append({"text": t, "q": q})
    user_texts_sessions[call.message.chat.id] = {
        "grade": grade, "lesson": lesson, "questions": all_q,
        "index": 0, "correct": 0, "wrong": 0,
        "current_text": None,
    }
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_text_question(call.message.chat.id)

def send_text_question(chat_id):
    sess = user_texts_sessions.get(chat_id)
    if not sess:
        return
    idx = sess["index"]
    total = len(sess["questions"])
    if idx >= total:
        send_text_results(chat_id, sess, "texts")
        del user_texts_sessions[chat_id]
        return

    item = sess["questions"][idx]
    text_data = item["text"]
    q = item["q"]

    # إذا تغير النص، اعرضه أولاً
    text_id = text_data.get("id", "")
    if sess["current_text"] != text_id:
        sess["current_text"] = text_id
        title = text_data.get("source_text", "نص")
        content = text_data.get("content_exam", "")
        full = f"📖 <b>{title}</b>\n\n{content}"
        if len(full) > 4000:
            for i in range(0, len(full), 3900):
                try:
                    bot.send_message(chat_id, full[i:i+3900], parse_mode='HTML')
                except Exception:
                    pass
        else:
            try:
                bot.send_message(chat_id, full, parse_mode='HTML')
            except Exception:
                pass

    q_type = q.get("type", "choice")
    prog = progress_bar(idx, total)
    header = (
        f"❓ <b>سؤال {idx+1} من {total}</b>\n"
        f"<code>{prog}</code>  {int((idx/total)*100)}%\n\n"
        f"<b>{q['question']}</b>"
    )
    end_btn = InlineKeyboardButton("🚪 إنهاء", callback_data=f"texts_end_{sess['grade']}_{sess['lesson']}")

    if q_type == "choice
