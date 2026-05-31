import json

from google import genai

from geo_monitor.config import settings


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def analyze_news(self, title: str) -> str:
        prompt = f"""
Ты аналитик инфоповодов.

Для новости:

{title}

Верни ответ строго в формате:

Категория:
Триггер:
Срочность:
Краткое описание:
Приоритет:
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    async def generate_idea(self, title: str) -> str:
        prompt = f"""
Ты senior affiliate marketer и performance copywriter.

На основе новости:

{title}

Сгенерируй маркетинговую заготовку для теста.

Верни ответ строго в формате:

Триггер:
Угол:
Связь с оффером:
Боль аудитории:
Тип креатива:
Приоритет:

Заголовки:
1.
2.
3.

Риски:
-
-
-
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

    async def generate_idea_json(self, title: str) -> dict:
        prompt = f"""
Ты senior affiliate marketer и performance copywriter.

На основе новости:

{title}

Сгенерируй маркетинговую идею для теста.

Верни ТОЛЬКО валидный JSON без markdown:

{{
  "angle": "маркетинговый угол",
  "offer_connection": "как связать с оффером",
  "audience_pain": "боль аудитории",
  "creative_type": "news|emotional|expose|personal_story",
  "priority": "A|B|C",
  "freshness_days": 1,
  "trigger_strength": 1,
  "offer_match": 1,
  "headlines": [
    {{
      "text": "заголовок",
      "format": "question|shock|number|quote|intrigue"
    }}
  ]
}}

Сделай 3 заголовка.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)