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
1. Создайте `.env` в корне проекта:
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
3. Запустите из корня репозитория:
   ```bash
   python main.py
   ```

## Структура проекта
- `main.py` — корневая точка входа (запуск приложения).
- `bot/` — пакет Telegram-бота (handlers, keyboards, middleware, внутренняя точка входа `bot.main`).
- `database/` — модели и CRUD.
- `wireguard/` — генерация WireGuard-конфигов и manager.
- `integrations/` — слой внешних интеграций (пока заглушки для платежей и WireGuard API).
- `scripts/` — запуск/деплой/бэкапы.

### Почему `main.py` был внутри `bot/`
`bot/` — это Python-пакет с кодом приложения, поэтому `bot/main.py` удобно использовать как модульную точку входа (`python -m bot.main`).

Чтобы не путаться с запуском из разных директорий, добавлена корневая точка входа `main.py`.
Теперь рекомендованный способ — всегда запускать из корня:

```bash
python main.py
```

## Заглушки под API
В `integrations/` добавлены временные заглушки:
- `integrations/payments/provider.py` — `StubPaymentProvider`.
- `integrations/wireguard/api.py` — `StubWireGuardApiClient`.

Это позволяет спокойно развивать архитектуру (handlers/services), а позже заменить заглушки на реальные API-клиенты без перестройки всего проекта.

## Важно
Платежный модуль сейчас в режиме MVP (ручное подтверждение/заглушки).
Перед релизом добавьте реального платежного провайдера, webhook-валидацию и полноценные API-интеграции.
- `scripts/` — запуск/деплой/бэкапы

## Важно
Это production-ready каркас, но платежный модуль сейчас в режиме MVP (ручное подтверждение `paid`).
Перед релизом добавьте реального платежного провайдера и webhook-валидацию.

