from .dbooks import DBooks


async def setup(bot):
    await bot.add_cog(DBooks(bot))
