import base64
import os
import logging
import sys

# إعداد ترميز UTF-8 للنظام
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # للتوافق مع إصدارات Python القديمة
        import codecs
        if sys.version_info.major == 3 and sys.version_info.minor >= 7:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# إعدادات بوت تليجرام - قيم مباشرة
BOT_TOKEN = '8526176589:AAF-Tj1tXNVv-7FHpukPx7rBOmMmpB5H73Q'
ADMIN_ID = 7700286311

# إعدادات API
API_KEY = 'aGN0cVhleDM2OHRmVW53eHhjbmVZZz09'
WEBSITE_API_URL = 'https://your-website.com/api'

# إعدادات قاعدة البيانات
DATABASE_URL = 'sqlite:///bot_database.db'

# إعدادات التطوير
DEBUG = True
LOG_LEVEL = 'INFO'

# فك تشفير API Key إذا كان مشفراً base64
def get_decoded_api_key():
    try:
        if API_KEY and '=' in API_KEY:
            decoded = base64.b64decode(API_KEY).decode('utf-8')
            return decoded
        return API_KEY
    except Exception as e:
        logging.warning(f"Failed to decode API key: {e}")
        return API_KEY

DECODED_API_KEY = get_decoded_api_key()

# أنواع المنتجات
PRODUCT_TYPES = {
    "accounts": "حسابات التواصل الاجتماعي",
    "activation": "ارقام التفعيل"
}

# أسعار المنتجات
PRICES = {
    "instagram": 50,
    "facebook": 30,
    "whatsapp": 25,
    "telegram": 20,
    "activation_number": 10
}

# إعدادات التسجيل بدون رموز تعبيرية
def setup_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # إعداد formatter بدون رموز تعبيرية
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler لل console بدون رموز تعبيرية
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Handler لل file
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=level,
        handlers=[console_handler, file_handler]
    )

# التحقق من الإعدادات المطلوبة
def validate_config():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")
    
    if DEBUG:
        logging.info("Running in DEBUG mode")
    
    logging.info("Configuration loaded successfully")

# تهيئة التسجيل والتحقق من الإعدادات
setup_logging()
validate_config()