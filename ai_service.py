import openai
from config import OPENAI_API_KEY
import random
import importlib
import sys
import os
import requests
import json
import aiohttp

class AIService:
    def __init__(self):
        # API ключ OpenRouter
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Заголовки для запросов к API - разные варианты авторизации
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/PRISSET/botmem",
            "X-Title": "ChatGPT Bot",
            "OpenAI-Organization": "openrouter"
        }
        
        self.target_names = ["Назар", "Леша", "Миша", "Михаил", "Андрей", "Дима"]
    
    async def _send_request(self, messages, max_tokens=1000, temperature=0.8):
        """Отправляет запрос к API OpenRouter напрямую через aiohttp"""
        try:
            data = {
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "route": "fallback"
            }
            
            print(f"Отправка запроса к OpenRouter API: {self.api_url}")
            print(f"Заголовки: {self.headers}")
            
            # Используем aiohttp вместо requests
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self.api_url,
                    headers=self.headers,
                    json=data
                ) as response:
                    print(f"Статус ответа: {response.status}")
                    
                    if response.status != 200:
                        response_text = await response.text()
                        print(f"Ошибка API: {response_text}")
                        
                        # Попробуем альтернативный способ, отправляя ключ API в параметре
                        print("Пробуем альтернативный способ...")
                        
                        # Добавляем api_key непосредственно в данные запроса
                        data["api_key"] = self.api_key
                        
                        # Попытка 2: с ключом в данных
                        async with session.post(
                            url=self.api_url,
                            headers={
                                "Content-Type": "application/json",
                                "HTTP-Referer": "https://github.com/PRISSET/botmem",
                                "X-Title": "ChatGPT Bot"
                            },
                            json=data
                        ) as response2:
                            print(f"Статус ответа (способ 2): {response2.status}")
                            
                            if response2.status != 200:
                                response_text2 = await response2.text()
                                print(f"Ошибка API (способ 2): {response_text2}")
                                
                                # Попытка 3: с другим URL
                                alt_url = "https://api.openrouter.ai/api/v1/chat/completions"
                                print(f"Пробуем URL: {alt_url}")
                                
                                # Пробуем другой URL API с исходными заголовками
                                async with session.post(
                                    url=alt_url,
                                    headers=self.headers,
                                    json={
                                        "model": "openai/gpt-4o-mini",
                                        "messages": messages,
                                        "max_tokens": max_tokens,
                                        "temperature": temperature
                                    }
                                ) as response3:
                                    print(f"Статус ответа (способ 3): {response3.status}")
                                    
                                    if response3.status != 200:
                                        response_text3 = await response3.text()
                                        print(f"Ошибка API (способ 3): {response_text3}")
                                        return None
                                    else:
                                        result3 = await response3.json()
                                        print("Успех со способом 3!")
                                        return result3["choices"][0]["message"]["content"]
                            else:
                                result2 = await response2.json()
                                print("Успех со способом 2!")
                                return result2["choices"][0]["message"]["content"]
                    else:
                        result = await response.json()
                        print("Успех с первым способом!")
                        return result["choices"][0]["message"]["content"]
                        
        except Exception as e:
            print(f"Ошибка _send_request: {e}")
            print(f"Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    async def create_reminder_text(self, activity, time):
        prompt = f"""
        Создай напоминание о {activity} в {time}.
        Говори в тюремном жаргоне с настоящими зоновскими фразами.
        Используй: братуха нахуй, сука блять, шершавый прутик, стальной шершень, морская резьба, колесо крылатого шершня, дьявольский поршень, шкваркнуться баяном.
        Матерись по-настоящему, говори жестко и прямо как на зоне.
        """
        
        system_message = "Ты зек с большим опытом зоны, говоришь тюремным жаргоном с матом, используешь настоящие зоновские фразы."
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        response = await self._send_request(messages, max_tokens=300, temperature=0.8)
        if response:
            return response
        else:
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
            
            response = await self._send_request(messages, max_tokens=1000, temperature=0.9)
            if response:
                return response
            else:
                return f"Братуха нахуй {username}, сука блять, у меня тут шершавый прутик заглючил! Ебать, стальной шершень не работает, но морская резьба крутится дальше! Колесо крылатого шершня не остановить, дьявольский поршень пашет! Не шкваркнись баяном, братуха!"
                
        except Exception as e:
            print(f"Ошибка chat_response: {e}")
            print(f"Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
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
            
            system_message = "Ты зек с большим опытом зоны, делаешь жесткие шутки тюремным жаргоном с матом."
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._send_request(messages, max_tokens=400, temperature=0.9)
            if response:
                return response
            else:
                return f"Братуха нахуй, а вы знали что {random.choice(self.target_names)} такой ебанутый что даже шершавый прутик не выдерживает? Сука блять, стальной шершень от него плавится! Морская резьба крутится, колесо крылатого шершня дымится, дьявольский поршень шкваркнулся баяном! Иуууу ебать!"
                
        except Exception as e:
            print(f"Ошибка generate_evil_joke: {e}")
            print(f"Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
            return f"Братуха нахуй, а вы знали что {random.choice(self.target_names)} такой ебанутый что даже шершавый прутик не выдерживает? Сука блять, стальной шершень от него плавится! Морская резьба крутится, колесо крылатого шершня дымится, дьявольский поршень шкваркнулся баяном! Иуууу ебать!"

ai_service = AIService() 