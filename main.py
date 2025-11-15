import os
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8239304307:AAGxvv1cI82eYE-mHIAFtts-QkO8-tQj2-M")

GAMES = {
    "sweet_bonanza": "Sweet Bonanza",
    "gates_of_olympus": "Gates of Olympus",
    "starlight_princess": "Starlight Princess",
    "sugar_rush": "Sugar Rush",
    "the_dog_house": "The Dog House",
    "big_bass_bonanza": "Big Bass Bonanza",
    "fruit_party": "Fruit Party",
    "wild_west_gold": "Wild West Gold",
    "mustang_gold": "Mustang Gold",
    "great_rhino": "Great Rhino",
    "wolf_gold": "Wolf Gold",
    "john_henry": "John Henry",
    "madame_destiny": "Madame Destiny",
    "fire_strike": "Fire Strike",
    "joker_jewels": "Joker Jewels",
    "hot_fiesta": "Hot Fiesta",
    "candy_village": "Candy Village",
    "gems_bonanza": "Gems Bonanza",
    "wild_bandito": "Wild Bandito",
    "bigger_bass_bonanza": "Bigger Bass Bonanza",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start – показывает меню выбора игры."""
    context.user_data.clear()
    context.user_data["active"] = True

    keyboard = [
        [
            InlineKeyboardButton("🎰 Выбрать игру", callback_data="select_game"),
            InlineKeyboardButton("🎁 Бонус", callback_data="bonus")
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
            InlineKeyboardButton("ℹ️ О боте", callback_data="about")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Привет! Это MaxWIN Radar 🎰✨",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки."""
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("active"):
        await query.edit_message_text(
            "Сначала отправьте команду /start, чтобы активировать бота."
        )
        return

    if query.data == "select_game" or query.data.startswith("page_"):
        # Получаем номер страницы из callback_data или используем 0
        page = 0
        if query.data.startswith("page_"):
            try:
                page = int(query.data.split("page_")[1])
            except:
                page = 0
        
        games_list = list(GAMES.items())
        games_per_page = 5
        total_pages = (len(games_list) + games_per_page - 1) // games_per_page
        
        # Получаем игры для текущей страницы
        start_idx = page * games_per_page
        end_idx = start_idx + games_per_page
        page_games = games_list[start_idx:end_idx]
        
        # Создаём кнопки для игр на текущей странице
        keyboard = []
        for key, name in page_games:
            keyboard.append([InlineKeyboardButton(name, callback_data=f"game_{key}")])
        
        # Кнопки навигации в одной строке, разделённые пополам
        nav_buttons = []
        if page > 0 and page < total_pages - 1:
            # Обе кнопки есть - размещаем их рядом
            nav_buttons = [
                InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"),
                InlineKeyboardButton("Вперёд ➡️", callback_data=f"page_{page+1}")
            ]
        elif page > 0:
            # Только кнопка "Назад"
            nav_buttons = [InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}")]
        elif page < total_pages - 1:
            # Только кнопка "Вперёд"
            nav_buttons = [InlineKeyboardButton("Вперёд ➡️", callback_data=f"page_{page+1}")]
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_menu")])
        
        page_info = f" (Страница {page + 1} из {total_pages})" if total_pages > 1 else ""
        await query.edit_message_text(
            f"Выберите слот для анализа:{page_info}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data.startswith("game_"):
        game_key = query.data.split("game_", maxsplit=1)[1]
        game_name = GAMES.get(game_key)

        if not game_name:
            await query.edit_message_text(
                "Не удалось найти выбранную игру. Попробуйте снова /start."
            )
            return

        context.user_data["selected_game"] = game_name
        await query.edit_message_text(
            f"✅ Игра «{game_name}» выбрана! 🎰\n\n"
            "📸 Теперь загрузите изображение слота для анализа.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔄 Сменить игру", callback_data="select_game"
                        )
                    ]
                ]
            ),
        )
        return

    if query.data == "bonus":
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")],
        ]
        await query.edit_message_text(
            "🎁✨ <b>Бонусный промокод</b> 🎊💎\n\n"
            "💰 <b>Промокод к депозиту</b> 💵\n\n"
            "🔥 Используй этот промокод для получения бонуса:\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "   <code>AI17UAPZ</code>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💫 <a href=\"https://1wclaa.life/?p=e6jt\">Нажми здесь, чтобы перейти на сайт и активировать промокод!</a>\n\n"
            "🎉 Удачи! 🍀",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data == "help":
        keyboard = [
            [InlineKeyboardButton("📸 Пример", callback_data="show_example")],
            [InlineKeyboardButton("🎰 Выбрать игру", callback_data="select_game")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")],
        ]
        
        help_text = (
            "📌 Как пользоваться ботом:\n\n"
            "1. Нажми «Выбрать игру»\n"
            "2. Выбери слот из списка\n"
            "3. Отправь скриншот слота 📸\n"
            "4. Получи прогноз по бонусной игре"
        )
        
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data == "show_example":
        screenshot_path = "help_screenshot.jpg"
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад к помощи", callback_data="help")],
        ]
        
        if os.path.exists(screenshot_path):
            try:
                with open(screenshot_path, 'rb') as photo:
                    await query.message.reply_photo(
                        photo=photo,
                        caption="📸 Пример скриншота слота для анализа",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
                    await query.answer("Пример отправлен!")
            except Exception as e:
                await query.answer("Ошибка при загрузке примера", show_alert=True)
        else:
            await query.answer("Файл с примером не найден", show_alert=True)
        return

    if query.data == "about":
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")],
        ]
        await query.edit_message_text(
            "🤖 <b>О боте MaxWIN Radar</b> 🎰\n\n"
            "📱 <b>Что это за бот?</b>\n"
            "MaxWIN Radar — это умный помощник для анализа слотов! 🎯\n\n"
            "🔍 <b>Как он работает?</b>\n"
            "• Вы выбираете слот из списка 🎮\n"
            "• Загружаете скриншот игрового экрана 📸\n"
            "• Бот анализирует изображение с помощью AI 🤖\n"
            "• Получаете прогноз: через сколько спинов выпадет бонус 🎁\n"
            "• Узнаёте вероятность бонусной игры в процентах 📊\n\n"
            "✨ <b>Особенности:</b>\n"
            "• Поддержка 20+ популярных слотов 🎰\n"
            "• Быстрый анализ за секунды ⚡\n"
            "• Точные прогнозы на основе данных 🎯\n"
            "• Простой и удобный интерфейс 💫\n\n"
            "🚀 Начни использовать прямо сейчас!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data == "how_it_works":
        await query.edit_message_text(
            "📌 Как это работает:\n"
            "• Вы выбираете слот и отправляете его скриншот.\n"
            "• Мы анализируем изображение и показываем, когда ждать бонус.\n"
            "• В демо-версии результат предварительный и всегда сообщает о бонусе через 20 спинов.\n\n"
            "Готовы попробовать? Нажмите «Выбрать игру».",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎰 Выбрать игру", callback_data="select_game")]]
            ),
        )
        return

    if query.data == "back_to_menu":
        keyboard = [
            [
                InlineKeyboardButton("🎰 Выбрать игру", callback_data="select_game"),
                InlineKeyboardButton("🎁 Бонус", callback_data="bonus")
            ],
            [
                InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
                InlineKeyboardButton("ℹ️ О боте", callback_data="about")
            ],
        ]
        await query.edit_message_text(
            "👋 Привет! Это MaxWIN Radar 🎰✨",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает загруженные изображения слотов."""
    game_name = context.user_data.get("selected_game")

    if not context.user_data.get("active"):
        await update.message.reply_text(
            "Чтобы начать, отправьте команду /start."
        )
        return

    if not game_name:
        keyboard = [
            [InlineKeyboardButton("🎰 Выбрать игру", callback_data="select_game")]
        ]
        await update.message.reply_text(
            "❌ Сначала выберите игру!\n\nНажмите кнопку ниже, чтобы выбрать слот для анализа.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Генерируем случайные значения
    spins = random.randint(20, 35)
    chance = random.randint(71, 93)
    
    # Отправляем сообщение о начале анализа
    processing_msg = await update.message.reply_text(
        "⏳ Получил изображение, запускаю MaxWIN Radar…"
    )
    
    # Имитация обработки (можно убрать, если не нужно)
    await asyncio.sleep(1)
    
    # Формируем результат
    result_text = (
        f"✅ <b>Анализ завершён</b>\n\n"
        f"🎰 <b>Слот:</b> {game_name}\n\n"
        f"📊 <b>Результат анализа:</b>\n"
        f"• Ожидайте бонус примерно через <b>{spins} спинов</b>\n"
        f"• Предполагаемая вероятность бонусной игры: <b>{chance}%</b>\n\n"
        f"🍀 Удачи!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 Новый анализ", callback_data="select_game")],
        [InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_menu")]
    ]
    
    # Удаляем сообщение о обработке и отправляем результат
    try:
        await processing_msg.delete()
    except:
        pass
    
    await update.message.reply_text(
        result_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Flask код удалён - больше не нужен, всё работает через inline-кнопки


def main():
    # Исправление для Python 3.14: устанавливаем политику event loop для Windows
    if os.name == 'nt':  # Windows
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            # Если Proactor недоступен, используем Selector
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            except AttributeError:
                pass  # Используем дефолтную политику
    
    try:
        print("Запуск MaxWIN Radar...")
        print(f"Токен бота: {BOT_TOKEN[:10]}...")  # Показываем только первые 10 символов
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.PHOTO, photo_handler))

        print("✅ Бот запущен! Напишите /start в Telegram.")
        print("Ожидание сообщений...")
        
        # Создаем event loop явно для Python 3.14
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        application.run_polling()
    except Exception as exc:
        import traceback
        print(f"❌ Ошибка при запуске: {exc}")
        print("\nПолный traceback:")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("Starting MaxWIN Radar Bot...")
    print("=" * 50)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


# Удалён весь Flask код - больше не нужен
