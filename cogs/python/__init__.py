from .python import Python


async def setup(bot):
    await bot.add_cog(Python(bot))
