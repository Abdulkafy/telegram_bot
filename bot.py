from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_ID, PRODUCT_TYPES, PRICES, DEBUG
from database import db
from api_handler import api_handler
import logging
import sys

# إعداد التسجيل
logger = logging.getLogger(__name__)

# دالة طباعة آمنة للويندوز
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # إزالة الرموز التعبيرية إذا فشل الطباعة
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

# لوحة المفاتيح الرئيسية
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("شراء حسابات", callback_data="buy_accounts")],
        [InlineKeyboardButton("شراء ارقام تفعيل", callback_data="buy_activation")],
        [InlineKeyboardButton("طلباتي", callback_data="my_orders")],
        [InlineKeyboardButton("الدعم الفني", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # إضافة المستخدم إلى قاعدة البيانات
    db.add_user(user_id, user.username, user.first_name)
    
    welcome_text = f"""
    اهلاً وسهلاً {user.first_name}!

    بوت بيع وشراء الحسابات وارقام التفعيل

    الخدمات المتاحة:
    - حسابات التواصل الاجتماعي
    - ارقام التفعيل لجميع البرامج
    - خدمة سريعة ومضمونة

    اختر من الخيارات ادناه
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
    elif data == "my_orders":
        await show_my_orders(query)
    elif data == "support":
        await show_support(query)
    elif data.startswith("buy_"):
        await process_purchase(query, data)
    else:
        await query.edit_message_text("خيار غير معروف")

# عرض قائمة الحسابات
async def show_accounts_menu(query):
    keyboard = [
        [InlineKeyboardButton("انستجرام", callback_data="buy_instagram")],
        [InlineKeyboardButton("فيسبوك", callback_data="buy_facebook")],
        [InlineKeyboardButton("واتساب", callback_data="buy_whatsapp")],
        [InlineKeyboardButton("تليجرام", callback_data="buy_telegram")],
        [InlineKeyboardButton("رجوع", callback_data="back_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "اختر نوع الحساب:\n\n"
        "- انستجرام: 50 ريال\n"
        "- فيسبوك: 30 ريال\n"
        "- واتساب: 25 ريال\n"
        "- تليجرام: 20 ريال\n\n"
        "اختر النوع الذي تريده:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# عرض قائمة ارقام التفعيل
async def show_activation_menu(query):
    keyboard = [
        [InlineKeyboardButton("شراء رقم تفعيل", callback_data="buy_activation_number")],
        [InlineKeyboardButton("رجوع", callback_data="back_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "ارقام التفعيل:\n\n"
        "- رقم تفعيل لجميع البرامج: 10 ريال\n\n"
        "اضغط على الزر ادناه للشراء:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# معالجة عملية الشراء
async def process_purchase(query, product_type):
    user_id = query.from_user.id
    product_map = {
        "buy_instagram": ("accounts", "انستجرام", 50),
        "buy_facebook": ("accounts", "فيسبوك", 30),
        "buy_whatsapp": ("accounts", "واتساب", 25),
        "buy_telegram": ("accounts", "تليجرام", 20),
        "buy_activation_number": ("activation", "رقم تفعيل", 10)
    }
    
    platform, platform_name, price = product_map.get(product_type, ("", "", 0))
    
    if platform:
        # إنشاء الطلب في قاعدة البيانات
        order_id = db.create_order(user_id, platform, platform_name, price)
        
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
            تمت العملية بنجاح!

            المنتج: {platform_name}
            السعر: {price} ريال
            رقم الطلب: {order_id}

            للحصول على المنتج: 
            تواصل مع الدعم الفني واعرض رقم طلبك.
            """
            
            if sync_success:
                success_text += "\n\nتم مزامنة الطلب مع الموقع"
            else:
                success_text += "\n\nلم يتم المزامنة مع الموقع - تواصل مع الدعم"
            
        else:
            success_text = "حدث خطأ في إنشاء الطلب، حاول مرة أخرى."
        
        keyboard = [[InlineKeyboardButton("الرجوع للقائمة", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            success_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# عرض طلبات المستخدم
async def show_my_orders(query):
    user_id = query.from_user.id
    orders = db.get_user_orders(user_id)
    
    if orders:
        orders_text = "طلباتك السابقة:\n\n"
        for order in orders:
            status_icon = "مكتمل" if order['status'] == 'completed' else "قيد الانتظار"
            orders_text += f"طلب #{order['id']} - {order['platform']} - {order['price']} ريال - {order['status']}\n"
    else:
        orders_text = "لا توجد طلبات سابقة\n\nلم تقم بأي طلبات حتى الآن."
    
    keyboard = [[InlineKeyboardButton("رجوع", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        orders_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# أمر طلباتي عبر command
async def show_my_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = db.get_user_orders(user_id)
    
    if orders:
        orders_text = "طلباتك السابقة:\n\n"
        for order in orders:
            status_icon = "مكتمل" if order['status'] == 'completed' else "قيد الانتظار"
            orders_text += f"طلب #{order['id']} - {order['platform']} - {order['price']} ريال - {order['status']}\n"
    else:
        orders_text = "لا توجد طلبات سابقة\n\nلم تقم بأي طلبات حتى الآن."
    
    await update.message.reply_text(orders_text, parse_mode='Markdown')

# عرض الدعم الفني
async def show_support(query):
    support_text = """
    الدعم الفني:
    
    للاستفسارات أو المشاكل:
    
    - تواصل مع المسؤول مباشرة
    - أو راسلنا على: @دعم_البوت
    
    اوقات الدعم:
    24 ساعة طوال الاسبوع
    """
    
    keyboard = [[InlineKeyboardButton("رجوع", callback_data="back_main")]]
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
        "القائمة الرئيسية\n\nاختر الخدمة التي تريدها:",
        reply_markup=main_keyboard(),
        parse_mode='Markdown'
    )

# أمر المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    دليل استخدام البوت:

    /start - بدء استخدام البوت
    /help - عرض هذه المساعدة
    /myorders - عرض طلباتي

    عملية الشراء:
    1. اختر نوع الخدمة
    2. اختر المنتج المناسب
    3. اتبع التعليمات
    4. تواصل مع الدعم لاكمال العملية
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    try:
        # إنشاء تطبيق البوت
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("myorders", show_my_orders_command))
        application.add_handler(CallbackQueryHandler(handle_button, pattern="^(?!back_main).*"))
        application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_main$"))
        
        # بدء البوت
        logger.info("البوت يعمل الآن...")
        safe_print("البوت يعمل الآن...")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"فشل في تشغيل البوت: {e}")
        safe_print(f"فشل في تشغيل البوت: {e}")
        raise

if __name__ == "__main__":
    main()