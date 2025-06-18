import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router, set_bot_username
from database import db
from reminder_scheduler import ReminderScheduler

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    me = await bot.get_me()
    print(f"Бот запущен: @{me.username}")
    
    # Устанавливаем имя пользователя бота
    set_bot_username(me.username)
    
    dp.include_router(router)
    
    scheduler = ReminderScheduler(bot)
    
    try:
        await db.init_db()
        
        scheduler_task = asyncio.create_task(scheduler.start_scheduler())
        
        print("Бот готов к работе!")
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        print("Остановка бота...")
    finally:
        scheduler.stop_scheduler()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 