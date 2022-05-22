from .share import Share


async def setup(bot):
    await bot.add_cog(Share(bot))
