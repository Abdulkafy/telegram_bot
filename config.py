```python
import base64
from decouple import config

# إعدادات بوت تليجرام
BOT_TOKEN = "8526176589:AAF-Tj1tXNVv-7FHpukPx7rBOmMmpB5H73Q"
ADMIN_ID = 7700286311

# فك تشفير API Key
def get_api_key():
    encrypted_api_key = "aGN0cVhleDM2OHRmVW53eHhjbmVZZz09"
    try:
        decoded = base64.b64decode(encrypted_api_key).decode('utf-8')
        return decoded
    except:
        return encrypted_api_key

API_KEY = get_api_key()
WEBSITE_API_URL = "https://your-website.com/api"  # ضع رابط API الخاص بك هنا

# أنواع المنتجات
PRODUCT_TYPES = {
    "accounts": "حسابات التواصل الاجتماعي",
    "activation": "أرقام التفعيل"
}

# أسعار المنتجات (يمكن تعديلها)
PRICES = {
    "instagram": 50,
    "facebook": 30,
    "whatsapp": 25,
    "telegram": 20,
    "activation_number": 10
}
```