# WireGuard VPN Telegram Bot

Готовая базовая структура для продажи VPN-подписок через Telegram и WireGuard Easy API.

## Возможности
- Регистрация пользователя в Telegram-боте.
- Покупка/активация подписки.
- Генерация WireGuard-конфига и выдача `.conf` файлом.
- Простая админ-панель (`/admin`) со статистикой.

## Стек
- `aiogram` (бот)
- `SQLAlchemy` + `SQLite` (хранилище)
- `aiohttp` (интеграция с WireGuard Easy API)

## Быстрый старт
1. Создайте `.env`:
   ```env
   BOT_TOKEN=...
   ADMIN_IDS=[123456789]
   DATABASE_URL=sqlite+aiosqlite:///./vpn_bot.db

   WIREGUARD_API_URL=https://your-wg-easy-domain
   WIREGUARD_API_TOKEN=your_api_token
   WIREGUARD_SERVER_PUBLIC_KEY=server_public_key
   WIREGUARD_SERVER_ENDPOINT=1.2.3.4:51820
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите:
   ```bash
   python -m bot.main
   ```

## Структура
- `bot/` — Telegram bot (handlers, keyboards, middleware)
- `database/` — модели и CRUD
- `wireguard/` — интеграция с WireGuard Easy + генератор конфигов
- `scripts/` — запуск/деплой/бэкапы

## Важно
Это production-ready каркас, но платежный модуль сейчас в режиме MVP (ручное подтверждение `paid`).
Перед релизом добавьте реального платежного провайдера и webhook-валидацию.
