import os
import asyncio
import re
import tempfile
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Keep-alive для Replit (предотвращает "засыпание" бота)
try:
    from keep_alive import keep_alive
    keep_alive()
    print("✅ Keep-alive сервер запущен (Replit)")
except ImportError:
    pass  # Если keep_alive.py нет, просто пропускаем

BOT_TOKEN = os.getenv("BOT_TOKEN", "8239304307:AAGxvv1cI82eYE-mHIAFtts-QkO8-tQj2-M")

# Папка для временных файлов
TEMP_DIR = Path("temp_downloads")
TEMP_DIR.mkdir(exist_ok=True)

# Максимальный размер файла для Telegram (50MB для видео)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def is_youtube_url(url: str) -> bool:
    """Проверяет, является ли ссылка ссылкой на YouTube."""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/',
    ]
    return any(re.search(pattern, url) for pattern in youtube_patterns)


def extract_video_id(url: str) -> str:
    """Извлекает ID видео из URL."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


async def download_video(url: str, quality: str = "best", audio_only: bool = False) -> tuple[str, dict]:
    """
    Скачивает видео с YouTube используя yt-dlp.
    
    Args:
        url: Ссылка на YouTube видео
        quality: Качество видео (best, worst, или формат типа 720p)
        audio_only: Если True, скачивает только аудио
    
    Returns:
        tuple: (путь к файлу, информация о видео)
    """
    import yt_dlp
    
    # Настройки для yt-dlp
    ydl_opts = {
        'outtmpl': str(TEMP_DIR / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    
    if audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        if quality == "best":
            ydl_opts['format'] = 'best[filesize<50M]/best'
        elif quality == "worst":
            ydl_opts['format'] = 'worst'
        else:
            # Попытка найти формат с указанным качеством
            ydl_opts['format'] = f'best[height<={quality}][filesize<50M]/best[filesize<50M]'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            duration = info.get('duration', 0)
            filesize = info.get('filesize') or info.get('filesize_approx', 0)
            
            # Проверяем размер файла
            if filesize > MAX_FILE_SIZE and not audio_only:
                # Пробуем скачать в более низком качестве
                ydl_opts['format'] = 'best[height<=720][filesize<50M]/best[filesize<50M]'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    info = ydl2.extract_info(url, download=True)
            else:
                ydl.download([url])
            
            # Находим скачанный файл
            downloaded_file = None
            for file in TEMP_DIR.iterdir():
                if file.is_file():
                    downloaded_file = file
                    break
            
            if not downloaded_file:
                raise Exception("Файл не был скачан")
            
            video_info = {
                'title': video_title,
                'duration': duration,
                'filesize': downloaded_file.stat().st_size,
                'filename': downloaded_file.name,
            }
            
            return str(downloaded_file), video_info
            
    except Exception as e:
        raise Exception(f"Ошибка при скачивании: {str(e)}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start – приветствие и инструкция."""
    welcome_text = (
        "👋 <b>Привет! Я бот для скачивания YouTube видео</b> 📥\n\n"
        "📌 <b>Как использовать:</b>\n"
        "1. Отправьте мне ссылку на YouTube видео\n"
        "2. Выберите формат (видео или аудио)\n"
        "3. Получите скачанное видео/аудио\n\n"
        "✨ <b>Поддерживаемые форматы:</b>\n"
        "• Обычные видео (youtube.com/watch?v=...)\n"
        "• Короткие видео (youtube.com/shorts/...)\n"
        "• Ссылки youtu.be\n\n"
        "🚀 Просто отправьте ссылку на видео!"
    )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help – справка."""
    help_text = (
        "📖 <b>Справка по использованию бота</b>\n\n"
        "🔗 <b>Отправка ссылки:</b>\n"
        "Просто отправьте ссылку на YouTube видео в чат.\n\n"
        "📥 <b>Форматы скачивания:</b>\n"
        "• <b>Видео</b> - скачивает видео с лучшим качеством (до 50MB)\n"
        "• <b>Аудио</b> - скачивает только звук в формате MP3\n\n"
        "⚙️ <b>Команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "⚠️ <b>Ограничения:</b>\n"
        "• Максимальный размер файла: 50MB\n"
        "• Для больших видео будет предложено более низкое качество\n"
        "• Некоторые видео могут быть недоступны для скачивания"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode="HTML"
    )


async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ссылки на YouTube видео."""
    url = update.message.text.strip()
    
    if not is_youtube_url(url):
        await update.message.reply_text(
            "❌ Это не похоже на ссылку YouTube.\n\n"
            "Пожалуйста, отправьте корректную ссылку на YouTube видео.\n"
            "Например: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        return
    
    # Сохраняем URL в контексте пользователя
    context.user_data["youtube_url"] = url
    
    # Показываем меню выбора формата
    keyboard = [
        [
            InlineKeyboardButton("📹 Видео", callback_data="format_video"),
            InlineKeyboardButton("🎵 Аудио (MP3)", callback_data="format_audio")
        ]
    ]
    
    await update.message.reply_text(
        "✅ Ссылка распознана!\n\n"
        "📥 Выберите формат скачивания:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки."""
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get("youtube_url")
    
    if not url:
        await query.edit_message_text(
            "❌ Ссылка не найдена. Пожалуйста, отправьте ссылку на YouTube видео."
        )
        return
    
    if query.data == "format_video":
        await query.edit_message_text("⏳ Начинаю скачивание видео...")
        
        try:
            file_path, video_info = await asyncio.to_thread(download_video, url, quality="best", audio_only=False)
            
            # Форматируем размер файла
            file_size_mb = video_info['filesize'] / (1024 * 1024)
            duration_min = video_info['duration'] // 60
            duration_sec = video_info['duration'] % 60
            
            caption = (
                f"📹 <b>{video_info['title']}</b>\n\n"
                f"📊 Размер: {file_size_mb:.2f} MB\n"
                f"⏱ Длительность: {duration_min}:{duration_sec:02d}"
            )
            
            # Отправляем видео
            with open(file_path, 'rb') as video_file:
                await query.message.reply_video(
                    video=video_file,
                    caption=caption,
                    parse_mode="HTML"
                )
            
            # Удаляем временный файл
            try:
                os.remove(file_path)
            except:
                pass
            
            await query.edit_message_text("✅ Видео успешно скачано и отправлено!")
            
        except Exception as e:
            error_msg = str(e)
            if "filesize" in error_msg.lower() or "50" in error_msg:
                await query.edit_message_text(
                    "❌ Видео слишком большое (больше 50MB).\n\n"
                    "Попробуйте скачать только аудио или выберите видео меньшей длительности."
                )
            else:
                await query.edit_message_text(
                    f"❌ Ошибка при скачивании видео:\n{error_msg}\n\n"
                    "Попробуйте еще раз или выберите другой формат."
                )
    
    elif query.data == "format_audio":
        await query.edit_message_text("⏳ Начинаю скачивание аудио...")
        
        try:
            file_path, video_info = await asyncio.to_thread(download_video, url, audio_only=True)
            
            # Форматируем размер файла
            file_size_mb = video_info['filesize'] / (1024 * 1024)
            duration_min = video_info['duration'] // 60
            duration_sec = video_info['duration'] % 60
            
            caption = (
                f"🎵 <b>{video_info['title']}</b>\n\n"
                f"📊 Размер: {file_size_mb:.2f} MB\n"
                f"⏱ Длительность: {duration_min}:{duration_sec:02d}"
            )
            
            # Отправляем аудио
            with open(file_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=caption,
                    parse_mode="HTML",
                    title=video_info['title']
                )
            
            # Удаляем временный файл
            try:
                os.remove(file_path)
            except:
                pass
            
            await query.edit_message_text("✅ Аудио успешно скачано и отправлено!")
            
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка при скачивании аудио:\n{str(e)}\n\n"
                "Попробуйте еще раз."
            )


def main():
    # Исправление для Python 3.14: устанавливаем политику event loop для Windows
    if os.name == 'nt':  # Windows
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            except AttributeError:
                pass
    
    try:
        print("Запуск YouTube Downloader Bot...")
        print(f"Токен бота: {BOT_TOKEN[:10]}...")
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, url_handler))
        
        print("✅ Бот запущен! Напишите /start в Telegram.")
        print("Ожидание сообщений...")
        
        application.run_polling()
        
    except Exception as exc:
        import traceback
        print(f"❌ Ошибка при запуске: {exc}")
        print("\nПолный traceback:")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("Starting YouTube Downloader Bot...")
    print("=" * 50)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
