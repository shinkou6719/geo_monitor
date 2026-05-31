from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, delete, func

import geo_monitor.models
from geo_monitor.config import settings
from geo_monitor.database import AsyncSessionLocal
from geo_monitor.models.geo import Geo
from geo_monitor.models.news import News
from geo_monitor.services.news_service import NewsService
from geo_monitor.services.ai_service import AIService
from geo_monitor.models.idea import Idea
from geo_monitor.models.headline import Headline

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()

dp.include_router(router)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🌍 GEO Monitor AI\n\n"
        "Доступные команды:\n\n"
        "/list_geos - список GEO\n"
        "/latest DE - последние новости\n"
        "/analyze DE - AI анализ новостей\n"
        "/ideas DE - генерация идей и углов\n"
        "/saved_ideas DE - сохранённые идеи из БД\n"
        "/refresh DE - обновить новости из RSS\n"
        "/clear_db - очистить новости, идеи и заголовки\n"
        "/weekly_report DE - отчёт по GEO\n"
    )

@router.message(Command("ideas"))
async def cmd_ideas(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Укажи GEO код.\n\nПример:\n/ideas DE")
        return

    geo_code = args[1].upper()
    await message.answer(f"🧠 Генерирую идеи для {geo_code}...")

    async with AsyncSessionLocal() as db:
        geo = await db.scalar(select(Geo).where(Geo.code == geo_code))

        if not geo:
            await message.answer(f"GEO {geo_code} не найден.")
            return

        result = await db.execute(
            select(News)
            .where(News.geo_id == geo.id)
            .order_by(News.published_at.desc())
            .limit(3)
        )

        news_list = result.scalars().all()

        if not news_list:
            await message.answer(f"Новостей для {geo_code} пока нет.")
            return

        ai = AIService()

        for item in news_list:
            item_title = item.title
            item_id = item.id

            try:
                idea_data = await ai.generate_idea_json(item_title)

                idea = Idea(
                    news_id=item_id,
                    angle=idea_data.get("angle", ""),
                    offer_connection=idea_data.get("offer_connection", ""),
                    audience_pain=idea_data.get("audience_pain", ""),
                    creative_type=idea_data.get("creative_type", "news"),
                    priority=idea_data.get("priority", "C"),
                    freshness_days=idea_data.get("freshness_days", 7),
                    trigger_strength=idea_data.get("trigger_strength", 5),
                    offer_match=idea_data.get("offer_match", 5),
                )

                db.add(idea)
                await db.flush()

                headlines_text = ""

                for h in idea_data.get("headlines", []):
                    headline_text = h.get("text", "")

                    db.add(
                        Headline(
                            idea_id=idea.id,
                            text=headline_text,
                            format=h.get("format", "intrigue"),
                        )
                    )

                    headlines_text += f"• {headline_text}\n"

                await db.commit()

                text = (
                    f"🔥 <b>{item_title}</b>\n\n"
                    f"<b>Угол:</b> {idea.angle}\n\n"
                    f"<b>Связь с оффером:</b> {idea.offer_connection}\n\n"
                    f"<b>Боль аудитории:</b> {idea.audience_pain}\n\n"
                    f"<b>Тип:</b> {idea.creative_type}\n"
                    f"<b>Приоритет:</b> {idea.priority}\n"
                    f"<b>Сила триггера:</b> {idea.trigger_strength}/10\n"
                    f"<b>Совпадение с оффером:</b> {idea.offer_match}/10\n\n"
                    f"<b>Заголовки:</b>\n{headlines_text}\n"
                    f"✅ Сохранено в БД"
                )

                await message.answer(text, parse_mode="HTML")

            except Exception as e:
                await db.rollback()

                error_text = str(e)

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "quota" in error_text.lower()
                ):
                    await message.answer(
                        "⚠️ Лимит Gemini API исчерпан.\n\n"
                        "Новости уже сохранены в БД, но AI-идеи сейчас не могут быть сгенерированы.\n"
                        "Попробуй позже или используй другой API-ключ."
                    )
                    return

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "high demand" in error_text.lower()
                ):
                    await message.answer(
                        "⚠️ Gemini сейчас перегружен.\n\n"
                        "Новости уже сохранены в БД, но генерация идей временно недоступна.\n"
                        "Попробуй ещё раз через пару минут."
                    )
                    return

                await message.answer(
                    "❌ Ошибка при генерации идеи.\n\n"
                    f"Новость: {item_title}\n\n"
                    f"Ошибка: {error_text[:500]}"
                )

@router.message(Command("saved_ideas"))
async def cmd_saved_ideas(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Укажи GEO код.\n\nПример:\n/saved_ideas DE")
        return

    geo_code = args[1].upper()

    async with AsyncSessionLocal() as db:
        geo = await db.scalar(select(Geo).where(Geo.code == geo_code))

        if not geo:
            await message.answer(f"GEO {geo_code} не найден.")
            return

        result = await db.execute(
            select(Idea, News)
            .join(News, Idea.news_id == News.id)
            .where(News.geo_id == geo.id)
            .order_by(Idea.created_at.desc())
            .limit(5)
        )

        rows = result.all()

        if not rows:
            await message.answer(f"Сохранённых идей для {geo_code} пока нет.")
            return

        for idea, news in rows:
            h_result = await db.execute(
                select(Headline)
                .where(Headline.idea_id == idea.id)
                .limit(3)
            )

            headlines = h_result.scalars().all()
            headlines_text = ""

            for h in headlines:
                headlines_text += f"• {h.text}\n"

            text = (
                f"💾 <b>Сохранённая идея #{idea.id}</b>\n\n"
                f"<b>Новость:</b> {news.title}\n\n"
                f"<b>Угол:</b> {idea.angle}\n\n"
                f"<b>Связь с оффером:</b> {idea.offer_connection}\n\n"
                f"<b>Боль:</b> {idea.audience_pain}\n\n"
                f"<b>Тип:</b> {idea.creative_type}\n"
                f"<b>Приоритет:</b> {idea.priority}\n"
                f"<b>Триггер:</b> {idea.trigger_strength}/10\n"
                f"<b>Оффер:</b> {idea.offer_match}/10\n\n"
                f"<b>Заголовки:</b>\n{headlines_text}"
            )

            await message.answer(text, parse_mode="HTML")

@router.message(Command("list_geos"))
async def cmd_list_geos(message: Message):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Geo).where(Geo.is_active == True))
        geos = result.scalars().all()

        if not geos:
            await message.answer("GEO пока нет в базе.")
            return

        text = "🌍 Активные GEO:\n\n"
        for geo in geos:
            text += f"• {geo.code} — {geo.name}\n"

        await message.answer(text)

@router.message(Command("clear_db"))
async def cmd_clear_db(message: Message):
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Headline))
        await db.execute(delete(Idea))
        await db.execute(delete(News))

        await db.commit()

    await message.answer(
        "🧹 База очищена.\n\n"
        "Удалены:\n"
        "• новости\n"
        "• идеи\n"
        "• заголовки\n\n"
        "GEO остались."
    )

@router.message(Command("refresh"))
async def cmd_refresh(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Укажи GEO код.\n\nПример:\n/refresh DE")
        return

    geo_code = args[1].upper()
    await message.answer(f"🔄 Обновляю новости для {geo_code}...")

    async with AsyncSessionLocal() as db:
        geo = await db.scalar(select(Geo).where(Geo.code == geo_code))

        if not geo:
            await message.answer(f"GEO {geo_code} не найден.")
            return

        service = NewsService(db)
        saved = await service.fetch_and_store(geo)

        await message.answer(
            f"✅ Новости обновлены.\n\n"
            f"Добавлено новых новостей: {len(saved)}\n\n"
            f"Дальше можно вызвать:\n"
            f"/latest {geo_code}\n"
            f"/analyze {geo_code}\n"
            f"/ideas {geo_code}"
        )
        
@router.message(Command("latest"))
async def cmd_latest(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Укажи GEO код. Например: /latest DE")
        return

    geo_code = args[1].upper()

    async with AsyncSessionLocal() as db:
        geo = await db.scalar(select(Geo).where(Geo.code == geo_code))

        if not geo:
            await message.answer(f"GEO {geo_code} не найден.")
            return

        result = await db.execute(
            select(News)
            .where(News.geo_id == geo.id)
            .order_by(News.published_at.desc())
            .limit(5)
        )

        news_list = result.scalars().all()

        if not news_list:
            await message.answer(f"Новостей для {geo_code} пока нет.")
            return

        text = f"📰 Последние новости для {geo.code} — {geo.name}:\n\n"

        for idx, item in enumerate(news_list, start=1):
            date = (
                item.published_at.strftime("%d.%m.%Y %H:%M")
                if item.published_at
                else "без даты"
            )

            text += (
                f"{idx}. <b>{item.title}</b>\n"
                f"Дата: {date}\n"
                f"<a href=\"{item.url}\">Источник</a>\n\n"
            )

        await message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

@router.message(Command("weekly_report"))
async def cmd_weekly_report(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer(
            "Укажи GEO код.\n\nПример:\n/weekly_report DE"
        )
        return

    geo_code = args[1].upper()

    async with AsyncSessionLocal() as db:
        geo = await db.scalar(
            select(Geo).where(Geo.code == geo_code)
        )

        if not geo:
            await message.answer(
                f"GEO {geo_code} не найден."
            )
            return

        news_count = await db.scalar(
            select(func.count())
            .select_from(News)
            .where(News.geo_id == geo.id)
        )

        ideas_count = await db.scalar(
            select(func.count())
            .select_from(Idea)
            .join(News)
            .where(News.geo_id == geo.id)
        )

        headlines_count = await db.scalar(
            select(func.count())
            .select_from(Headline)
            .join(Idea)
            .join(News)
            .where(News.geo_id == geo.id)
        )

        result = await db.execute(
            select(Idea, News)
            .join(News)
            .where(News.geo_id == geo.id)
            .order_by(Idea.trigger_strength.desc())
            .limit(5)
        )

        top_ideas = result.all()

        text = (
            f"📊 <b>REPORT {geo.code} — {geo.name}</b>\n\n"
            f"📰 Новостей: {news_count}\n"
            f"💡 Идей: {ideas_count}\n"
            f"📝 Заголовков: {headlines_count}\n\n"
            f"🔥 <b>ТОП ИДЕИ</b>\n\n"
        )

        for idx, (idea, news) in enumerate(top_ideas, start=1):
            text += (
                f"{idx}. <b>{news.title}</b>\n"
                f"Приоритет: {idea.priority}\n"
                f"Триггер: {idea.trigger_strength}/10\n"
                f"Угол: {idea.angle[:120]}\n\n"
            )

        await message.answer(
            text,
            parse_mode="HTML"
        )

@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Укажи GEO код. Например: /analyze DE")
        return

    geo_code = args[1].upper()
    await message.answer(f"🧠 Анализирую последние новости для {geo_code}...")

    async with AsyncSessionLocal() as db:
        geo = await db.scalar(select(Geo).where(Geo.code == geo_code))

        if not geo:
            await message.answer(f"GEO {geo_code} не найден.")
            return

        result = await db.execute(
            select(News)
            .where(News.geo_id == geo.id)
            .order_by(News.published_at.desc())
            .limit(5)
        )

        news_list = result.scalars().all()

        if not news_list:
            await message.answer(f"Новостей для {geo_code} пока нет.")
            return

        ai = AIService()
        text = f"🔥 AI-анализ инфоповодов для {geo.code} — {geo.name}\n\n"

        for idx, item in enumerate(news_list, start=1):
            analysis = await ai.analyze_news(item.title)

            text += (
                f"{idx}. <b>{item.title}</b>\n\n"
                f"{analysis}\n\n"
                f"━━━━━━━━━━━━━━\n\n"
            )

        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

async def start_bot():
    await dp.start_polling(bot)