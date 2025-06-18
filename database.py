import sqlite3
import asyncio
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    async def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                message TEXT,
                remind_time DATETIME,
                is_sent BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                message_text TEXT,
                is_bot_message BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_chats (
                chat_id INTEGER PRIMARY KEY,
                chat_title TEXT,
                last_message_time DATETIME,
                last_joke_time DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def add_user(self, user_id, username, first_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name) 
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        conn.commit()
        conn.close()
    
    async def add_reminder(self, user_id, chat_id, message, remind_time):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (user_id, chat_id, message, remind_time) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, chat_id, message, remind_time))
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id
    
    async def get_pending_reminders(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, chat_id, message, remind_time 
            FROM reminders 
            WHERE is_sent = 0 AND remind_time <= ?
        ''', (datetime.now(),))
        reminders = cursor.fetchall()
        conn.close()
        return reminders
    
    async def mark_reminder_sent(self, reminder_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE reminders SET is_sent = 1 WHERE id = ?', (reminder_id,))
        conn.commit()
        conn.close()
    
    async def add_chat_message(self, chat_id, user_id, username, message_text, is_bot_message=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (chat_id, user_id, username, message_text, is_bot_message) 
            VALUES (?, ?, ?, ?, ?)
        ''', (chat_id, user_id, username, message_text, is_bot_message))
        conn.commit()
        conn.close()
    
    async def get_chat_history(self, chat_id, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username, message_text, is_bot_message, created_at
            FROM chat_history 
            WHERE chat_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (chat_id, limit))
        history = cursor.fetchall()
        conn.close()
        return list(reversed(history))
    
    async def clear_old_chat_history(self, chat_id, keep_last=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM chat_history 
            WHERE chat_id = ? AND id NOT IN (
                SELECT id FROM chat_history 
                WHERE chat_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            )
        ''', (chat_id, chat_id, keep_last))
        conn.commit()
        conn.close()
    
    async def add_or_update_group_chat(self, chat_id, chat_title):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO group_chats (chat_id, chat_title, last_message_time) 
            VALUES (?, ?, ?)
        ''', (chat_id, chat_title, datetime.now()))
        conn.commit()
        conn.close()
    
    async def update_last_message_time(self, chat_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE group_chats SET last_message_time = ? WHERE chat_id = ?
        ''', (datetime.now(), chat_id))
        conn.commit()
        conn.close()
    
    async def get_groups_for_jokes(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chat_id, chat_title, last_message_time, last_joke_time
            FROM group_chats 
            WHERE is_active = 1
        ''')
        groups = cursor.fetchall()
        conn.close()
        return groups
    
    async def update_last_joke_time(self, chat_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE group_chats SET last_joke_time = ? WHERE chat_id = ?
        ''', (datetime.now(), chat_id))
        conn.commit()
        conn.close()

db = Database() 