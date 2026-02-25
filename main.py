import asyncio

from bot.main import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        # Graceful shutdown on Ctrl+C without traceback noise.
        pass
