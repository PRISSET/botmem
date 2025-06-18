import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import FSInputFile
import os
from database import db
from ai_service import ai_service
from voice_service import voice_service

class ReminderScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.is_running = False
    
    async def start_scheduler(self):
        self.is_running = True
        while self.is_running:
            try:
                await self.check_and_send_reminders()
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(60)
    
    async def send_voice_reminder(self, chat_id: int, text: str):
        try:
            voice_path = await voice_service.create_voice_message_async(text)
            voice_file = FSInputFile(voice_path)
            await self.bot.send_voice(chat_id=chat_id, voice=voice_file)
            os.unlink(voice_path)
        except Exception as e:
            print(f"Ошибка создания голосового напоминания: {e}")
            await self.bot.send_message(chat_id=chat_id, text=text)
    
    async def check_and_send_reminders(self):
        reminders = await db.get_pending_reminders()
        
        for reminder in reminders:
            reminder_id, user_id, chat_id, message, remind_time = reminder
            
            try:
                reminder_text = f"Эй йоу чувак, напоминание от твоего свагового брата!\n\n{message}"
                await self.send_voice_reminder(chat_id, reminder_text)
                await db.mark_reminder_sent(reminder_id)
                print(f"Отправлено голосовое напоминание {reminder_id}")
            except Exception as e:
                print(f"Ошибка отправки напоминания {reminder_id}: {e}")
    
    def stop_scheduler(self):
        self.is_running = False 