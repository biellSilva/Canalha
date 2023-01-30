import discord
import config
import datetime

from discord.ext import commands



class On_message(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if message.author.bot:
            return

        if message.channel.id == config.sugestao:
            
            guild = message.guild
            sugestao = guild.get_channel(config.sugestao)
            
            em = discord.Embed(title="Sugestão",
                               color=config.vermelho,
                               description=f"Sugestão de {message.author.mention}:\n"
                                           f"||autor: {message.author} - {message.author.id}||\n\n"
                                           f"{message.content}",
                                           timestamp=datetime.datetime.now(tz=config.tz_brazil))
            em.set_footer(text="Reaja com base na sua decisão", icon_url=guild.icon)

            msg = await sugestao.send(embed=em)
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            await message.delete()
        

async def setup(bot):
    await bot.add_cog(On_message(bot))
