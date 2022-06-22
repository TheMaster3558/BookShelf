from .command import CustomCommand
from .customcommands import CustomCommands


async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
