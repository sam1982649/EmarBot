import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ⚠️ ضع التوكن الخاص بك هنا (بدون حذف علامات التنصيص)
TOKEN = "8635643004:AAG--rxwYJJfP3ze1fEpqRysvMcJM-O7x5M"
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

    if call.data == 'main_menu':
        send_welcome(call.message)
        
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
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=activation_text, reply_markup=markup, parse_mode='HTML')
        
    elif call.data == 'about_bot':
        bot.send_message(call.message.chat.id, "👨‍🏫 <b>معلومات حول البوت:</b>\n\nتم تصميم هذا البوت لتسهيل وصول الطلاب إلى ملفات قناة إيمار.", parse_mode='HTML')
        
    # ==========================================
    # 1. قائمة الصفوف
    # ==========================================
    elif call.data.startswith('grade_'):
        grade_num = call.data.split('_')[1]
        all_buttons = []
        
        if grade_num in ['4', '5', '6']:
            for i in range(1, 21):
                all_buttons.append(InlineKeyboardButton(f"Unit {i}", callback_data=f"lesson_{grade_num}_{i}"))
                if i % 5 == 0:
                    rev_num = i // 5
                    all_buttons.append(InlineKeyboardButton(f"📝 Revision {rev_num}", callback_data=f"lesson_{grade_num}_rev{rev_num}"))
        elif grade_num in ['7', '8', '9']:
            for i in range(1, 13):
                all_buttons.append(InlineKeyboardButton(f"Unit {i}", callback_data=f"lesson_{grade_num}_{i}"))
                if i % 6 == 0:
                    rev_num = i // 6
                    all_buttons.append(InlineKeyboardButton(f"📝 Revision {rev_num}", callback_data=f"lesson_{grade_num}_rev{rev_num}"))
        else:
            for i in range(1, 13):
                all_buttons.append(InlineKeyboardButton(f"Unit {i}", callback_data=f"lesson_{grade_num}_{i}"))
                if i % 4 == 0:
                    rev_num = i // 4
                    all_buttons.append(InlineKeyboardButton(f"📝 Revision {rev_num}", callback_data=f"lesson_{grade_num}_rev{rev_num}"))
        
        units_markup = InlineKeyboardMarkup(row_width=2)
        units_markup.add(*all_buttons)

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
        
        units_markup.add(InlineKeyboardButton("➖➖ أقسام إضافية ➖➖", callback_data="ignore"))
        for row in extra_markup.keyboard:
            units_markup.add(*row)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎓 لقد اخترت <b>الصف {grade_num}</b>.\n\n👇 <b>اختر الدرس أو القسم المطلوب:</b>",
            reply_markup=units_markup,
            parse_mode='HTML'
        )

    # ==========================================
    # 2. تمارين الدرس
    # ==========================================
    elif call.data.startswith('lesson_'):
        parts = call.data.split('_')
        grade = parts[1]
        lesson = parts[2]
        lesson_name = lesson.replace("rev", "Revision ") if "rev" in lesson else f"Unit {lesson}"
        
        markup = InlineKeyboardMarkup(row_width=1) 
        
        markup.add(
            InlineKeyboardButton("📘 الشرح", callback_data=f"nofile_lesson_{grade}_{lesson}_1"),
            InlineKeyboardButton("📄 النصوص", callback_data=f"nofile_lesson_{grade}_{lesson}_2"),
            InlineKeyboardButton("🔗 توصيل", callback_data=f"nofile_lesson_{grade}_{lesson}_3"),
            InlineKeyboardButton("❓ تحويل إلى سؤال", callback_data=f"nofile_lesson_{grade}_{lesson}_4"),
            InlineKeyboardButton("✍️ كتابة جواب", callback_data=f"nofile_lesson_{grade}_{lesson}_5"),
            InlineKeyboardButton("📚 المواضيع", callback_data=f"nofile_lesson_{grade}_{lesson}_6")
        )
        markup.add(InlineKeyboardButton("🔙 العودة للدروس", callback_data=f"grade_{grade}"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📚 <b>الصف {grade} - {lesson_name}</b>\n\n👇 <b>اختر نوع التمرين أو الملف:</b>",
            reply_markup=markup,
            parse_mode='HTML'
        )

    # ==========================================
    # 3. الأقسام الإضافية
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
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📚 <b>الصف {grade} - {type_names[extra_type]}</b>\n\n⚠️ <b>ملاحظة:</b> لم يتم رفع ملفات هذا القسم بعد.",
            reply_markup=markup,
            parse_mode='HTML'
        )

    # ==========================================
    # 4. الأزرار الفارغة
    # ==========================================
    elif call.data.startswith('nofile_'):
        bot.answer_callback_query(call.id, "⚠️ عذراً، لم يتم رفع هذا الملف بعد. سيتم إضافته قريباً!", show_alert=True)

print("البوت يعمل الآن بانتظار الرسائل...")
bot.infinity_polling()
