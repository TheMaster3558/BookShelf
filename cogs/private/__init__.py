from discord.ext import commands


extensions = (
    'tree_sync',
    'backup',
    'errors',
    'help'
)


async def setup(bot) -> None:
    for extension in extensions:
        try:
            await bot.load_extension(f'cogs.private.{extension}')
        except commands.ExtensionAlreadyLoaded:
            pass


async def teardown(bot) -> None:
    for extension in extensions:
        try:
            await bot.unload_extension(f'cogs.private.{extension}')
        except commands.ExtensionNotLoaded:
            pass
