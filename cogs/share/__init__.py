from .share import Share


async def setup(bot) -> None:
    await bot.add_cog(Share(bot))
