import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from database import Database

# ===================== LOGGING =====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ===================== CONFIG =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = list(
    map(int, os.getenv("ADMIN_IDS", "7454731921").split(","))
)

db = Database()

# ===================== SUBSCRIPTION =====================

async def check_subscription(user_id, bot):

    channels = db.get_channels()

    if not channels:
        return True

    for channel in channels:

        channel_id = channel[1]

        try:

            member = await bot.get_chat_member(
                channel_id,
                user_id
            )

            if member.status not in [
                "member",
                "administrator",
                "creator"
            ]:
                return False

        except:
            return False

    return True


async def subscription_required(update, context):

    channels = db.get_channels()

    keyboard = []

    for channel in channels:

        channel_id = channel[1]
        channel_name = channel[2]

        username = channel_id.replace("@", "")

        keyboard.append([
            InlineKeyboardButton(
                f"📢 {channel_name}",
                url=f"https://t.me/{username}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "✅ Tekshirish",
            callback_data="check_sub"
        )
    ])

    await update.message.reply_text(
        "📢 Botdan foydalanish uchun kanallarga obuna bo'ling:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
# ===================== HELPERS =====================


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ===================== USER COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    is_subscribed = await check_subscription(
        update.effective_user.id,
        context.bot
    )

    if not is_subscribed:

        await subscription_required(
            update,
            context
        )

        return

    text = (
        f"👋 Salom, *{user.first_name}*!\n\n"
        "🎬 *Kino Bot*ga xush kelibsiz!\n\n"
        "📌 Kino olish uchun kino kodini yuboring.\n"
        "Masalan: `1001`\n\n"
        "📋 Buyruqlar:\n"
        "/start — Botni ishga tushirish\n"
        "/help — Yordam\n"
        "/admin — Admin panel"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 *Yordam*\n\n"
        "Kino olish uchun kino kodini yuboring.\n"
        "Masalan:\n"
        "`1001`\n"
        "`2005`\n"
        "`333`\n\n"
        "Kod noto'g'ri bo'lsa, bot sizga xabar beradi."
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


# ===================== USER CODE HANDLER =====================

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_subscribed = await check_subscription(
        update.effective_user.id,
        context.bot
    )

    if not is_subscribed:
        await subscription_required(
            update,
            context
        )

        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # Agar command bo'lsa o'tkazib yuboriladi
    if text.startswith("/"):
        return

    # Faqat raqam qabul qilish
    if not text.isdigit():
        await update.message.reply_text(
            "❌ Noto'g'ri kod.\n\n"
            "Iltimos, raqamli kod yuboring.\n"
            "Masalan: `1001`",
            parse_mode="Markdown"
        )
        return

    movie = db.get_movie_by_code(text)

    if not movie:
        await update.message.reply_text(
            f"❌ *{text}* kodi bo'yicha kino topilmadi.",
            parse_mode="Markdown"
        )
        return

    movie_id, code, name, description, file_id, file_type = movie

    caption = (
        f"🎬 *{name}*\n"
        f"📌 Kod: `{code}`"
    )

    if description:
        caption += f"\n\n📝 {description}"

    try:
        if file_type == "video":
            await update.message.reply_video(
                video=file_id,
                caption=caption,
                parse_mode="Markdown"
            )

        elif file_type == "document":
            await update.message.reply_document(
                document=file_id,
                caption=caption,
                parse_mode="Markdown"
            )

        else:
            await update.message.reply_text(
                "❌ Fayl turi noto'g'ri."
            )

    except Exception as e:
        logger.error(f"Kino yuborishda xato: {e}")

        await update.message.reply_text(
            "⚠️ Kino yuborishda xatolik yuz berdi."
        )


# ===================== ADMIN PANEL =====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(
            "❌ Siz admin emassiz!"
        )
        return

    keyboard = [
        [InlineKeyboardButton("➕ Kino qo'shish", callback_data="admin_add")],
        [InlineKeyboardButton("📋 Kinolar ro'yxati", callback_data="admin_list")],
        [InlineKeyboardButton("🗑 Kino o'chirish", callback_data="admin_delete")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Kanallar", callback_data="admin_channels")]
    ]

    await update.message.reply_text(
        "👨‍💼 *Admin Panel*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===================== CALLBACK HANDLER =====================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.edit_message_text(
            "❌ Siz admin emassiz!"
        )
        return

    data = query.data
    # ================= CHANNELS =================

    if data == "admin_channels":

        keyboard = [

            [InlineKeyboardButton(
                "➕ Kanal qo'shish",
                callback_data="add_channel"
            )],

            [InlineKeyboardButton(
                "🗑 Kanal o'chirish",
                callback_data="delete_channel"
            )],

            [InlineKeyboardButton(
                "🔙 Orqaga",
                callback_data="admin_back"
            )]
        ]

        await query.edit_message_text(
            "📢 Kanal boshqaruvi",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    elif data == "add_channel":

        context.user_data["state"] = "waiting_channel"

        await query.edit_message_text(
            "📢 Kanal username yuboring.\n\n"
            "Masalan:\n"
            "@mychannel"
        )

    # ================= ADD MOVIE =================

    elif data == "admin_add":

        context.user_data["state"] = "waiting_code"

        await query.edit_message_text(
            "➕ *Yangi kino qo'shish*\n\n"
            "🎬 Kino kodini yuboring.\n"
            "Masalan: `1001`",
            parse_mode="Markdown"
        )

        # ================= CHANNEL DELETE =================

    elif data == "delete_channel":

        channels = db.get_channels()

        if not channels:
            await query.edit_message_text(
                "❌ Kanallar yo'q"
            )

            return

        keyboard = []

        for channel in channels:
            keyboard.append([

                InlineKeyboardButton(
                    channel[2],
                    callback_data=f"del_channel_{channel[1]}"
                )

            ])

        await query.edit_message_text(
            "🗑 O'chiriladigan kanalni tanlang",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    elif data.startswith("del_channel_"):

        channel_id = data.replace(
            "del_channel_",
            ""
        )

        db.delete_channel(channel_id)

        await query.edit_message_text(
            "✅ Kanal o'chirildi"
        )


    elif data == "check_sub":

        is_subscribed = await check_subscription(
            query.from_user.id,
            context.bot
        )

        if is_subscribed:

            await query.message.delete()

            await query.message.reply_text(
                "✅ Obuna tasdiqlandi"
            )

        else:

            await query.answer(
                "❌ Hali barcha kanallarga obuna bo'lmagansiz",
                show_alert=True
            )

    # ================= LIST MOVIES =================

    elif data == "admin_list":
        movies = db.get_all_movies()

        if not movies:
            await query.edit_message_text(
                "📭 Hozircha kinolar yo'q."
            )
            return

        text = "📋 *Kinolar ro'yxati*\n\n"

        for movie in movies[:20]:
            text += (
                f"🎬 *{movie[2]}*\n"
                f"📌 Kod: `{movie[1]}`\n\n"
            )

        if len(movies) > 20:
            text += f"... va yana {len(movies) - 20} ta kino"

        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
        ]

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ================= DELETE MOVIE =================

    elif data == "admin_delete":
        context.user_data["state"] = "waiting_delete_code"

        await query.edit_message_text(
            "🗑 O'chirmoqchi bo'lgan kino kodini yuboring:",
            parse_mode="Markdown"
        )

    # ================= STATS =================

    elif data == "admin_stats":
        count = db.get_movie_count()

        keyboard = [
            [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
        ]

        await query.edit_message_text(
            f"📊 *Statistika*\n\n🎬 Jami kinolar: *{count}* ta",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ================= BACK =================

    elif data == "admin_back":
        keyboard = [
            [InlineKeyboardButton("➕ Kino qo'shish", callback_data="admin_add")],
            [InlineKeyboardButton("📋 Kinolar ro'yxati", callback_data="admin_list")],
            [InlineKeyboardButton("🗑 Kino o'chirish", callback_data="admin_delete")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")]
        ]

        await query.edit_message_text(
            "👨‍💼 *Admin Panel*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ================= CONFIRM DELETE =================

    elif data.startswith("confirm_delete_"):
        code = data.replace("confirm_delete_", "")

        db.delete_movie_by_code(code)

        context.user_data.clear()

        await query.edit_message_text(
            f"✅ `{code}` kodli kino o'chirildi.",
            parse_mode="Markdown"
        )

    # ================= CANCEL DELETE =================

    elif data == "cancel_delete":
        context.user_data.clear()

        await query.edit_message_text(
            "❌ O'chirish bekor qilindi."
        )


# ===================== ADMIN TEXT HANDLER =====================

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state")

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # ================= WAITING CODE =================

    if state == "waiting_code":

        if not text.isdigit():
            await update.message.reply_text(
                "❌ Faqat raqam yuboring!"
            )
            return

        if db.get_movie_by_code(text):
            await update.message.reply_text(
                f"❌ `{text}` kodi mavjud!",
                parse_mode="Markdown"
            )
            return

        context.user_data["new_movie_code"] = text
        context.user_data["state"] = "waiting_name"

        await update.message.reply_text(
            "✅ Kod saqlandi.\n\n"
            "2️⃣ Kino nomini yuboring:"
        )

    # ================= WAITING NAME =================

    elif state == "waiting_name":

        context.user_data["new_movie_name"] = text
        context.user_data["state"] = "waiting_description"

        await update.message.reply_text(
            "3️⃣ Kino tavsifini yuboring.\n\n"
            "O'tkazib yuborish uchun `/skip` yuboring.",
            parse_mode="Markdown"
        )

    # ================= WAITING DESCRIPTION =================

    elif state == "waiting_description":

        if text == "/skip":
            description = ""
        else:
            description = text

        context.user_data["new_movie_description"] = description
        context.user_data["state"] = "waiting_file"

        await update.message.reply_text(
            "4️⃣ Endi video yoki dokument yuboring."
        )

    # ================= WAITING DELETE CODE =================

    elif state == "waiting_delete_code":

        if not text.isdigit():
            await update.message.reply_text(
                "❌ Faqat raqam yuboring!"
            )
            return

        movie = db.get_movie_by_code(text)

        if not movie:
            await update.message.reply_text(
                "❌ Kino topilmadi."
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Ha",
                    callback_data=f"confirm_delete_{text}"
                ),
                InlineKeyboardButton(
                    "❌ Yo'q",
                    callback_data="cancel_delete"
                )
            ]
        ]

        await update.message.reply_text(
            f"⚠️ *{movie[2]}* kinoni o'chirasizmi?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    # ================= WAITING CHANNEL =================

    elif state == "waiting_channel":

        channel_id = text

        try:

            chat = await context.bot.get_chat(
                channel_id
            )

            db.add_channel(
                channel_id,
                chat.title
            )

            context.user_data.clear()

            await update.message.reply_text(
                f"✅ Kanal qo'shildi:\n{chat.title}"
            )

        except Exception as e:

            await update.message.reply_text(
                f"❌ Xato:\n{e}"
            )

# ===================== ADMIN FILE HANDLER =====================

async def handle_admin_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state")

    if state != "waiting_file":
        return

    file_id = None
    file_type = None

    # ================= VIDEO =================

    if update.message.video:
        file_id = update.message.video.file_id
        file_type = "video"

    # ================= DOCUMENT =================

    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"

    else:
        await update.message.reply_text(
            "❌ Video yoki dokument yuboring!"
        )
        return

    code = context.user_data.get("new_movie_code")
    name = context.user_data.get("new_movie_name")
    description = context.user_data.get(
        "new_movie_description",
        ""
    )

    db.add_movie(
        code,
        name,
        description,
        file_id,
        file_type
    )

    context.user_data.clear()

    await update.message.reply_text(
        f"✅ *Kino qo'shildi!*\n\n"
        f"🎬 Nom: *{name}*\n"
        f"📌 Kod: `{code}`\n"
        f"📁 Turi: *{file_type}*",
        parse_mode="Markdown"
    )


# ===================== MAIN =====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_panel))

    # Callback
    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    # Admin file handler
    app.add_handler(
        MessageHandler(
            filters.User(ADMIN_IDS)
            & (filters.VIDEO | filters.Document.ALL),
            handle_admin_file
        )
    )

    # Admin text handler
    app.add_handler(
        MessageHandler(
            filters.User(ADMIN_IDS)
            & filters.TEXT,
            handle_admin_input
        )
    )

    # User code handler
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_code
        )
    )

    logger.info("✅ Bot ishga tushdi...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ===================== START =====================

if __name__ == "__main__":
    main()
