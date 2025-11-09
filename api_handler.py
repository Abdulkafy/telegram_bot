import requests
import logging
from config import DECODED_API_KEY, WEBSITE_API_URL, DEBUG

class APIHandler:
    def __init__(self):
        self.api_key = DECODED_API_KEY
        self.base_url = WEBSITE_API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'X-API-Key': self.api_key,
            'User-Agent': 'TelegramBot/1.0'
        }
        self.timeout = 30
    
    def sync_order(self, order_data):
        """مزامنة الطلب مع الموقع"""
        try:
            if DEBUG:
                logging.info(f"Syncing order with website: {order_data}")
            
            # محاكاة نجاح المزامنة إذا لم يكن الموقع جاهزاً
            if "your-website.com" in self.base_url:
                logging.info("Using mock API sync (website not configured)")
                return True
            
            response = requests.post(
                f"{self.base_url}/orders",
                headers=self.headers,
                json=order_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logging.info("Order synced successfully with website")
                return True
            else:
                logging.warning(f"API returned status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return False

# إنشاء instance من API Handler
api_handler = APIHandler()