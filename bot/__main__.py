import asyncio
import re

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message

from bot.core import Configuration, get_logger

logger = get_logger()
config = Configuration()

router = Router()


# Предкомпилируем регулярку для всех банвордов (ускоряет работу)
# Например, config.banwords = ["дурак", "идиот", "тупой"]
BANWORDS_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in config.banwords) + r")\b", re.IGNORECASE
)


@router.message(lambda m: m.chat.id == config.chat_id)
async def message_handler(message: Message) -> None:
    """Отливаливает все сообщения в целевом чате."""
    text = message.text or ""

    # Проверяем через регэксп — ловит даже "идиот!", "дурак,", и т.д.
    match = BANWORDS_PATTERN.search(text)
    if match:
        bad_word = match.group(1)
        await message.answer(f"⚠️ Ваше сообщение содержит запрещённое слово: <b>{bad_word}</b>.")
        try:
            await message.delete()
        except Exception as e:
            logger.exception(f"Failed to delete message: {message.text}: {e}")
        logger.info(f"Deleted message from {message.from_user.id}: {message.text}")  # type: ignore


async def main():
    """Функция запускает бота."""
    try:
        bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True),
        )

        # Dispatcher
        dp = Dispatcher()

        # Register handlers
        dp.include_router(router)

        # Выводим сообщение о запуске бота
        logger.warning(f"Bot @{(await bot.get_me()).username} started up!")

        # Launch polling
        await dp.start_polling(
            bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True
        )
    except KeyboardInterrupt:
        logger.warning("Bot shutdown")
    except Exception as e:
        logger.error(f"Error ({type(e)}) while starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
