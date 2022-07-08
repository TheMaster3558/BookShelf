from .tree_sync import TreeSync


async def setup(bot):
    await bot.add_cog(TreeSync(bot))
