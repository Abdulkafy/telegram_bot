from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_ID, PRODUCT_TYPES, PRICES
from database import db
from api_handler import api_handler
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# لوحة المفاتيح الرئيسية
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 شراء حسابات", callback_data="buy_accounts")],
        [InlineKeyboardButton("📱 شراء أرقام تفعيل", callback_data="buy_activation")],
        [InlineKeyboardButton("💼 عرض حساباتي", callback_data="my_accounts")],
        [InlineKeyboardButton("👤 الدعم الفني", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # إضافة المستخدم إلى قاعدة البيانات
    db.add_user(user_id, user.username, user.first_name)
    
    welcome_text = f"""
    🎯 أهلاً وسهلاً {user.first_name}!

    🤖 **بوت بيع وشراء الحسابات وأرقام التفعيل**

    🛍️ **الخدمات المتاحة:**
    • 📲 حسابات التواصل الاجتماعي
    • 🔢 أرقام التفعيل لجميع البرامج
    • ⚡ خدمة سريعة ومضمونة

    اختر من الخيارات أدناه 👇
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_keyboard(),
        parse_mode='Markdown'
    )

# معالجة الأزرار
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "buy_accounts":
        await show_accounts_menu(query)
    elif data == "buy_activation":
        await show_activation_menu(query)
    elif data == "my_accounts":
        await show_my_accounts(query)
    elif data == "support":
        await show_support(query)
    elif data.startswith("buy_"):
        await process_purchase(query, data)

# عرض قائمة الحسابات
async def show_accounts_menu(query):
    keyboard = [
        [InlineKeyboardButton("📸 إنستجرام", callback_data="buy_instagram")],
        [InlineKeyboardButton("📘 فيسبوك", callback_data="buy_facebook")],
        [InlineKeyboardButton("💬 واتساب", callback_data="buy_whatsapp")],
        [InlineKeyboardButton("📱 تليجرام", callback_data="buy_telegram")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📲 **اختر نوع الحساب:**\n\n"
        "• إنستجرام: 50 ريال 💰\n"
        "• فيسبوك: 30 ريال 💰\n"
        "• واتساب: 25 ريال 💰\n"
        "• تليجرام: 20 ريال 💰\n\n"
        "اختر النوع الذي تريده:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# عرض قائمة أرقام التفعيل
async def show_activation_menu(query):
    keyboard = [
        [InlineKeyboardButton("🔢 شراء رقم تفعيل", callback_data="buy_activation_number")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📱 **أرقام التفعيل:**\n\n"
        "• رقم تفعيل لجميع البرامج: 10 ريال 💰\n\n"
        "اضغط على الزر أدناه للشراء:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# معالجة عملية الشراء
async def process_purchase(query, product_type):
    user_id = query.from_user.id
    product_map = {
        "buy_instagram": ("instagram", "إنستجرام", 50),
        "buy_facebook": ("facebook", "فيسبوك", 30),
        "buy_whatsapp": ("whatsapp", "واتساب", 25),
        "buy_telegram": ("telegram", "تليجرام", 20),
        "buy_activation_number": ("activation", "رقم تفعيل", 10)
    }
    
    platform, platform_name, price = product_map.get(product_type, ("", "", 0))
    
    if platform:
        # هنا يمكنك إضافة المنتج إلى قاعدة البيانات
        order_id = db.create_order(user_id, platform)
        
        if order_id:
            # مزامنة الطلب مع الموقع
            order_data = {
                "user_id": user_id,
                "product_type": platform,
                "product_name": platform_name,
                "price": price,
                "order_id": order_id
            }
            
            sync_success = api_handler.sync_order(order_data)
            
            success_text = f"""
            ✅ **تمت العملية بنجاح!**

            🛍️ **المنتج:** {platform_name}
            💰 **السعر:** {price} ريال
            🆔 **رقم الطلب:** {order_id}

            📞 **للحصول على المنتج:** 
            تواصل مع الدعم الفني وأعرض رقم طلبك.
            """
            
            if sync_success:
                success_text += "\n\n✅ تم مزامنة الطلب مع الموقع"
            else:
                success_text += "\n\n⚠️ لم يتم المزامنة مع الموقع - تواصل مع الدعم"
            
        else:
            success_text = "❌ حدث خطأ في إنشاء الطلب، حاول مرة أخرى."
        
        keyboard = [[InlineKeyboardButton("🔙 الرجوع للقائمة", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            success_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# عرض حسابات المستخدم
async def show_my_accounts(query):
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📋 **حساباتي المشتراة:**\n\n"
        "سيتم عرض الحسابات التي اشتريتها هنا...\n\n"
        "⏳ هذه الميزة قيد التطوير",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# عرض الدعم الفني
async def show_support(query):
    support_text = """
    📞 **الدعم الفني:**
    
    للاستفسارات أو المشاكل:
    
    • تواصل مع المسؤول مباشرة
    • أو راسلنا على: @دعم_البوت
    
    ⏰ **أوقات الدعم:**
    24 ساعة طوال الأسبوع
    """
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        support_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# الرجوع للقائمة الرئيسية
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🏠 **القائمة الرئيسية**\n\nاختر الخدمة التي تريدها:",
        reply_markup=main_keyboard(),
        parse_mode='Markdown'
    )

def main():
    # إنشاء تطبيق البوت
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button, pattern="^(?!back_main).*"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_main$"))
    
    # بدء البوت
    print("🤖 البوت يعمل الآن...")
    application.run_polling()

if __name__ == "__main__":
    main()