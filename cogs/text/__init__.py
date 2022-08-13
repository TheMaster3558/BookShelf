from .text import Text


async def setup(bot):
    await bot.add_cog(Text(bot))
