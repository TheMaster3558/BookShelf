from .logs import Logs


async def setup(bot) -> None:
    await bot.add_cog(Logs(bot))
