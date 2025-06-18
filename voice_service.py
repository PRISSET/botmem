import os
import tempfile
import edge_tts
from pydub import AudioSegment
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re
import openai
from config import OPENAI_API_KEY
import speech_recognition as sr

class VoiceService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.male_voices = [
            "ru-RU-DmitryNeural",
            "ru-RU-SvetlanaNeural", 
        ]
        self.current_voice = "ru-RU-DmitryNeural"
        self.openai_client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        self.recognizer = sr.Recognizer()
    
    def clean_text_for_speech(self, text):
        text = re.sub(r'https?://[^\s]+', 'ссылка', text)
        text = re.sub(r'@\w+', 'пользователь', text)
        text = re.sub(r'#\w+', 'хештег', text)
        text = text.replace('*', '')
        text = text.replace('_', '')
        text = text.replace('`', '')
        text = text.replace('```', '')
        text = re.sub(r'\n+', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    async def create_voice_message_async(self, text, voice=None):
        try:
            clean_text = self.clean_text_for_speech(text)
            
            if len(clean_text) > 1000:
                clean_text = clean_text[:1000] + "..."
            
            voice_to_use = voice or self.current_voice
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            communicate = edge_tts.Communicate(clean_text, voice_to_use, rate='+50%', pitch='-10Hz')
            await communicate.save(temp_path)
            
            audio = AudioSegment.from_mp3(temp_path)
            
            audio = audio + 2
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as ogg_file:
                ogg_path = ogg_file.name
            
            audio.export(ogg_path, format="ogg", codec="libopus", bitrate="96k")
            
            os.unlink(temp_path)
            
            return ogg_path
            
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e
    
    def set_voice(self, voice_name):
        if voice_name in self.male_voices:
            self.current_voice = voice_name
    
    def get_available_voices(self):
        return self.male_voices
    
    async def transcribe_voice_message(self, voice_file_path):
        try:
            audio = AudioSegment.from_file(voice_file_path)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as wav_file:
                wav_path = wav_file.name
            
            audio.export(wav_path, format="wav")
            
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
            
            try:
                text = self.recognizer.recognize_google(audio_data, language='ru-RU')
                os.unlink(wav_path)
                return text
            except sr.UnknownValueError:
                os.unlink(wav_path)
                return None
            except sr.RequestError as e:
                print(f"Ошибка Google Speech Recognition: {e}")
                os.unlink(wav_path)
                return None
                
        except Exception as e:
            print(f"Ошибка транскрибации: {e}")
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.unlink(wav_path)
            return None

voice_service = VoiceService() 