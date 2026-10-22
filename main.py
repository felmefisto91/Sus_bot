import logging

import discord
from discord.ext import commands

import config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("AllianceSiegeBot")


class AllianceSiegeBot(commands.Bot):
    """A narrowly scoped bot that owns only the Alliance Siege workflow."""

    def __init__(self):
        # Slash commands and component interactions do not require Message Content
        # or Server Members privileged intents.
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        logger.info("Завантаження Alliance Siege модуля...")
        await self.load_extension("cogs.alliance_siege")

        logger.info("Синхронізація дерева команд (tree.sync)...")
        synced_commands = await self.tree.sync()
        logger.info("✅ Синхронізовано команд: %s", len(synced_commands))

    async def on_ready(self):
        logger.info("Авторизовано як %s (ID: %s)", self.user, self.user.id)


def main() -> None:
    try:
        config.validate_configuration()
    except ValueError as error:
        logger.critical("❌ Помилка конфігурації: %s", error)
        return

    AllianceSiegeBot().run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
