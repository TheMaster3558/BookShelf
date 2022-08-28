from .roles import Roles


async def setup(bot) -> None:
    await bot.add_cog(Roles(bot))
