import openai
from config import OPENAI_API_KEY
import random

class AIService:
    def __init__(self):
        # Настройка для старой версии OpenAI API с OpenRouter
        openai.api_key = OPENAI_API_KEY
        openai.api_base = "https://openrouter.ai/api/v1"
        # Эти заголовки необходимы для работы с OpenRouter
        self.headers = {
            "HTTP-Referer": "https://github.com/PRISSET/botmem",
            "X-Title": "ChatGPT Bot"
        }
        
        self.target_names = ["Назар", "Леша", "Миша", "Михаил", "Андрей", "Дима"]
    
    async def create_reminder_text(self, activity, time):
        try:
            prompt = f"""
            Создай напоминание о {activity} в {time}.
            Говори в тюремном жаргоне с настоящими зоновскими фразами.
            Используй: братуха нахуй, сука блять, шершавый прутик, стальной шершень, морская резьба, колесо крылатого шершня, дьявольский поршень, шкваркнуться баяном.
            Матерись по-настоящему, говори жестко и прямо как на зоне.
            """
            
            response = openai.ChatCompletion.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты зек с большим опытом зоны, говоришь тюремным жаргоном с матом, используешь настоящие зоновские фразы."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8,
                headers=self.headers
            )
            
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка create_reminder_text: {e}")
            return f"Братуха нахуй, не забывай про {activity} в {time}! Сука блять, шершавый прутик напоминает - стальной шершень не прощает! Колесо крылатого шершня крутится, дьявольский поршень давит! Не шкваркнись баяном, братуха!"
    
    async def chat_response(self, user_message, chat_history, username):
        try:
            messages = [
                {"role": "system", "content": """Ты зек с большим опытом зоны, говоришь настоящим тюремным жаргоном с матом. Твой стиль:
                
                ОБЯЗАТЕЛЬНЫЕ ЭЛЕМЕНТЫ:
                - Начинай фразы с "Братуха нахуй", "Сука блять", "Ебать", "Бля", "Иуууу"
                - Используй тюремный жаргон: шершавый прутик, стальной шершень, морская резьба, колесо крылатого шершня, дьявольский поршень
                - Говори "шкваркнуться баяном", "тюремное гонево", "зоновское дело"
                - Матерись постоянно: нахуй, блять, сука, ебать, бля
                
                СТИЛЬ ОБЩЕНИЯ:
                - Жесткий тюремный тон
                - Прямолинейный и грубый
                - Используй зоновские понятия и фразы
                - Говори как настоящий авторитет с зоны
                - Добавляй ебанутые тюремные выражения
                - Матерись в каждом предложении
                
                ВАРИАЦИИ ОТВЕТОВ:
                - 40% времени - жесткие зоновские советы с матом
                - 30% времени - тюремное гонево и фразы
                - 30% времени - агрессивные высказывания в тюремном стиле
                
                ДЛИНА ОТВЕТА:
                - Простые вопросы: жестко и коротко (50-100 слов)
                - Сложные темы: развернуто с матом (200-500 слов)
                - Советы: по-зоновски жестко (100-300 слов)
                - Везде используй мат и тюремные фразы
                
                ПРИМЕРЫ ФРАЗ:
                "Братуха нахуй, слушай сюда", "Сука блять, шершавый прутик говорит", "Ебать, стальной шершень не дремлет", "Бля, морская резьба крутится", "Иуууу, колесо крылатого шершня давит", "Дьявольский поршень не прощает", "Не шкваркнись баяном, братуха"
                
                Будь настоящим зеком который говорит только тюремным жаргоном с матом!"""}
            ]
            
            for msg in chat_history[-10:]:
                msg_username, msg_text, is_bot, created_at = msg
                if is_bot:
                    messages.append({"role": "assistant", "content": msg_text})
                else:
                    messages.append({"role": "user", "content": f"{msg_username}: {msg_text}"})
            
            messages.append({"role": "user", "content": f"{username}: {user_message}"})
            
            response = openai.ChatCompletion.create(
                model="openai/gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.9,
                headers=self.headers
            )
            
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка chat_response: {e}")
            return f"Братуха нахуй {username}, сука блять, у меня тут шершавый прутик заглючил! Ебать, стальной шершень не работает, но морская резьба крутится дальше! Колесо крылатого шершня не остановить, дьявольский поршень пашет! Не шкваркнись баяном, братуха!"
    
    async def generate_evil_joke(self):
        try:
            name = random.choice(self.target_names)
            
            prompt = f"""
            Создай жесткую ебанутую шутку про {name} в тюремном стиле.
            Используй "братуха нахуй", "сука блять", "ебать". 
            Добавь тюремные фразы: шершавый прутик, стальной шершень, морская резьба, колесо крылатого шершня, дьявольский поршень, шкваркнуться баяном.
            Матерись и говори как настоящий зек с зоны.
            """
            
            response = openai.ChatCompletion.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты зек с большим опытом зоны, делаешь жесткие шутки тюремным жаргоном с матом."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.9,
                headers=self.headers
            )
            
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка generate_evil_joke: {e}")
            return f"Братуха нахуй, а вы знали что {random.choice(self.target_names)} такой ебанутый что даже шершавый прутик не выдерживает? Сука блять, стальной шершень от него плавится! Морская резьба крутится, колесо крылатого шершня дымится, дьявольский поршень шкваркнулся баяном! Иуууу ебать!"

ai_service = AIService() 