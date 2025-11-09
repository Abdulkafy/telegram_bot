import sqlite3
import logging

# استيراد الإعدادات من config
try:
    from config import DATABASE_URL, DEBUG
except ImportError:
    # قيم افتراضية إذا فشل الاستيراد
    DATABASE_URL = 'sqlite:///bot_database.db'
    DEBUG = True

class Database:
    def __init__(self):
        self.db_path = DATABASE_URL.replace('sqlite:///', '')
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """إنشاء اتصال بقاعدة البيانات"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            if DEBUG:
                logging.info("Connected to database successfully")  # بدون رموز تعبيرية
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise
    
    def create_tables(self):
        """إنشاء الجداول إذا لم تكن موجودة"""
        try:
            # جدول المستخدمين
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المنتجات
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    details TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الطلبات
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    price REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            self.conn.commit()
            
            # إضافة بعض المنتجات الافتراضية إذا لم تكن موجودة
            self.add_default_products()
            
            if DEBUG:
                logging.info("Database tables created successfully")  # بدون رموز تعبيرية
                
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            raise
    
    def add_default_products(self):
        """إضافة منتجات افتراضية"""
        default_products = [
            ('accounts', 'instagram', 'حساب انستجرام ميمز', 50, 10),
            ('accounts', 'facebook', 'حساب فيسبوك نشط', 30, 10),
            ('accounts', 'whatsapp', 'حساب واتساب مفعل', 25, 10),
            ('accounts', 'telegram', 'حساب تليجرام جديد', 20, 10),
            ('activation', 'all', 'رقم تفعيل لجميع البرامج', 10, 50)
        ]
        
        try:
            for product in default_products:
                # التحقق إذا كان المنتج موجوداً مسبقاً
                cursor = self.conn.execute(
                    'SELECT id FROM products WHERE product_type = ? AND platform = ?',
                    (product[0], product[1])
                )
                if not cursor.fetchone():
                    self.conn.execute('''
                        INSERT INTO products 
                        (product_type, platform, details, price, quantity)
                        VALUES (?, ?, ?, ?, ?)
                    ''', product)
            
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding default products: {e}")
    
    def add_user(self, user_id, username, first_name):
        """إضافة مستخدم جديد"""
        try:
            self.conn.execute(
                'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
                (user_id, username, first_name)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding user: {e}")
            return False
    
    def get_products(self, product_type=None):
        """جلب المنتجات المتاحة"""
        try:
            if product_type:
                cursor = self.conn.execute(
                    'SELECT * FROM products WHERE product_type = ? AND quantity > 0 AND is_active = 1',
                    (product_type,)
                )
            else:
                cursor = self.conn.execute(
                    'SELECT * FROM products WHERE quantity > 0 AND is_active = 1'
                )
            
            products = [dict(row) for row in cursor.fetchall()]
            return products
        except sqlite3.Error as e:
            logging.error(f"Error getting products: {e}")
            return []
    
    def create_order(self, user_id, product_type, platform, price, details=""):
        """إنشاء طلب جديد"""
        try:
            cursor = self.conn.execute(
                '''INSERT INTO orders 
                (user_id, product_type, platform, price, details) 
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, product_type, platform, price, details)
            )
            order_id = cursor.lastrowid
            self.conn.commit()
            return order_id
        except sqlite3.Error as e:
            logging.error(f"Error creating order: {e}")
            return None
    
    def get_user_orders(self, user_id):
        """جلب طلبات المستخدم"""
        try:
            cursor = self.conn.execute(
                'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            orders = [dict(row) for row in cursor.fetchall()]
            return orders
        except sqlite3.Error as e:
            logging.error(f"Error getting user orders: {e}")
            return []

# إنشاء instance من قاعدة البيانات
db = Database()