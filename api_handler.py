```python
import requests
import json
from config import API_KEY, WEBSITE_API_URL

class APIHandler:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = WEBSITE_API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'X-API-Key': self.api_key
        }
    
    def sync_order(self, order_data):
        """مزامنة الطلب مع الموقع"""
        try:
            response = requests.post(
                f"{self.base_url}/orders",
                headers=self.headers,
                json=order_data,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_user_balance(self, user_id):
        """جلب رصيد المستخدم من الموقع"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}/balance",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('balance', 0)
            return 0
        except:
            return 0

api_handler = APIHandler()
```
