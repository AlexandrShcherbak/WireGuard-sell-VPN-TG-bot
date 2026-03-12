# WireGuard VPN Telegram Bot

Готовая базовая структура для продажи VPN-подписок через Telegram и WireGuard Easy API.

## Возможности
- Регистрация пользователя в Telegram-боте.
- Покупка/активация подписки.
- Генерация WireGuard-конфига по шаблону и выдача `.conf` + QR-кода.
- Оплата через Crypto Bot и рублёвый донат-сервис.
- Команда `/howto` с краткой инструкцией по подключению.
- Webhook-интеграции для Crypto Bot / донатов / Sendler.
- Простая админ-панель (`/admin`) со статистикой.

## Стек
- `aiogram` (бот)
- `SQLAlchemy` + `SQLite` (хранилище)
- `aiohttp` (интеграция с WireGuard Easy API)

## Быстрый старт
1. Создайте `.env` в корне проекта:
   ```env
   BOT_TOKEN=...
   # Можно указать одного админа:
   ADMIN_ID=123456789
   # или список:
   ADMIN_IDS=[123456789]
   DATABASE_URL=sqlite+aiosqlite:///./vpn_bot.db

   WIREGUARD_API_URL=https://your-wg-easy-domain
   WIREGUARD_API_TOKEN=your_api_token
   WIREGUARD_SERVER_PUBLIC_KEY=server_public_key
   WIREGUARD_SERVER_ENDPOINT=1.2.3.4:51820

   SUPPORT_CONTACT=@your_support_username

   # Платежи
   CRYPTOBOT_TOKEN=...
   DONATION_BASE_URL=https://www.donationalerts.com/r/your_page

   # Webhook сервер (для callback от Sendler/донатов/CryptoBot)
   SENDLER_WEBHOOK_ENABLED=true
   SENDLER_WEBHOOK_HOST=0.0.0.0
   SENDLER_WEBHOOK_PORT=8080
   SENDLER_WEBHOOK_SECRET=super-secret
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите из корня репозитория:
   ```bash
   python main.py
   ```


### Почему `main.py` не читает `.env` напрямую
`main.py` только запускает приложение (`asyncio.run(main())`). Настройки читаются внутри модулей через `config.settings`/`config.config`, например в `bot/bot_instance.py` и `bot/handlers/*`. Это нормальная схема: точка входа минимальная, а конфигурация загружается там, где используется.

Поддерживаются оба файла переменных: `.env` и `env` в корне проекта. Загрузка выполняется встроенным парсером (`KEY=VALUE`) и не требует `python-dotenv`.

> Важно: переменные `WG_CONFIG_PATH` и `WG_INTERFACE` в текущей версии кода не используются — интеграция построена через `WIREGUARD_API_*` и параметры сервера (`WIREGUARD_SERVER_*`).

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

## Webhook endpoints
- `POST /webhooks/cryptobot` — успешные события оплаты Crypto Bot.
- `POST /webhooks/donation` — подтверждение рублёвой оплаты от донат-сервиса.
- `POST /webhooks/sendler` — лиды/события из Sendler.

## Важно
- Для безопасности включайте `SENDLER_WEBHOOK_SECRET` и проверяйте секрет в webhook-запросах.
- Для донат-сервисов статус обычно подтверждается только webhook'ом.
