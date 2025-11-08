```python
import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot_database.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        # جدول المستخدمين
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنتجات
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_type TEXT,
                platform TEXT,
                details TEXT,
                price REAL,
                quantity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الطلبات
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name):
        """إضافة مستخدم جديد"""
        try:
            self.conn.execute(
                'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                (user_id, username, first_name)
            )
            self.conn.commit()
            return True
        except:
            return False
    
    def get_products(self, product_type=None):
        """جلب المنتجات المتاحة"""
        try:
            if product_type:
                cursor = self.conn.execute(
                    'SELECT * FROM products WHERE product_type = ? AND quantity > 0',
                    (product_type,)
                )
            else:
                cursor = self.conn.execute('SELECT * FROM products WHERE quantity > 0')
            
            products = cursor.fetchall()
            return products
        except:
            return []
    
    def create_order(self, user_id, product_id):
        """إنشاء طلب جديد"""
        try:
            cursor = self.conn.execute(
                'INSERT INTO orders (user_id, product_id) VALUES (?, ?)',
                (user_id, product_id)
            )
            order_id = cursor.lastrowid
            self.conn.commit()
            return order_id
        except:
            return None

# إنشاء instance من قاعدة البيانات
db = Database()
```