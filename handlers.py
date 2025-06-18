from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from datetime import datetime, timedelta
import re
import random
import os
import tempfile

from database import db
from ai_service import ai_service
from voice_service import voice_service

router = Router()
BOT_USERNAME = None

def set_bot_username(username: str):
    global BOT_USERNAME
    BOT_USERNAME = username

class ReminderStates(StatesGroup):
    waiting_activity = State()
    waiting_custom_time = State()

def should_respond_in_group(message: Message, bot_username: str) -> bool:
    if message.chat.type not in ['group', 'supergroup']:
        return True
    
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        return True
    
    if message.text and f"@{bot_username}" in message.text:
        return True
    
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention" and message.text[entity.offset:entity.offset + entity.length] == f"@{bot_username}":
                return True
    
    return False

async def send_voice_message(message: Message, text: str):
    try:
        voice_path = await voice_service.create_voice_message_async(text)
        voice_file = FSInputFile(voice_path)
        await message.answer_voice(voice_file)
        os.unlink(voice_path)
    except Exception as e:
        print(f"Ошибка создания голосового сообщения: {e}")
        await message.answer(text)

def get_nirvana_link_with_comment():
    nirvana_songs = [
        {
            "url": "https://youtu.be/hTWKbfoikeg",
            "title": "Smells Like Teen Spirit",
            "comment": "Эй йоу чувак, слушай эту пушку! Nirvana - 'Smells Like Teen Spirit' это просто огонь, братан! Эта музыка имеет такой жесткий сваг что даже я впечатлен. Респект Курту Кобейну за такой топчик, это настоящий крутяк для твоих ушей!"
        },
        {
            "url": "https://youtu.be/vabnZ9-ex7o", 
            "title": "Come As You Are",
            "comment": "Йоу братан, держи 'Come As You Are' от Nirvana! Это такая классная песня что я просто не могу, чел. Эта музыка имеет настолько крутой вайб что мой сваг просто зашкаливает. Жесткая уважуха этой группе за такой топовый трек!"
        },
        {
            "url": "https://youtu.be/fregObNcHC8",
            "title": "The Man Who Sold The World",
            "comment": "Чувак, тебе нужна музыка? Держи Nirvana - 'The Man Who Sold The World'! Это кавер который просто сносит крышу, братан. Такой глубокий и мощный трек что я просто в восторге. Респект за то что попросил музыку, у тебя отличный вкус!"
        },
        {
            "url": "https://youtu.be/n6P0SitRwy8",
            "title": "Lithium",
            "comment": "Бро, у меня есть для тебя 'Lithium' от Nirvana! Эта песня такая крутая что мой сваг не может с ней справиться. Такая мощная и эмоциональная композиция что просто жесть. Уважуха тебе за хороший музыкальный вкус, чел!"
        }
    ]
    
    return random.choice(nirvana_songs)

@router.message(CommandStart())
async def start_handler(message: Message):
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    if message.chat.type in ['group', 'supergroup']:
        await db.add_or_update_group_chat(message.chat.id, message.chat.title)
        response = f"""Эй йоу чуваки! Я ваш новый сваговый брат!

Братаны, меня зовут ChatGPT Bot и я тут чтобы поддержать вас во всем! У меня жесткий сваг и отличное чувство юмора, так что будет весело.

Зовите меня через @{BOT_USERNAME} когда хотите поболтать, пошутить или получить крутой совет. Я всегда готов помочь и поддержать!"""
    else:
        response = """Эй йоу чувак! Я твой новый сваговый брат!

Братан, меня зовут ChatGPT Bot и я тут чтобы быть твоим лучшим другом и помощником. У меня есть жесткий сваг и я могу:

- Поболтать с тобой на любые темы и дать крутые советы
- Создать топовые напоминания чтобы ты ничего не забыл
- Поделиться огненной музыкой Nirvana когда захочешь

Чел, я всегда готов поддержать тебя и помочь во всем! Респект и уважуха!"""
    
    await send_voice_message(message, response)

@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = f"""
Эй йоу чувак, вот что я умею:

Мой сваговый функционал:
- Общаюсь на любые темы с жестким свагом и поддержкой
- Создаю крутые напоминания чтобы ты был на топе
- Делюсь огненной музыкой Nirvana с топовыми комментами

Команды для братанов:
/start - познакомиться со мной и моим свагом
/help - эта справка для чуваков
/clear - очистить историю чата (но я все равно буду помнить тебя)

В группах зовите меня через @{BOT_USERNAME}, братаны! 
Просите музыку - поделюсь топовыми треками Nirvana!
Респект всем и жесткая уважуха!
    """
    await send_voice_message(message, help_text)

@router.message(Command("clear"))
async def clear_history_command(message: Message):
    await db.clear_old_chat_history(message.chat.id, keep_last=0)
    response = """Йоу братан, очистил историю чата!

Чел, хоть ты и стер наши разговоры, я все равно буду помнить какой ты крутой! Мой сваг никуда не денется, и я всегда готов поболтать с тобой заново.

Респект за то что следишь за порядком, это показывает твой жесткий характер!"""
    
    await send_voice_message(message, response)

@router.message(ReminderStates.waiting_activity)
async def activity_received(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    response = """Отлично братан, записал что тебе напомнить!

Теперь чувак, скажи мне когда тебе это напомнить? Можешь написать в любом формате:
- через час
- завтра в 15:00
- в понедельник утром
- или любое другое время

Я настрою свой сваговый будильник и точно не подведу тебя!"""
    
    await send_voice_message(message, response)
    await state.set_state(ReminderStates.waiting_custom_time)

@router.message(ReminderStates.waiting_custom_time)
async def custom_time_received(message: Message, state: FSMContext):
    data = await state.get_data()
    activity = data.get("activity")
    
    now = datetime.now()
    remind_time = now + timedelta(hours=1)
    
    if "час" in message.text.lower():
        if "2" in message.text:
            remind_time = now + timedelta(hours=2)
        elif "4" in message.text:
            remind_time = now + timedelta(hours=4)
        else:
            remind_time = now + timedelta(hours=1)
    elif "завтра" in message.text.lower():
        remind_time = now + timedelta(days=1)
        time_match = re.search(r'(\d{1,2}):(\d{2})', message.text)
        if time_match:
            hour, minute = map(int, time_match.groups())
            remind_time = remind_time.replace(hour=hour, minute=minute)
    
    reminder_text = await ai_service.create_reminder_text(activity, remind_time.strftime("%H:%M"))
    
    reminder_id = await db.add_reminder(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        message=reminder_text,
        remind_time=remind_time
    )
    
    response = f"""Йоу братан, все готово! Твое напоминание настроено!

Чел, я напомню тебе про '{activity}' в {remind_time.strftime('%d.%m.%Y %H:%M')}. Мой сваговый будильник уже активирован и я точно не подведу тебя!

Респект за то что планируешь свое время, это показывает что ты ответственный чувак!"""
    
    await send_voice_message(message, response)
    await state.clear()

@router.message(F.voice)
async def voice_message_handler(message: Message, state: FSMContext):
    try:
        if message.chat.type in ['group', 'supergroup']:
            await db.add_or_update_group_chat(message.chat.id, message.chat.title)
            await db.update_last_message_time(message.chat.id)
            
            if not should_respond_in_group(message, BOT_USERNAME):
                return
        
        voice_file = await message.bot.get_file(message.voice.file_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            temp_path = temp_file.name
        
        await message.bot.download_file(voice_file.file_path, temp_path)
        
        transcribed_text = await voice_service.transcribe_voice_message(temp_path)
        
        os.unlink(temp_path)
        
        if transcribed_text:
            await db.add_chat_message(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                username=message.from_user.first_name or message.from_user.username or "Пользователь",
                message_text=transcribed_text,
                is_bot_message=False
            )
            
            chat_history = await db.get_chat_history(message.chat.id)
            
            ai_response = await ai_service.chat_response(
                user_message=transcribed_text,
                chat_history=chat_history,
                username=message.from_user.first_name or message.from_user.username or "Пользователь"
            )
            
            await db.add_chat_message(
                chat_id=message.chat.id,
                user_id=0,
                username="Бот",
                message_text=ai_response,
                is_bot_message=True
            )
            
            await send_voice_message(message, ai_response)
            
            await db.clear_old_chat_history(message.chat.id, keep_last=100)
        else:
            error_response = "Братуха нахуй, сука блять, не могу разобрать что ты там говоришь! Шершавый прутик не слышит, стальной шершень глохнет! Морская резьба крутится, но колесо крылатого шершня не понимает! Дьявольский поршень требует четче говорить, не шкваркнись баяном!"
            await send_voice_message(message, error_response)
    
    except Exception as e:
        print(f"Ошибка обработки голосового сообщения: {e}")
        error_response = "Братуха нахуй, сука блять, шершавый прутик сломался! Ебать, стальной шершень не работает! Морская резьба заклинила, колесо крылатого шершня встало! Дьявольский поршень шкваркнулся баяном!"
        await send_voice_message(message, error_response)

@router.message()
async def chat_message_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if message.chat.type in ['group', 'supergroup']:
        await db.add_or_update_group_chat(message.chat.id, message.chat.title)
        await db.update_last_message_time(message.chat.id)
        
        if not should_respond_in_group(message, BOT_USERNAME):
            return
    
    if current_state:
        return
    
    if message.text:
        clean_text = message.text.replace(f"@{BOT_USERNAME}", "").strip().lower()
        
        music_keywords = ["музык", "песн", "трек", "music", "song", "послушать", "включи", "поставь"]
        if any(keyword in clean_text for keyword in music_keywords):
            song_data = get_nirvana_link_with_comment()
            music_response = f"{song_data['comment']}\n\n{song_data['title']}:\n{song_data['url']}"
            await send_voice_message(message, song_data['comment'])
            await message.answer(f"{song_data['title']}:\n{song_data['url']}")
            return
        
        if "напомни" in clean_text and current_state != ReminderStates.waiting_activity:
            response = """Эй йоу чувак, хочешь чтобы я тебе что-то напомнил?

Братан, это просто крутяк! Скажи мне что именно тебе напомнить, и я настрою свой сваговый будильник. Я никогда не подвожу своих друзей!

Жду от тебя детали, чел!"""
            
            await send_voice_message(message, response)
            await state.set_state(ReminderStates.waiting_activity)
            return
        
        await db.add_chat_message(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            username=message.from_user.first_name or message.from_user.username or "Пользователь",
            message_text=message.text,
            is_bot_message=False
        )
        
        chat_history = await db.get_chat_history(message.chat.id)
        
        ai_response = await ai_service.chat_response(
            user_message=message.text,
            chat_history=chat_history,
            username=message.from_user.first_name or message.from_user.username or "Пользователь"
        )
        
        await db.add_chat_message(
            chat_id=message.chat.id,
            user_id=0,
            username="Бот",
            message_text=ai_response,
            is_bot_message=True
        )
        
        await send_voice_message(message, ai_response)
        
        await db.clear_old_chat_history(message.chat.id, keep_last=100) 