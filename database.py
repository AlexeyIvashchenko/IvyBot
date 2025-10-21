import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bookings.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Создает таблицы в базе данных"""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                booking_date TEXT,
                status TEXT DEFAULT 'active',
                deposit_paid BOOLEAN DEFAULT FALSE,
                final_paid BOOLEAN DEFAULT FALSE,
                brief_completed BOOLEAN DEFAULT FALSE,
                payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                payment_id TEXT UNIQUE,
                amount REAL,
                payment_type TEXT,
                status TEXT DEFAULT 'pending',
                booking_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def add_booking(self, user_id, username, full_name, booking_date):
        """Добавляет бронирование в базу"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (user_id, username, full_name, booking_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, booking_date, "active"))
        self.conn.commit()
        return cursor.lastrowid

    def save_payment_info(self, user_id, payment_id, amount, booking_date, payment_type):
        """Сохраняет информацию о платеже"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, payment_id, amount, payment_type, booking_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, payment_id, amount, payment_type, booking_date))
        self.conn.commit()

    def update_payment_status(self, payment_id, status):
        """Обновляет статус платежа"""
        cursor = self.conn.cursor()

        # Сначала обновляем статус в таблице payments
        cursor.execute('''
            UPDATE payments SET status = ? WHERE payment_id = ?
        ''', (status, payment_id))

        if status == 'succeeded':
            # Ищем соответствующее бронирование
            payment_info = self.get_payment_info(payment_id)
            if payment_info:
                user_id, payment_type, booking_date = payment_info[0], payment_info[3], payment_info[4]
                logger.info(f"Обновление бронирования: user_id={user_id}, type={payment_type}, date={booking_date}")

                if payment_type == 'deposit':
                    # Обновляем статус предоплаты
                    cursor.execute('''
                        UPDATE bookings SET deposit_paid = TRUE 
                        WHERE user_id = ? AND booking_date = ?
                    ''', (user_id, booking_date))
                    logger.info(f"Предоплата подтверждена для user_id={user_id}, date={booking_date}")
                elif payment_type == 'final':
                    # Обновляем статус финальной оплаты
                    cursor.execute('''
                        UPDATE bookings SET final_paid = TRUE 
                        WHERE user_id = ? AND booking_date = ?
                    ''', (user_id, booking_date))
                    logger.info(f"Финальная оплата подтверждена для user_id={user_id}, date={booking_date}")

        self.conn.commit()

    def get_payment_info(self, payment_id):
        """Получает информацию о платеже"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, payment_id, amount, payment_type, booking_date 
            FROM payments WHERE payment_id = ?
        ''', (payment_id,))
        return cursor.fetchone()

    def get_user_bookings(self, user_id):
        """Получает бронирования пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM bookings WHERE user_id = ? ORDER BY booking_date DESC
        ''', (user_id,))
        return cursor.fetchall()

    def is_date_available(self, booking_date):
        """Проверяет доступна ли дата в формате YYYY-MM-DD"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM bookings 
            WHERE booking_date = ? AND status = 'active' AND deposit_paid = TRUE
        ''', (booking_date,))
        count = cursor.fetchone()[0]

        # Также проверяем в Google Sheets через локальную логику
        # (это дополнительная проверка, основная - через booked_dates)
        logger.info(f"Проверка даты {booking_date}: найдено {count} оплаченных бронирований")
        return count == 0

    def mark_project_completed(self, user_id, booking_date):
        """Отмечает проект как завершенный"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE bookings SET status = 'completed' 
            WHERE user_id = ? AND booking_date = ?
        ''', (user_id, booking_date))
        self.conn.commit()
        logger.info(f"Проект отмечен завершенным: user_id={user_id}, date={booking_date}")

    def mark_brief_completed(self, user_id):
        """Отмечает бриф как заполненный"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE bookings SET brief_completed = TRUE WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()

    def get_today_bookings(self):
        """Получает бронирования на сегодня с предоплатой но без финальной оплаты"""
        cursor = self.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT * FROM bookings 
            WHERE booking_date = ? AND deposit_paid = TRUE AND final_paid = FALSE
        ''', (today,))
        return cursor.fetchall()

    def get_upcoming_bookings(self, days=7):
        """Получает предстоящие бронирования"""
        cursor = self.conn.cursor()
        from datetime import datetime, timedelta

        upcoming_bookings = []
        for i in range(days + 1):
            target_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute('''
                SELECT * FROM bookings 
                WHERE booking_date = ? AND deposit_paid = TRUE AND brief_completed = FALSE
            ''', (target_date,))
            upcoming_bookings.extend(cursor.fetchall())

        return upcoming_bookings

    def mark_date_as_booked(self, booking_date):
        """Отмечает дату как забронированную в базе данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE bookings SET status = 'booked' 
            WHERE booking_date = ? AND deposit_paid = TRUE
        ''', (booking_date,))
        self.conn.commit()

    def get_user_booking_date(self, user_id):
        """Получает дату бронирования пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT booking_date FROM bookings 
            WHERE user_id = ? AND deposit_paid = TRUE 
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_user_active_booking(self, user_id):
        """Получает активное бронирование пользователя (без проверки оплаты)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM bookings 
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        return cursor.fetchone()

    def get_all_user_bookings(self, user_id):
        """Получает все бронирования пользователя (для отладки)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        return cursor.fetchall()

    def get_user_booking_date(self, user_id):
        """Получает дату бронирования пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT booking_date FROM bookings 
            WHERE user_id = ? AND deposit_paid = TRUE 
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_user_booking_date(self, user_id):
        """Получает дату бронирования пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT booking_date FROM bookings 
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
