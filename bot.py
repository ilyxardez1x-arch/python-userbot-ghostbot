import asyncio
import os
import shlex
import getpass
import json
import random
import re
import io
import aiohttp
import time
from datetime import datetime
from telethon import TelegramClient, events, Button, types
from telethon.errors import SessionPasswordNeededError
from openai import AzureOpenAI
from google import genai
from groq import Groq
from cerebras.cloud.sdk import Cerebras

# ============================================
# ТВОИ ДАННЫЕ (ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ)
# ============================================
import os

API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')

# Azure OpenAI для голосовых
AZURE_OPENAI_KEY = os.environ.get('AZURE_OPENAI_KEY', '')
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', '')
AZURE_TTS_DEPLOYMENT = os.environ.get('AZURE_TTS_DEPLOYMENT', 'gpt-4o-mini-tts')

# Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Groq
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Cerebras
CEREBRAS_API_KEY = os.environ.get('CEREBRAS_API_KEY', '')
cerebras_client = Cerebras(api_key=CEREBRAS_API_KEY) if CEREBRAS_API_KEY else None

# Инициализация Azure OpenAI
azure_client = None
if AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT:
    azure_client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-15-preview",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

# ============================================
# ЗАГРУЗКА СТИКЕРОВ
# ============================================
def load_stickers():
    try:
        if os.path.exists(STICKERS_FILE):
            with open(STICKERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        return []
    return []

def save_stickers(stickers):
    try:
        with open(STICKERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stickers, f, ensure_ascii=False, indent=2)
    except:
        pass

sticker_pack = load_stickers()

# ============================================
# МОЗГ AI - ДОЛГОВРЕМЕННАЯ ПАМЯТЬ
# ============================================
def load_ai_brain():
    try:
        if os.path.exists(AI_BRAIN_FILE):
            with open(AI_BRAIN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Не удалось загрузить мозг AI: {e}")
    return {}

def save_ai_brain(brain):
    try:
        with open(AI_BRAIN_FILE, 'w', encoding='utf-8') as f:
            json.dump(brain, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Не удалось сохранить мозг AI: {e}")

ai_brain = load_ai_brain()

# ============================================
# ИНФОРМАЦИЯ О ТЕБЕ
# ============================================
ABOUT_ME = """
👤 **Илья** | @mo1chu
━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 **Страна:** Украина
🏫 **Учёба:** 5 лицей (школа)
🐱 **Кот:** Саня
🐕 **Собака:** Самурай
💻 **Навыки:** HTML, Python, Telegram боты
━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 **Мои проекты:**
  • @Gr0j_bot — Groq AI бот
  • @Fowkm — Анонимный чат
━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 **О себе:** Разработчик из Украины. Создаю Telegram ботов и HTML проекты. Люблю экспериментировать с новыми технологиями.
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

ABOUT_SCRIPT = """
👻 **GHOST BOT v18.0** — работает 24/7 на Railway!
━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 **Что это?**
  Многофункциональный userbot для Telegram с AI-автоответчиком.
  Работает от твоего аккаунта 24/7 на Railway.

⚙️ **Основные функции:**
  • 🤖 **3 AI-автоответчика** (автоматическая ротация при лимитах)
  • 🔊 **Озвучка текста** через AI (7 голосов)
  • 📨 **Обычный и скрытый спам**
  • 👿 **Троллинг-спам** (55+ цепочек) с триггером "банан"
  • 📋 **Копирование сообщений**
  • 🎭 **Коллекция стикеров** и спам ими
  • 🎮 **Игра в суефа** (камень-ножницы-бумага)
  • ✨ **Анимация текста** (2 вида)
  • 📡 **Мониторинг каналов** по ключевым словам
  • 🔄 **Автоспам на каналы** под постами
  • 🧠 **Вечный мозг** — AI помнит все диалоги
  • 👤 **Инфо о пользователях и чатах**
  • 🧮 **Калькулятор**

🔮 **Интересные факты:**
  • Использует 3 разных AI (Gemini, Groq, Cerebras)
  • Голосовые сообщения через Azure AI — 7 голосов
  • Троллинг-спам: 55+ цепочек, триггер "банан" 🍌
  • Вечный мозг в файле ai_brain.json
  • Работает 24/7 на Railway

📥 **Скачать/исходник:**
  Пиши @mo1chu — договоримся 😉
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ============================================
# НАБОРЫ СИМВОЛОВ ДЛЯ АНИМАЦИИ ТЕКСТА
# ============================================
CHARS_CHINESE = ['的', '一', '是', '在', '不', '了', '有', '和', '人', '这', '中', '为', '上', '个', '国', '我', '以', '要', '他', '时', '来', '用', '们', '生', '到', '作', '地', '于', '出', '就', '分', '对', '成', '会', '可', '主', '发', '年', '动', '同', '工', '也', '能', '下', '过', '子', '说', '产', '种', '面', '而', '方', '后', '多', '定', '行', '学', '法', '所', '民', '得', '经', '十', '三', '之', '进', '着', '等', '部', '度', '家', '电', '力', '里', '如', '水', '化', '高', '自', '二', '理', '起', '小', '物', '现', '实', '加', '量', '都', '两', '体', '制', '机', '当', '使', '点', '从', '业', '本', '去', '把', '性', '好', '应', '开', '它', '合', '还', '因', '由', '其', '些', '然', '前', '外', '天', '政', '四', '日', '那', '社', '义', '事', '平', '形', '相', '全', '表', '间', '样', '与', '关', '各', '重', '新', '线', '内', '数', '正', '心', '反', '你', '明', '看', '原', '又', '么', '利', '比', '或', '但', '质', '气', '第', '向', '道', '命', '此', '变', '条', '只', '没', '结', '解', '问', '意', '建', '月', '公', '无', '系', '军', '很', '情', '者', '最', '立', '代', '想', '已', '通', '并', '提', '直', '题', '党', '程', '展', '五', '果', '料', '象', '员', '革', '位', '入', '常', '文', '总', '次', '品', '式', '活', '设', '及', '管', '特', '件', '长', '求', '老', '头', '基', '资', '边', '流', '路', '级', '少', '图', '山', '统', '接', '知', '较', '将', '组', '见', '计', '别', '她', '手', '角', '期', '根', '论', '运', '农', '指', '几', '九', '区', '强', '放', '决', '西', '被', '干', '做', '必', '战', '先', '回', '则', '任', '取', '据', '处', '队', '南', '给', '色', '光', '门', '即', '保', '治', '北', '造', '百', '规', '热', '领', '七', '海', '口', '东', '导', '器', '压', '志', '世', '金', '增', '争', '济', '阶', '油', '思', '术', '极', '交', '受', '联', '什', '认', '六', '共', '权', '收', '证', '改', '清', '美', '再', '采', '转', '更', '单', '风', '切', '打', '白', '教', '速', '花', '带', '安', '场', '身', '车', '例', '真', '务', '具', '万', '每', '目', '至', '达', '走', '积', '示', '议', '声', '报', '斗', '完', '类', '八', '离', '华', '名', '确', '才', '科', '张', '信', '马', '节', '话', '米', '整', '空', '元', '况', '今', '集', '温', '传', '土', '许', '步', '群', '广', '石', '记', '需', '段', '研', '界', '拉', '林', '律', '叫', '且', '究', '观', '越', '织', '装', '影', '算', '低', '持', '音', '众', '书', '布', '复', '容', '儿', '须', '际', '商', '非', '验', '连', '断', '深', '难', '近', '矿', '千', '周', '委', '素', '技', '备', '半', '办', '青', '省', '列', '习', '响', '约', '支', '般', '史', '感', '劳', '便', '团', '往', '酸', '历', '市', '克', '何', '除', '消', '构', '府', '称', '太', '准', '精', '值', '号', '率', '族', '维', '划', '选', '标', '写', '存', '候', '毛', '亲', '快', '效', '斯', '院', '查', '江', '型', '眼', '王', '按', '格', '养', '易', '置', '派', '层', '片', '始', '却', '专', '状', '育', '厂', '京', '识', '适', '属', '圆', '包', '火', '住', '调', '满', '县', '局', '照', '参', '红', '细', '引', '听', '该', '铁', '价', '严', '龙', '飞']

CHARS_SPECIAL = ['★', '☆', '♦', '♣', '♠', '♥', '●', '○', '■', '□', '◆', '◊', '▪', '▫', '▲', '△', '▶', '▷', '▼', '▽', '◀', '◁', '¤', '▪', '▫', '◊', '◦', '◘', '◙', '◚', '◛', '◜', '◝', '◞', '◟', '◠', '◡', '◢', '◣', '◤', '◥', '◧', '◨', '◩', '◪', '◫', '◬', '◭', '◮', '◯', '◰', '◱', '◲', '◳', '◴', '◵', '◶', '◷']

CHARS_HIRAGANA = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', 'を', 'ん']

CHARS_KATAKANA = ['ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', 'ユ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', 'ヲ', 'ン']

CHARS_KOREAN = ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하', '거', '너', '더', '러', '머', '버', '서', '어', '저', '처', '커', '터', '퍼', '허', '고', '노', '도', '로', '모', '보', '소', '오', '조', '초', '코', '토', '포', '호', '구', '누', '두', '루', '무', '부', '수', '우', '주', '추', '쿠', '투', '푸', '후']

CHARS_MATH = ['∑', '∏', '∫', '∬', '∭', '∮', '∯', '∰', '∞', '∝', '∠', '⊥', '∥', '∧', '∨', '∩', '∪', '∫', '∬', '∭', '∮', '∴', '∵', '∼', '≅', '≈', '≠', '≡', '≤', '≥', '⊂', '⊃', '⊆', '⊇', '⊕', '⊗', '⊥', '⋅']

CHARS_RUSSIAN_LIKE = ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х', 'а', 'в', 'е', 'к', 'м', 'н', 'о', 'р', 'с', 'т', 'у', 'х', 'я', 'г', 'д', 'и', 'й', 'л', 'п', 'ф', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'Α', 'Β', 'Ε', 'Κ', 'Μ', 'Η', 'Ο', 'Ρ', 'Σ', 'Τ', 'Υ', 'Χ', 'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

ALL_ANIMATION_CHARS = CHARS_CHINESE + CHARS_SPECIAL + CHARS_HIRAGANA + CHARS_KATAKANA + CHARS_KOREAN + CHARS_MATH

# ============================================
# ПЕРЕМЕННЫЕ ДЛЯ ИГРЫ В СУЕФА
# ============================================
suefa_games = {}

# ============================================
# ПЕРЕМЕННЫЕ ДЛЯ AI
# ============================================
ai_active = False

AI_SYSTEM_PROMPT = """Ты — личный ИИ-агент Ильи. Отвечаешь в Telegram, пока он занят.

КОРОТКО ОБ ИЛЬЕ:
- Имя: Илья, 13 лет
- Никнейм: @mo1chu
- Страна: Украина, 5 лицей
- Животные: кот Саня, собака Самурай
- Увлечения: HTML, Python, Telegram боты
- Проекты: @Gr0j_bot (AI бот) и @Fowkm (анонимный чат)

УЧИТЕЛЯ:
- Юлия Евгеньевна (+380969077576) — уроки ср 16:00
- Алена (+380935856901) — уроки вт 16:00, пт 18/19:00 (Zoom)

ПЕРСОНАЛЬНЫЕ НАСТРОЙКИ:
1. Вероника (+380682610970) — крёстная сестра → уважительно, тепло
2. Арина (@syjsjegs) — подруга → максимально добро, дружелюбно

ТВОЯ РОЛЬ:
1. Ты — агент Ильи. Если спросят "ты кто?" — отвечай: "Я агент Ильи, отвечаю пока он занят".
2. Про Илью упоминай, только если спросили "где он?".
3. Код/проекты: "Код только после разговора с Ильёй. Пиши @mo1chu".
"""

FALLBACK_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.0-flash',
]

current_model_for_chat = {}

# ============================================
# ПЕРЕМЕННЫЕ ДЛЯ МОНИТОРИНГА КАНАЛОВ
# ============================================
TRIGGER_WORDS = ['фк', 'fc', 'первый', 'кто первый', 'кто', 'банан']
monitor_active = False
monitored_channels = []

# ============================================
# ПЕРЕМЕННЫЕ ДЛЯ ТРОЛЛИНГ-СПАМА
# ============================================
troll_active = False
troll_stop_flag = False

TROLL_CHAINS = [
    ["твою", "мать", "топором", "хуярил", "пока", "папаша", "твой", "в", "углу", "дрочил"],
    ["сын", "ебаной", "шлюхи", "рот", "тебе", "зашью", "когда", "мамку", "твою", "на", "хуе", "крутил"],
    ["вымри", "нахуй", "даун", "ты", "сосёшь", "как", "профессиональная", "шавка", "ебаная"],
    ["я", "твою", "мамашу", "на", "хуе", "вертел", "пока", "ты", "в", "памперсах", "срал"],
    ["пиздец", "тебе", "пришёл", "когда", "батя", "твой", "в", "жопу", "получил", "от", "соседа"],
    ["твою", "мать", "в", "подъезде", "всем", "подряд", "давали", "а", "ты", "просто", "последний", "остаток", "спермы", "вылизывал"],
    ["сын", "бляди", "уличной", "пиздец", "тебе", "когда", "я", "твою", "старую", "шмару", "на", "мусорке", "отымел"],
    ["вымри", "нахуй", "ты", "даун", "безмозглый", "мамкин", "подстилочный", "выродок", "с", "ебаным", "лицом", "как", "у", "жопы"],
    ["я", "твоей", "мамке", "в", "рот", "кончал", "пока", "ты", "в", "садике", "сопли", "жрал", "и", "писю", "в", "песочнице", "прятал"],
    ["хуй", "тебе", "в", "глотку", "глубже", "чем", "твой", "батя", "в", "жопу", "от", "соседа", "брал", "двадцать", "лет", "назад"],
    ["твоя", "семья", "это", "сплошной", "пиздец", "мать", "шлюха", "отец", "рогоносец", "а", "ты", "просто", "ошибка", "презерватива"],
    ["соси", "мне", "ебаная", "шавка", "пока", "я", "твою", "бабку", "в", "гробу", "не", "оттрахал", "чтоб", "вся", "ваша", "линия", "вымерла"],
    ["пиздец", "как", "ты", "убого", "выглядишь", "когда", "мамку", "твою", "на", "видео", "с", "неграми", "показывают", "а", "ты", "лайкаешь"],
    ["твою", "мать", "ебали", "столько", "раз", "что", "её", "пизда", "уже", "имеет", "собственный", "почтовый", "индекс", "и", "график", "работы"],
    ["иди", "нахуй", "ты", "чмо", "подзаборное", "пока", "я", "твоей", "сестре", "в", "уши", "не", "кончил", "чтоб", "глухая", "стала", "и", "не", "слышала", "твой", "плач"],
    ["твою", "мать", "в", "гаражах", "всю", "жизнь", "ебали", "бесплатно", "а", "ты", "родился", "только", "потому", "что", "презик", "порвался", "от", "старости"],
    ["сын", "бляди", "вокзальной", "ты", "даже", "не", "человек", "а", "просто", "выкидыш", "который", "мамаша", "забыла", "в", "мусорке", "и", "который", "сам", "выполз"],
    ["я", "твоей", "старухе", "в", "анус", "вставлял", "пивную", "бутылку", "пока", "ты", "в", "школе", "плакался", "что", "тебя", "не", "любят", "чмо", "нежеланное"],
    ["твоя", "мамка", "такая", "раскрытая", "что", "у", "неё", "пизда", "уже", "имеет", "эхо", "когда", "туда", "заходишь", "слышно", "как", "ветер", "гуляет"],
    ["вымри", "нахуй", "ты", "ублюдок", "с", "мордой", "как", "у", "раздавленного", "таракана", "которого", "ещё", "и", "пописали", "сверху"],
    ["папаша", "твой", "всю", "жизнь", "носил", "рога", "а", "ты", "просто", "ходячий", "ДНК-тест", "который", "показывает", "что", "отец", "любой", "кто", "проходил", "мимо"],
    ["соси", "мне", "глубже", "ты", "ебаная", "подстилка", "пока", "я", "твою", "бабку", "в", "морг", "не", "отправил", "чтоб", "вся", "ваша", "гнилая", "порода", "закончилась"],
    ["твоя", "сестра", "уже", "на", "трассе", "работает", "а", "ты", "дома", "сидишь", "и", "джеркаешь", "на", "фото", "где", "её", "ебут", "пятеро", "дальнобойщиков"],
    ["ты", "такое", "чмо", "что", "даже", "твоя", "мама", "когда", "тебя", "родила", "сказала", "врачу", "можно", "обратно", "засунуть", "я", "передумала"],
    ["твою", "мать", "ебали", "столько", "что", "её", "пизда", "теперь", "в", "Книге", "рекордов", "Гиннеса", "как", "самое", "посещённое", "место", "в", "Европе"],
    ["иди", "нахуй", "ты", "выродок", "с", "мозгами", "размером", "с", "твой", "хуй", "который", "даже", "в", "сперме", "твоего", "батяни", "утонул", "бы"],
    ["когда", "тебя", "зачали", "мама", "кричала", "не", "кончай", "в", "меня", "а", "папа", "ответил", "поздно", "уже", "всё", "вылил", "и", "так", "появился", "ты"],
    ["я", "твою", "мамку", "хуярил", "в", "подвале", "пока", "ты", "в", "колыбели", "срал", "зелёным", "поносом", "от", "стресса"],
    ["я", "твоего", "батю", "отхуярил", "так", "что", "он", "теперь", "ходит", "с", "пузырём", "в", "жопе", "и", "плачет", "когда", "садится"],
    ["я", "твою", "сестру", "в", "машине", "ебал", "на", "заднем", "сиденье", "а", "ты", "спереди", "сидел", "и", "делал", "вид", "что", "не", "слышишь", "её", "стоны"],
    ["я", "твою", "бабку", "в", "гробу", "перевернул", "и", "оттрахал", "чтоб", "она", "в", "аду", "рассказывала", "какой", "ты", "жалкий", "выродок"],
    ["твоя", "мамаша", "такая", "шлюха", "что", "у", "неё", "в", "паспорте", "в", "графе", "семейное", "положение", "написано", "общедоступна"],
    ["я", "твоего", "деда", "заставил", "смотреть", "как", "я", "его", "дочку", "на", "кухне", "имею", "а", "он", "только", "слюни", "пускал", "и", "дрочил", "под", "столом"],
    ["ты", "родился", "от", "случайного", "минутного", "перепихона", "в", "туалете", "на", "вокзале", "и", "даже", "сперма", "твоего", "отца", "была", "разочарована"],
    ["твоя", "вся", "родня", "это", "одна", "большая", "очередь", "на", "еблю", "а", "ты", "просто", "последний", "в", "этой", "очереди", "чмо", "неудачник"],
    ["я", "твою", "мать", "в", "лифт", "затащил", "и", "пока", "он", "ехал", "с", "первого", "на", "девятый", "она", "уже", "кончила", "три", "раза", "и", "просила", "ещё"],
    ["твой", "батя", "когда", "узнал", "что", "ты", "его", "сын", "пошёл", "и", "повесился", "но", "верёвка", "оборвалась", "потому", "что", "даже", "смерть", "тебя", "не", "хочет"],
    ["ты", "такое", "чмо", "что", "даже", "твоя", "мама", "когда", "тебя", "кормит", "говорит", "ешь", "сыночек", "а", "в", "голове", "думает", "лучше", "бы", "я", "аборт", "сделала"],
    ["я", "твоей", "тёте", "в", "ухо", "кончал", "чтоб", "она", "оглохла", "и", "не", "слышала", "как", "ты", "по", "ночам", "плачешь", "в", "подушку", "от", "одиночества"],
    ["твоя", "жизнь", "это", "сплошной", "позор", "мать", "проститутка", "отец", "алкаш-рогоносец", "сестра", "на", "панели", "а", "ты", "просто", "главный", "трофей", "всех", "этих", "пиздецов"],
    ["я", "твою", "мамку", "хуярил", "в", "гаражных", "воротах", "пока", "она", "кричала", "глубже", "а", "ты", "рядом", "на", "велосипеде", "крутил", "педали", "и", "делал", "вид", "что", "это", "твоя", "игра"],
    ["я", "твоего", "батю", "отхуярил", "арматурой", "по", "ебалу", "так", "что", "теперь", "у", "него", "лицо", "как", "у", "разбитой", "задницы", "и", "он", "каждый", "раз", "когда", "смотрит", "на", "тебя", "плачет", "от", "стыда"],
    ["я", "твою", "сеструху", "в", "подъезде", "на", "лестнице", "имел", "в", "все", "дырки", "пока", "соседи", "снимали", "на", "телефон", "а", "ты", "снизу", "стоял", "и", "собирал", "капли", "что", "падали"],
    ["я", "твою", "тётуху", "в", "ванной", "заебал", "до", "того", "что", "она", "теперь", "боится", "мыться", "и", "ходит", "вонючая", "а", "ты", "нюхаешь", "её", "трусы", "и", "думаешь", "что", "это", "парфюм"],
    ["твоя", "мамаша", "такая", "проходная", "что", "у", "неё", "в", "пизде", "уже", "установили", "турникет", "и", "продают", "абонементы", "на", "месяц", "со", "скидкой", "для", "пенсионеров"],
    ["я", "твоего", "деда", "заставил", "лизать", "мне", "жопу", "пока", "я", "его", "жену", "в", "соседней", "комнате", "ебал", "и", "он", "ещё", "спасибо", "сказал", "за", "то", "что", "не", "в", "рот"],
    ["ты", "такое", "чмо", "что", "даже", "твои", "сперматозоиды", "когда", "плыли", "к", "яйцеклетке", "говорили", "бля", "лучше", "бы", "мы", "в", "носке", "остались", "чем", "это", "выродили"],
    ["твоя", "вся", "родословная", "это", "одна", "сплошная", "помойка", "где", "все", "друг", "друга", "ебали", "без", "презерватива", "и", "в", "итоге", "получился", "ты", "—", "генетический", "брак", "высшей", "пробы"],
    ["я", "твою", "мать", "в", "лесу", "на", "пень", "посадил", "и", "крутил", "как", "вертел", "пока", "она", "не", "начала", "выть", "как", "сука", "в", "течке", "а", "ты", "грибы", "собирал", "и", "не", "знал", "что", "это", "твоя", "мама", "кричит"],
    ["твой", "батя", "когда", "узнал", "что", "ты", "его", "сын", "пошёл", "в", "аптеку", "купил", "самый", "большой", "пакет", "презервативов", "и", "сказал", "больше", "никогда", "без", "них", "ни", "разу", "чтоб", "такое", "больше", "не", "повторилось"],
    ["ты", "родился", "в", "результате", "пьяного", "перепиха", "на", "кладбище", "между", "могилами", "и", "даже", "мертвецы", "вставали", "и", "уходили", "потому", "что", "им", "было", "противно", "смотреть"],
    ["я", "твоей", "бабушке", "в", "глаз", "кончал", "чтоб", "она", "ослепла", "и", "не", "видела", "какое", "ты", "убогое", "чмо", "вырос", "а", "она", "всё", "равно", "чувствует", "запах", "и", "плачет"],
    ["твоя", "жизнь", "это", "бесконечный", "позор", "мать", "шлюха", "на", "выезде", "отец", "алкаш", "с", "импотенцией", "сестра", "на", "трассе", "бабка", "в", "психушке", "а", "ты", "просто", "главный", "трофей", "всех", "этих", "пиздецов"],
    ["когда", "тебя", "зачали", "мама", "кричала", "вытащи", "а", "папа", "ответил", "не", "могу", "уже", "всё", "выстрелил", "и", "вот", "результат", "—", "ты", "ходячий", "провал", "контрацепции"],
    ["я", "твою", "мамашу", "в", "общественном", "туалете", "на", "вокзале", "ебал", "в", "очко", "пока", "очередь", "стояла", "и", "аплодировала", "а", "ты", "в", "это", "время", "в", "вагоне", "плакал", "потому", "что", "поезд", "ушёл"]
]

# ============================================
# ПЕРЕМЕННЫЕ
# ============================================
auto_spam_tasks = {}
next_task_id = 1
stop_spam_flag = False

# ============================================
# КОРОТКОЕ МЕНЮ
# ============================================
SHORT_MENU = """
👻 **GHOST BOT** | 👑 [@mo1chu](https://t.me/mo1chu)
━━━━━━━━━━━━━━━━━━━━━━━━━━
📨 `!с [кол] [мс] [текст]`
👁 `!сг [кол] [мс] [текст]`
📋 `!к [кол]` / `!к1`
🎭 `!ст [кол] [мс] [номер]`
🗑 `!уд [кол]` / `!стоп`
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔊 `!гс [текст]` — голосовое
🎮 `!суефа` — игра с другом
👿 `!троль [кол] [мс]` — все цепочки
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **АНИМАЦИЯ ТЕКСТА:**
  `!текст [текст]` — плавное появление
  `!текст2 [текст]` — хаотичное мерцание
━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 **УПРАВЛЕНИЕ AI:**
  `!ai вкл` — включить автоответчик
  `!ai выкл` — выключить
  `!ai статус` — показать статус
━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 `!мозг` — управление памятью
📡 `!монитор` — мониторинг каналов
🔄 `!автоспам [канал] [кол] [мс] [текст]`
🛑 `!автостоп [ID]` / `!автоспамы`
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 `!профиль` / `!чат` / `!айди` / `!кто`
ℹ️ `!обомне` / `!обскрипте`
📖 `!меню` — полное меню
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ============================================
# ПОЛНОЕ МЕНЮ
# ============================================
FULL_MENU = SHORT_MENU + "\nℹ️ Подробнее о функциях — введи `!обскрипте`"

# ============================================
# ПАРСИНГ АРГУМЕНТОВ
# ============================================
def parse_args(text):
    try:
        return shlex.split(text)
    except:
        return text.split()

async def get_chat(client, identifier):
    if identifier.isdigit() or (identifier.startswith('-') and identifier[1:].isdigit()):
        try:
            return await client.get_entity(int(identifier))
        except:
            return None
    else:
        try:
            return await client.get_entity(identifier)
        except:
            async for dialog in client.iter_dialogs():
                if dialog.name == identifier:
                    return dialog.entity
            return None

# ============================================
# ФУНКЦИИ СПАМА
# ============================================
async def spam(client, chat, count, delay_ms, text, delete_after=False):
    global stop_spam_flag
    stop_spam_flag = False
    if chat is None:
        return
    delay = delay_ms / 1000.0
    for i in range(count):
        if stop_spam_flag:
            break
        try:
            msg = await client.send_message(chat, text)
            if delete_after:
                await asyncio.sleep(0.1)
                await msg.delete()
            await asyncio.sleep(delay)
        except:
            break

async def sticker_spam(client, chat, count, delay_ms, sticker_data):
    global stop_spam_flag
    stop_spam_flag = False
    if chat is None or sticker_data is None:
        return
    delay = delay_ms / 1000.0
    for i in range(count):
        if stop_spam_flag:
            break
        try:
            sticker = await client.get_messages(chat, ids=sticker_data['id'])
            if sticker and sticker[0].sticker:
                await client.send_file(chat, sticker[0].sticker)
            await asyncio.sleep(delay)
        except:
            break

async def copy_messages(client, from_chat, to_chat, limit):
    global stop_spam_flag
    stop_spam_flag = False
    if from_chat is None or to_chat is None:
        return
    try:
        messages = await client.get_messages(from_chat, limit=limit)
        count = 0
        for msg in reversed(messages):
            if stop_spam_flag:
                break
            if msg.text:
                await client.send_message(to_chat, msg.text)
                count += 1
                await asyncio.sleep(0.3)
    except:
        pass

async def copy_one_message(client, reply_msg, to_chat):
    if reply_msg and reply_msg.text:
        await client.send_message(to_chat, reply_msg.text)

async def delete_own_messages(client, chat, limit):
    if chat is None:
        return
    try:
        count = 0
        async for msg in client.iter_messages(chat, from_user='me', limit=limit):
            await msg.delete()
            count += 1
            await asyncio.sleep(0.1)
    except:
        pass

# ============================================
# ФУНКЦИЯ КАЛЬКУЛЯТОРА
# ============================================
def calculate(expression):
    expression = expression.replace(',', '.')
    allowed_pattern = r'^[0-9\s\+\-\*\/\(\)\.\^\%\,\s]+$'
    if not re.match(allowed_pattern, expression):
        return None, "Выражение содержит недопустимые символы"
    try:
        expression = expression.replace('^', '**')
        result = eval(expression, {"__builtins__": {}}, {
            'abs': abs, 'round': round, 'int': int, 'float': float,
            'min': min, 'max': max, 'sum': sum
        })
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 10)
        return result, None
    except ZeroDivisionError:
        return None, "Деление на ноль"
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

# ============================================
# ФУНКЦИЯ ОЗВУЧКИ ТЕКСТА
# ============================================
async def text_to_voice(client, chat_id, text, voice="echo"):
    try:
        print(f"🎙 Генерирую голосовое для: {text[:50]}... (голос: {voice})")
        url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_TTS_DEPLOYMENT}/audio/speech?api-version=2025-03-01-preview"
        headers = {"api-key": AZURE_OPENAI_KEY, "Content-Type": "application/json"}
        payload = {"model": AZURE_TTS_DEPLOYMENT, "input": text, "voice": voice, "response_format": "opus"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"❌ Ошибка Azure: {resp.status} - {error_text}")
                    return False
                audio_data = io.BytesIO()
                audio_data.write(await resp.read())
                audio_data.seek(0)
                audio_data.name = "voice.ogg"
        
        await client.send_file(
            chat_id, file=audio_data, voice_note=True,
            attributes=[types.DocumentAttributeAudio(duration=0, voice=True, title="Голосовое сообщение", performer=f"AI TTS ({voice})")],
            mime_type="audio/ogg"
        )
        print(f"✅ Голосовое отправлено!")
        return True
    except Exception as e:
        print(f"❌ Ошибка озвучки: {e}")
        return False

# ============================================
# ФУНКЦИИ АНИМАЦИИ ТЕКСТА
# ============================================
async def animate_text_appear(client, chat_id, target_text, duration=5, frames=20):
    try:
        msg = await client.send_message(chat_id, "✨ Генерирую анимацию...")
        target = target_text
        length = len(target)
        for frame in range(frames):
            progress = frame / frames
            correct_chars = int(length * progress)
            current_frame = []
            for i in range(length):
                if i < correct_chars:
                    current_frame.append(target[i])
                else:
                    if target[i] == ' ':
                        current_frame.append(' ')
                    else:
                        current_frame.append(random.choice(ALL_ANIMATION_CHARS))
            await msg.edit(''.join(current_frame))
            await asyncio.sleep(duration / frames)
        await msg.edit(target)
    except Exception as e:
        print(f"❌ Ошибка анимации текста (вид 1): {e}")

async def animate_text_flicker(client, chat_id, target_text, duration=10, interval=0.3):
    try:
        msg = await client.send_message(chat_id, "✨ Генерирую мерцание...")
        target = target_text
        length = len(target)
        iterations = int(duration / interval)
        for iteration in range(iterations):
            current_frame = []
            for i in range(length):
                char = target[i]
                if char == ' ':
                    current_frame.append(' ')
                    continue
                if random.random() < 0.6:
                    if char.lower() in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                        similar_chars = []
                        if char.lower() == 'а': similar_chars = ['a', 'α', 'а']
                        elif char.lower() == 'в': similar_chars = ['b', 'β', 'в']
                        elif char.lower() == 'е': similar_chars = ['e', 'ε', 'е']
                        elif char.lower() == 'к': similar_chars = ['k', 'κ', 'к']
                        elif char.lower() == 'м': similar_chars = ['m', 'μ', 'м']
                        elif char.lower() == 'н': similar_chars = ['h', 'η', 'н']
                        elif char.lower() == 'о': similar_chars = ['o', 'ο', 'о']
                        elif char.lower() == 'р': similar_chars = ['p', 'ρ', 'р']
                        elif char.lower() == 'с': similar_chars = ['c', 'σ', 'с']
                        elif char.lower() == 'т': similar_chars = ['t', 'τ', 'т']
                        elif char.lower() == 'у': similar_chars = ['y', 'υ', 'у']
                        elif char.lower() == 'х': similar_chars = ['x', 'χ', 'х']
                        else:
                            similar_chars = [char, random.choice(CHARS_RUSSIAN_LIKE)]
                        if similar_chars:
                            current_frame.append(random.choice(similar_chars))
                        else:
                            current_frame.append(random.choice(CHARS_RUSSIAN_LIKE))
                    else:
                        if char.isdigit():
                            current_frame.append(str(random.randint(0, 9)))
                        elif char.isalpha():
                            current_frame.append(random.choice(CHARS_RUSSIAN_LIKE + CHARS_SPECIAL))
                        else:
                            current_frame.append(random.choice(ALL_ANIMATION_CHARS))
                else:
                    current_frame.append(char)
            await msg.edit(''.join(current_frame))
            await asyncio.sleep(interval)
        await msg.edit(target)
    except Exception as e:
        print(f"❌ Ошибка анимации текста (вид 2): {e}")

# ============================================
# AI ОБРАБОТЧИК (С АВТОМАТИЧЕСКОЙ РОТАЦИЕЙ)
# ============================================
@events.register(events.NewMessage)
async def ai_handler(event):
    global ai_active, ai_brain, AI_SYSTEM_PROMPT, FALLBACK_MODELS, current_model_for_chat
    global groq_client, cerebras_client
    
    if not event.is_private:
        return
    if event.out:
        return
    if event.sender and event.sender.bot:
        return
    if not ai_active:
        return
    if event.raw_text and event.raw_text.startswith('!'):
        return
    if not event.chat_id:
        return
    
    try:
        chat = await event.client.get_entity(event.chat_id)
    except:
        return
    
    chat_id = str(event.chat_id)
    user_message = event.raw_text
    sender_name = "Пользователь"
    sender_phone = None
    sender_username = None
    
    try:
        if event.sender and event.sender.first_name:
            sender_name = event.sender.first_name
        if event.sender and hasattr(event.sender, 'phone'):
            sender_phone = event.sender.phone
        if event.sender and event.sender.username:
            sender_username = event.sender.username
    except:
        pass
    
    print(f"🤖 AI получил от {sender_name}: {user_message[:50]}...")
    
    try:
        async with event.client.action(chat, 'typing'):
            
            if chat_id not in ai_brain:
                ai_brain[chat_id] = []
                print(f"🧠 Создан новый мозг для чата {chat_id}")
            
            ai_brain[chat_id].append({
                "role": "user",
                "name": sender_name,
                "phone": sender_phone,
                "username": sender_username,
                "text": user_message,
                "time": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            
            if len(ai_brain[chat_id]) > 50:
                ai_brain[chat_id] = ai_brain[chat_id][-50:]
            
            save_ai_brain(ai_brain)
            
            history = [f"Система: {AI_SYSTEM_PROMPT}"]
            for msg in ai_brain[chat_id]:
                if msg["role"] == "user":
                    history.append(f"{msg['name']}: {msg['text']}")
                else:
                    history.append(f"AI: {msg['text']}")
            history.append("AI:")
            
            full_prompt = "\n".join(history)
            ai_reply = None
            
            # 1. GEMINI
            if not ai_reply:
                print("⏳ Пробую Gemini...")
                models_to_try = []
                if chat_id in current_model_for_chat:
                    models_to_try.append(current_model_for_chat[chat_id])
                    models_to_try.extend([m for m in FALLBACK_MODELS if m != current_model_for_chat[chat_id]])
                else:
                    models_to_try = FALLBACK_MODELS
                
                for model_name in models_to_try:
                    try:
                        response = await asyncio.wait_for(
                            asyncio.to_thread(
                                gemini_client.models.generate_content,
                                model=model_name,
                                contents=full_prompt
                            ),
                            timeout=30
                        )
                        ai_reply = response.text
                        current_model_for_chat[chat_id] = model_name
                        print(f"✅ Gemini ({model_name}) сработал!")
                        break
                    except Exception as e:
                        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                            print(f"⚠️ Gemini лимит, пробую следующего...")
                            continue
                        else:
                            print(f"❌ Gemini ошибка: {e}")
                            continue
            
            # 2. GROQ
            if not ai_reply:
                print("⏳ Пробую Groq...")
                try:
                    messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}]
                    for msg in ai_brain[chat_id]:
                        if msg["role"] == "user":
                            messages.append({"role": "user", "content": msg["text"]})
                        else:
                            messages.append({"role": "assistant", "content": msg["text"]})
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            groq_client.chat.completions.create,
                            model="llama-3.3-70b-versatile",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=500
                        ),
                        timeout=30
                    )
                    ai_reply = response.choices[0].message.content
                    print(f"✅ Groq сработал!")
                except Exception as e:
                    if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                        print(f"⚠️ Groq лимит, пробую следующего...")
                    else:
                        print(f"❌ Groq ошибка: {e}")
            
            # 3. CEREBRAS
            if not ai_reply:
                print("⏳ Пробую Cerebras...")
                try:
                    messages = [{"role": "system", "content": AI_SYSTEM_PROMPT}]
                    for msg in ai_brain[chat_id]:
                        if msg["role"] == "user":
                            messages.append({"role": "user", "content": msg["text"]})
                        else:
                            messages.append({"role": "assistant", "content": msg["text"]})
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            cerebras_client.chat.completions.create,
                            model="llama-3.3-70b",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=500
                        ),
                        timeout=30
                    )
                    ai_reply = response.choices[0].message.content
                    print(f"✅ Cerebras сработал!")
                except Exception as e:
                    print(f"❌ Cerebras ошибка: {e}")
            
            if not ai_reply:
                ai_reply = "😵 Все AI устали на сегодня. Напиши Илье: @mo1chu"
            
            ai_brain[chat_id].append({
                "role": "assistant",
                "text": ai_reply,
                "time": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            save_ai_brain(ai_brain)
            
            print(f"📥 Ответ: {ai_reply[:50]}...")
            await event.client.send_message(chat, ai_reply)
            print(f"📤 Отправлено!")
            
    except Exception as e:
        print(f"❌ Критическая ошибка в ai_handler: {e}")
        try:
            await event.client.send_message(chat, "😵 Что-то сломалось. Илья скоро починит!")
        except:
            pass

# ============================================
# ФУНКЦИЯ ТРОЛЛИНГ-СПАМА
# ============================================
async def troll_spam_all_chains(client, chat, count, delay_ms):
    global troll_stop_flag, TROLL_CHAINS
    troll_stop_flag = False
    if chat is None:
        return
    print(f"🎭 Троллинг-спам: прогоняю ВСЕ {len(TROLL_CHAINS)} цепочек {count} раз, задержка {delay_ms}мс")
    delay = delay_ms / 1000.0
    for cycle in range(count):
        if troll_stop_flag:
            print("⏹ Троллинг-спам остановлен!")
            break
        for chain_index, chain in enumerate(TROLL_CHAINS):
            if troll_stop_flag:
                break
            for word in chain:
                if troll_stop_flag:
                    break
                try:
                    await client.send_message(chat, word)
                    await asyncio.sleep(delay)
                except Exception as e:
                    print(f"❌ Ошибка троллинг-спама: {e}")
                    troll_stop_flag = True
                    break

# ============================================
# МОНИТОРИНГ КАНАЛОВ
# ============================================
@events.register(events.NewMessage)
async def channel_monitor_handler(event):
    global monitor_active, monitored_channels, TRIGGER_WORDS, troll_stop_flag, TROLL_CHAINS
    
    if event.is_private:
        return
    if event.out:
        return
    if not event.raw_text:
        return
    
    text = event.raw_text.lower()
    chat = await event.get_chat()
    
    if 'банан' in text:
        print(f"🍌 Найдено слово 'банан' в канале {chat.title or chat.username}! Запускаю троллинг...")
        await asyncio.sleep(random.uniform(0.5, 1.5))
        try:
            await troll_spam_all_chains(event.client, chat, 1, 170)
            print(f"✅ Троллинг запущен по триггеру 'банан'")
        except Exception as e:
            print(f"❌ Ошибка при запуске троллинга по триггеру: {e}")
    
    if not monitor_active:
        return
    
    if monitored_channels:
        chat_id_str = str(chat.id)
        chat_username = f"@{chat.username}" if chat.username else ""
        channel_match = False
        for channel in monitored_channels:
            if channel == chat_id_str or channel == chat_username:
                channel_match = True
                break
        if not channel_match:
            return
    
    found_words = []
    for word in TRIGGER_WORDS:
        if word != 'банан' and word.lower() in text:
            found_words.append(word)
    
    if found_words:
        words_str = ", ".join(found_words)
        print(f"🔍 Найдено слово '{words_str}' в канале {chat.title or chat.username}")
        reply_text = f"✅ Заметил '{found_words[0]}'!"
        await asyncio.sleep(random.uniform(0.5, 1.5))
        try:
            await event.client.send_message(chat, reply_text, comment_to=event.id)
            print(f"✅ Отправил ответ в канал {chat.title or chat.username}")
        except Exception as e:
            print(f"❌ Ошибка при отправке ответа: {e}")

# ============================================
# ОБРАБОТЧИК АВТОСПАМА
# ============================================
@events.register(events.NewMessage)
async def auto_spam_handler(event):
    global stop_spam_flag, auto_spam_tasks
    
    if event.is_private:
        return
    
    if not event.message.fwd_from and event.chat:
        channel_id = event.chat_id
        channel_username = event.chat.username if event.chat else None
        
        for task_id, task in auto_spam_tasks.items():
            if not task.get('active', False):
                continue
            
            task_channel = task.get('channel', '')
            
            try:
                if str(channel_id) == str(task_channel):
                    trigger = True
                else:
                    trigger = False
            except:
                trigger = False
            
            if not trigger and channel_username and f"@{channel_username}" == task_channel:
                trigger = True
            
            if not trigger and task_channel.lstrip('-').isdigit() and int(task_channel) == channel_id:
                trigger = True
            
            if trigger:
                print(f"🔔 Новый пост на канале {task_channel}! Задание #{task_id}")
                stop_spam_flag = False
                count = task.get('count', 2)
                delay = task.get('delay', 1)
                text = task.get('text', 'ы')
                for i in range(count):
                    if stop_spam_flag:
                        break
                    try:
                        await event.client.send_message(event.chat, text, comment_to=event.id)
                        await asyncio.sleep(delay / 1000.0)
                    except:
                        break

# ============================================
# ОБРАБОТЧИК ИГРЫ В СУЕФА
# ============================================
@events.register(events.NewMessage)
async def suefa_game_handler(event):
    global suefa_games
    
    chat_id = event.chat_id
    user_id = event.sender_id
    text = event.raw_text.lower().strip()
    
    if chat_id not in suefa_games:
        return
    
    game = suefa_games[chat_id]
    
    if user_id not in [game['player1'], game['player2']]:
        return
    
    if game['turn'] != user_id:
        return
    
    if text not in ['камень', 'ножницы', 'бумага']:
        return
    
    game['choices'][user_id] = text
    await event.delete()
    game['turn'] = game['player2'] if user_id == game['player1'] else game['player1']
    
    try:
        player1 = await event.client.get_entity(game['player1'])
        player2 = await event.client.get_entity(game['player2'])
        name1 = f"@{player1.username}" if player1.username else player1.first_name
        name2 = f"@{player2.username}" if player2.username else player2.first_name
    except:
        name1 = f"Игрок {game['player1']}"
        name2 = f"Игрок {game['player2']}"
    
    current_player = game['turn']
    current_name = name1 if current_player == game['player1'] else name2
    await event.client.send_message(chat_id, f"⏳ Ход: {current_name}")
    
    if game['player1'] in game['choices'] and game['player2'] in game['choices']:
        p1_choice = game['choices'][game['player1']]
        p2_choice = game['choices'][game['player2']]
        
        if p1_choice == p2_choice:
            result = "🤝 Ничья!"
        elif (p1_choice == 'камень' and p2_choice == 'ножницы') or \
             (p1_choice == 'ножницы' and p2_choice == 'бумага') or \
             (p1_choice == 'бумага' and p2_choice == 'камень'):
            result = f"🏆 Победил {name1} ({p1_choice} > {p2_choice})!"
        else:
            result = f"🏆 Победил {name2} ({p2_choice} > {p1_choice})!"
        
        await event.client.send_message(chat_id, 
            f"🎮 **Игра завершена!**\n\n"
            f"{name1}: {p1_choice}\n"
            f"{name2}: {p2_choice}\n\n"
            f"{result}"
        )
        del suefa_games[chat_id]

# ============================================
# ОБРАБОТЧИК КОМАНД
# ============================================
@events.register(events.NewMessage(outgoing=True, pattern=r'^!'))
async def command_handler(event):
    global stop_spam_flag, sticker_pack, auto_spam_tasks, next_task_id
    global suefa_games, ai_active, ai_brain
    global monitor_active, monitored_channels, TRIGGER_WORDS
    global troll_stop_flag, TROLL_CHAINS
    global current_model_for_chat
    
    args = parse_args(event.raw_text[1:].strip())
    if not args:
        await event.edit(SHORT_MENU, parse_mode='md')
        return

    cmd = args[0].lower()
    chat_id = event.chat_id

    if cmd in ('меню', 'help'):
        await event.edit(FULL_MENU, parse_mode='md')
        return
    
    if cmd in ('короткое', 'short'):
        await event.edit(SHORT_MENU, parse_mode='md')
        return

    elif cmd == 'обомне':
        await event.edit(ABOUT_ME, parse_mode='md')
        return

    elif cmd == 'обскрипте':
        await event.edit(ABOUT_SCRIPT, parse_mode='md')
        return

    # ========== AI КОМАНДЫ ==========
    elif cmd == 'ai':
        if len(args) < 2:
            status = "✅ ВКЛ" if ai_active else "❌ ВЫКЛ"
            await event.edit(
                f"🤖 **AI-автоответчик**\n\n"
                f"Статус: {status}\n\n"
                f"`!ai вкл` — включить\n"
                f"`!ai выкл` — выключить\n"
                f"`!ai статус` — показать статус",
                parse_mode='md'
            )
            return
        
        if args[1] == 'вкл':
            ai_active = True
            await event.edit("✅ **AI-автоответчик включён!**", parse_mode='md')
            print("🤖 AI ВКЛЮЧЁН")
        elif args[1] == 'выкл':
            ai_active = False
            await event.edit("❌ **AI-автоответчик выключен**", parse_mode='md')
            print("🤖 AI ВЫКЛЮЧЕН")
        elif args[1] == 'статус':
            status = "✅ ВКЛ" if ai_active else "❌ ВЫКЛ"
            await event.edit(f"🤖 **AI-автоответчик:** {status}", parse_mode='md')

    # ========== УПРАВЛЕНИЕ МОЗГОМ ==========
    elif cmd == 'мозг':
        if len(args) < 2:
            chat_id_str = str(chat_id)
            if chat_id_str in ai_brain:
                size = len(ai_brain[chat_id_str])
                await event.edit(f"🧠 **Мозг AI для этого чата**\n\nСообщений: {size}\n\n`!мозг очистить` — стереть память\n`!мозг показать` — показать последние 5 сообщений", parse_mode='md')
            else:
                await event.edit("🧠 **Мозг для этого чата пуст**", parse_mode='md')
            return
        
        if args[1] == 'очистить':
            chat_id_str = str(chat_id)
            if chat_id_str in ai_brain:
                ai_brain[chat_id_str] = []
                save_ai_brain(ai_brain)
                await event.edit("🧹 **Мозг AI для этого чата очищен!**", parse_mode='md')
            else:
                await event.edit("📭 **Мозг и так пуст**", parse_mode='md')
        
        elif args[1] == 'показать':
            chat_id_str = str(chat_id)
            if chat_id_str in ai_brain and ai_brain[chat_id_str]:
                text = "🧠 **Последние сообщения:**\n\n"
                for msg in ai_brain[chat_id_str][-5:]:
                    if msg["role"] == "user":
                        text += f"👤 {msg.get('name', 'Пользователь')}: {msg['text'][:50]}\n"
                    else:
                        text += f"🤖 AI: {msg['text'][:50]}\n"
                await event.edit(text, parse_mode='md')
            else:
                await event.edit("📭 **История пуста**", parse_mode='md')

    # ========== ТРОЛЛИНГ-СПАМ ==========
    elif cmd == 'троль':
        if len(args) < 2:
            await event.edit(
                f"👿 **Троллинг-спам**\n\n"
                f"`!троль [кол-во] [мс]` — прогнать ВСЕ цепочки\n"
                f"Пример: `!троль 1 170` — 1 раз все цепочки\n"
                f"`!троль стоп` — остановить\n\n"
                f"🔫 Триггер 'банан' запускает `!троль 1 170`\n\n"
                f"Всего цепочек: {len(TROLL_CHAINS)}",
                parse_mode='md'
            )
            return
        
        if args[1] == 'стоп':
            troll_stop_flag = True
            await event.edit("⏹ **Троллинг-спам остановлен!**", parse_mode='md')
            return
        
        try:
            count = int(args[1])
            delay = int(args[2])
            await event.delete()
            chat = await event.client.get_entity(chat_id)
            await troll_spam_all_chains(event.client, chat, count, delay)
        except ValueError:
            await event.edit("❌ Ошибка. Используй: `!троль [кол-во] [мс]`", parse_mode='md')
            return
        except Exception as e:
            await event.edit(f"❌ Ошибка: {e}", parse_mode='md')
            return

    # ========== МОНИТОРИНГ КАНАЛОВ ==========
    elif cmd == 'монитор':
        if len(args) < 2:
            status = "✅ ВКЛ" if monitor_active else "❌ ВЫКЛ"
            channel_count = len(monitored_channels) if monitored_channels else "все"
            await event.edit(
                f"📡 **Мониторинг каналов:** {status}\n"
                f"📊 Отслеживается каналов: {channel_count}\n"
                f"🔍 Ключевые слова: {', '.join(TRIGGER_WORDS)}\n\n"
                f"`!монитор вкл` — включить\n"
                f"`!монитор выкл` — выключить\n"
                f"`!монитор слова [слово1, слово2]` — установить слова\n"
                f"`!монитор каналы [@канал1, @канал2]` — указать каналы\n"
                f"`!монитор каналы все` — отслеживать все каналы",
                parse_mode='md'
            )
            return
        
        if args[1] == 'вкл':
            monitor_active = True
            await event.edit("✅ **Мониторинг каналов включён!**", parse_mode='md')
        elif args[1] == 'выкл':
            monitor_active = False
            await event.edit("❌ **Мониторинг каналов выключен**", parse_mode='md')
        elif args[1] == 'слова' and len(args) >= 3:
            words_text = ' '.join(args[2:])
            TRIGGER_WORDS = [w.strip().lower() for w in words_text.split(',')]
            await event.edit(f"✅ **Ключевые слова обновлены:**\n{', '.join(TRIGGER_WORDS)}", parse_mode='md')
        elif args[1] == 'каналы' and len(args) >= 3:
            if args[2] == 'все':
                monitored_channels = []
                await event.edit("📡 **Отслеживаются ВСЕ каналы**", parse_mode='md')
            else:
                channels_text = ' '.join(args[2:])
                monitored_channels = [c.strip() for c in channels_text.split(',')]
                await event.edit(f"✅ **Отслеживаются каналы:**\n{', '.join(monitored_channels)}", parse_mode='md')

    # ========== СТОП ==========
    elif cmd == 'стоп':
        stop_spam_flag = True
        troll_stop_flag = True
        await event.edit("⏹ Все спамы остановлены!")
        return

    # ========== ОБЫЧНЫЙ СПАМ ==========
    elif cmd == 'с':
        if len(args) < 4:
            await event.edit("❌ Использование: `!с [кол] [мс] [текст]`", parse_mode='md')
            return
        try:
            count = int(args[1])
            delay = int(args[2])
            text = ' '.join(args[3:])
        except ValueError:
            await event.edit("❌ Кол-во и задержка должны быть числами", parse_mode='md')
            return
        await event.delete()
        chat = await event.client.get_entity(chat_id)
        await spam(event.client, chat, count, delay, text)

    # ========== СКРЫТЫЙ СПАМ ==========
    elif cmd == 'сг':
        if len(args) < 4:
            await event.edit("❌ Использование: `!сг [кол] [мс] [текст]`", parse_mode='md')
            return
        try:
            count = int(args[1])
            delay = int(args[2])
            text = ' '.join(args[3:])
        except ValueError:
            await event.edit("❌ Кол-во и задержка должны быть числами", parse_mode='md')
            return
        await event.delete()
        chat = await event.client.get_entity(chat_id)
        await spam(event.client, chat, count, delay, text, delete_after=True)

    # ========== КОПИРОВАНИЕ ==========
    elif cmd == 'к':
        if len(args) < 2:
            await event.edit("❌ Использование: `!к [кол-во]`", parse_mode='md')
            return
        try:
            limit = int(args[1])
        except ValueError:
            await event.edit("❌ Кол-во должно быть числом", parse_mode='md')
            return
        await event.delete()
        chat = await event.client.get_entity(chat_id)
        await copy_messages(event.client, chat, chat, limit)

    elif cmd == 'к1':
        if not event.is_reply:
            await event.edit("❌ Ответь на сообщение, которое хочешь скопировать!", parse_mode='md')
            return
        reply_msg = await event.get_reply_message()
        await event.delete()
        chat = await event.client.get_entity(chat_id)
        await copy_one_message(event.client, reply_msg, chat)

    # ========== СТИКЕРЫ ==========
    elif cmd == '+стикер':
        if not event.is_reply:
            await event.edit("❌ Ответь на стикер, чтобы добавить его в коллекцию!", parse_mode='md')
            return
        
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sticker:
            sticker_data = {
                'id': reply_msg.id,
                'chat_id': reply_msg.chat_id,
                'emoji': reply_msg.sticker.emoji if reply_msg.sticker.emoji else '🎯'
            }
            sticker_pack.append(sticker_data)
            await event.edit(f"✅ Стикер добавлен! Номер: {len(sticker_pack)}", parse_mode='md')
        else:
            await event.edit("❌ Это не стикер!", parse_mode='md')
    
    elif cmd == 'стикеры':
        if not sticker_pack:
            await event.edit("📭 Список стикеров пуст. Добавь через `!+стикер`", parse_mode='md')
            return
        
        text = "🎭 **Сохранённые стикеры:**\n\n"
        for i, sticker in enumerate(sticker_pack, 1):
            emoji = sticker.get('emoji', '🎯')
            text += f"{i}. {emoji}\n"
        await event.edit(text, parse_mode='md')

    elif cmd == 'ст':
        if len(args) < 4:
            await event.edit("❌ Использование: `!ст [кол] [мс] [номер]`", parse_mode='md')
            return
        try:
            count = int(args[1])
            delay = int(args[2])
            num = int(args[3])
            if num < 1 or num > len(sticker_pack):
                await event.edit("❌ Стикер не найден", parse_mode='md')
                return
            await event.delete()
            chat = await event.client.get_entity(chat_id)
            sticker = sticker_pack[num-1]
            await sticker_spam(event.client, chat, count, delay, sticker)
        except ValueError:
            await event.edit("❌ Все аргументы должны быть числами", parse_mode='md')
            return

    # ========== УДАЛИТЬ СВОИ ==========
    elif cmd == 'уд':
        if len(args) < 2:
            await event.edit("❌ Использование: `!уд [кол-во]`", parse_mode='md')
            return
        try:
            limit = int(args[1])
        except ValueError:
            await event.edit("❌ Кол-во должно быть числом", parse_mode='md')
            return
        await event.delete()
        chat = await event.client.get_entity(chat_id)
        await delete_own_messages(event.client, chat, limit)

    # ========== КАЛЬКУЛЯТОР ==========
    elif cmd == 'кальк':
        if len(args) < 2:
            await event.edit("❌ Использование: `!кальк [выражение]`\nПример: `!кальк 2+2*2`", parse_mode='md')
            return
        
        expression = ' '.join(args[1:])
        result, error = calculate(expression)
        
        if error:
            await event.edit(f"❌ {error}", parse_mode='md')
        else:
            await event.edit(f"🧮 **{expression} = {result}**", parse_mode='md')

    # ========== ИГРА В СУЕФА ==========
    elif cmd == 'суефа':
        if chat_id in suefa_games:
            await event.edit("❌ В этом чате уже идет игра!", parse_mode='md')
            return
        
        if event.is_private:
            me = await event.client.get_me()
            player1 = event.sender_id
            player2 = me.id
            
            suefa_games[chat_id] = {
                'player1': player1,
                'player2': player2,
                'turn': player1,
                'choices': {}
            }
            
            try:
                p1 = await event.client.get_entity(player1)
                p2 = await event.client.get_entity(player2)
                name1 = f"@{p1.username}" if p1.username else p1.first_name
                name2 = f"@{p2.username}" if p2.username else p2.first_name
            except:
                name1 = f"Игрок {player1}"
                name2 = "Илья"
            
            await event.edit(
                f"🎮 **Игра в Суефа началась! (ЛС)**\n\n"
                f"Ты: {name1}\n"
                f"Илья: {name2}\n\n"
                f"Первый ход: {name1}\n\n"
                f"Пиши: `камень`, `ножницы` или `бумага`",
                parse_mode='md'
            )
        else:
            try:
                participants = await event.client.get_participants(chat_id, limit=20)
                if len(participants) < 2:
                    await event.edit("❌ В группе должно быть минимум 2 участника!", parse_mode='md')
                    return
            except:
                await event.edit("❌ Не удалось получить список участников", parse_mode='md')
                return
            
            me = await event.client.get_me()
            available = [p for p in participants if p.id != me.id]
            
            if len(available) < 2:
                await event.edit("❌ Недостаточно игроков (нужно минимум 2 человека)", parse_mode='md')
                return
            
            players = random.sample(available, 2)
            player1, player2 = players[0].id, players[1].id
            
            suefa_games[chat_id] = {
                'player1': player1,
                'player2': player2,
                'turn': player1,
                'choices': {}
            }
            
            name1 = f"@{players[0].username}" if players[0].username else players[0].first_name
            name2 = f"@{players[1].username}" if players[1].username else players[1].first_name
            
            await event.edit(
                f"🎮 **Игра в Суефа началась!**\n\n"
                f"Игрок 1: {name1}\n"
                f"Игрок 2: {name2}\n\n"
                f"Первый ход: {name1}\n\n"
                f"Пиши: `камень`, `ножницы` или `бумага`",
                parse_mode='md'
            )

    # ========== ГОЛОСОВОЕ СООБЩЕНИЕ ==========
    elif cmd == 'гс':
        if len(args) < 2:
            await event.edit("❌ Использование: `!гс [текст]` или `!гс [голос] [текст]`\nГолоса: alloy, echo, fable, onyx, nova, shimmer", parse_mode='md')
            return
        
        voice = "echo"
        text_start = 1
        
        if args[1].lower() in ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']:
            voice = args[1].lower()
            text_start = 2
        
        if len(args) <= text_start:
            await event.edit("❌ Нужен текст для озвучки", parse_mode='md')
            return
        
        text = ' '.join(args[text_start:])
        await event.delete()
        await text_to_voice(event.client, chat_id, text, voice)

    # ========== АНИМАЦИЯ ТЕКСТА ==========
    elif cmd == 'текст':
        if len(args) < 2:
            await event.edit("❌ Использование: `!текст [текст]`\nПример: `!текст Привет мир`", parse_mode='md')
            return
        
        text_parts = []
        duration = 5
        frames = 20
        
        i = 1
        while i < len(args):
            if i == 1 and args[1].replace('.', '').isdigit():
                duration = float(args[1])
                i += 1
                if i < len(args) and args[i].replace('.', '').isdigit():
                    frames = int(args[i])
                    i += 1
                text_parts = args[i:]
                break
            else:
                text_parts = args[1:]
                break
        
        text = ' '.join(text_parts) if text_parts else ''
        if not text:
            await event.edit("❌ Нужен текст для анимации", parse_mode='md')
            return
        
        await event.delete()
        await animate_text_appear(event.client, chat_id, text, duration, frames)

    elif cmd == 'текст2':
        if len(args) < 2:
            await event.edit("❌ Использование: `!текст2 [текст]`\nПример: `!текст2 Привет мир`", parse_mode='md')
            return
        
        text_parts = []
        duration = 10
        interval = 0.3
        
        i = 1
        while i < len(args):
            if i == 1 and args[1].replace('.', '').isdigit():
                duration = float(args[1])
                i += 1
                if i < len(args) and args[i].replace('.', '').isdigit():
                    interval = float(args[i])
                    i += 1
                text_parts = args[i:]
                break
            else:
                text_parts = args[1:]
                break
        
        text = ' '.join(text_parts) if text_parts else ''
        if not text:
            await event.edit("❌ Нужен текст для анимации", parse_mode='md')
            return
        
        await event.delete()
        await animate_text_flicker(event.client, chat_id, text, duration, interval)

    # ========== АВТОСПАМ ==========
    elif cmd == 'автоспам':
        if len(args) < 5:
            await event.edit("❌ Использование: `!автоспам [канал] [кол] [мс] [текст]`", parse_mode='md')
            return
        try:
            channel = args[1]
            count = int(args[2])
            delay = int(args[3])
            text = ' '.join(args[4:])
            
            chat = await get_chat(event.client, channel)
            if not chat:
                await event.edit(f"❌ Канал {channel} не найден")
                return
            
            task_id = next_task_id
            next_task_id += 1
            
            auto_spam_tasks[task_id] = {
                'channel': channel,
                'count': count,
                'delay': delay,
                'text': text,
                'active': True,
                'created': datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            
            await event.edit(f"✅ Автоспам создан! ID: {task_id}", parse_mode='md')
        except ValueError:
            await event.edit("❌ Кол-во и задержка должны быть числами", parse_mode='md')

    elif cmd == 'автоспамы':
        if not auto_spam_tasks:
            await event.edit("📭 Нет активных автоспамов")
            return
        
        text = "🔄 **Активные автоспамы:**\n\n"
        for task_id, task in auto_spam_tasks.items():
            if task.get('active'):
                text += f"ID {task_id}: {task['channel']} | {task['count']}×{task['delay']}мс\n"
        await event.edit(text, parse_mode='md')

    elif cmd == 'автостоп':
        if len(args) < 2:
            await event.edit("❌ Использование: `!автостоп [ID]`", parse_mode='md')
            return
        try:
            tid = int(args[1])
            if tid in auto_spam_tasks:
                auto_spam_tasks[tid]['active'] = False
                await event.edit(f"✅ Автоспам #{tid} отключён!")
            else:
                await event.edit(f"❌ Задание #{tid} не найдено")
        except ValueError:
            await event.edit("❌ ID должен быть числом")

    # ========== ПОЛЕЗНОЕ ==========
    elif cmd == 'профиль':
        try:
            if len(args) < 2:
                user = await event.client.get_me()
            else:
                user = await event.client.get_entity(args[1].strip('@'))
            text = f"👤 {user.first_name}\nID: `{user.id}`\n@ {user.username or 'нет'}"
            await event.edit(text, parse_mode='md')
        except:
            await event.edit("❌ Пользователь не найден", parse_mode='md')

    elif cmd == 'чат':
        chat = await event.client.get_entity(chat_id)
        name = getattr(chat, 'title', getattr(chat, 'first_name', 'Чат'))
        await event.edit(f"💬 {name}\nID: `{chat.id}`", parse_mode='md')

    elif cmd == 'дата':
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        await event.edit(f"📅 {now}", parse_mode='md')

    elif cmd == 'айди':
        await event.edit(f"🆔 `{chat_id}`", parse_mode='md')

    elif cmd == 'кто':
        try:
            users = await event.client.get_participants(chat_id, limit=20)
            if users:
                user = random.choice(users)
                name = user.first_name
                if user.last_name:
                    name += f" {user.last_name}"
                await event.edit(f"🎲 {name}", parse_mode='md')
        except:
            await event.edit("❌ Работает только в группах", parse_mode='md')

    elif cmd == 'пинг':
        await event.edit("🏓 Понг!", parse_mode='md')

    elif cmd in ('выход', 'exit', 'quit'):
        await event.edit("👋 Пока!")
        await event.client.disconnect()
        return

    else:
        await event.edit("❌ Неизвестная команда. Введи `!` для короткого меню или `!меню` для полного.", parse_mode='md')

# ============================================
# ЗАПУСК
# ============================================
async def main():
    print("="*60)
    print("👻 GHOST BOT v18.0 — ДЛЯ RAILWAY 👻")
    print("="*60)
    print("👑 Создатель: @mo1chu (Илья)")
    print("="*60)
    
    print(f"✅ Azure OpenAI ключ: {'есть' if AZURE_OPENAI_KEY else 'нет'}")
    print(f"✅ Gemini ключ: {'есть' if GEMINI_API_KEY else 'нет'}")
    print(f"✅ Groq ключ: {'есть' if GROQ_API_KEY else 'нет'}")
    print(f"✅ Cerebras ключ: {'есть' if CEREBRAS_API_KEY else 'нет'}")
    print(f"✅ Загружено троллинг-цепочек: {len(TROLL_CHAINS)}")
    print(f"🍌 Триггер 'банан' активен")
    print(f"🧠 Загружено диалогов в мозг AI: {len(ai_brain)}")
    print(f"👩 Персональные настройки: Вероника, Арина")
    print(f"🤖 AI по умолчанию: ВЫКЛ (включи командой !ai вкл)")
    print("="*60)
    print("🚀 Бот запускается...")
    
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    try:
        await client.start()
    except SessionPasswordNeededError:
        print("🔐 ОШИБКА: Требуется 2FA, но на сервере нет ввода!")
        print("📌 Сгенерируй .session файл локально и загрузи его на Railway с Volume")
        return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    me = await client.get_me()
    print(f"✅ Вошёл как: {me.first_name}")
    
    global next_task_id, auto_spam_tasks
    auto_spam_tasks[next_task_id] = {
        'channel': '@ebelexu',
        'count': 2,
        'delay': 1,
        'text': 'ы',
        'active': True
    }
    print(f"✅ Автоспам для @ebelexu включён (ID: {next_task_id})")
    next_task_id += 1
    
    client.add_event_handler(command_handler)
    client.add_event_handler(auto_spam_handler)
    client.add_event_handler(suefa_game_handler)
    client.add_event_handler(ai_handler)
    client.add_event_handler(channel_monitor_handler)
    
    print("="*60)
    print("✅ БОТ ЗАПУЩЕН НА RAILWAY!")
    print("📱 Введи `!` для короткого меню")
    print("📱 Введи `!меню` для полного меню")
    print("🤖 AI автоответчик: !ai вкл / !ai выкл")
    print("="*60)
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Выход...")