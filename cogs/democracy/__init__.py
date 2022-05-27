from .democracy import Democracy


async def setup(bot):
    await bot.add_cog(Democracy(bot))
