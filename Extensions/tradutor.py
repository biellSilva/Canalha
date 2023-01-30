import discord
import config

from googletrans import Translator
from flag import dflagize
from countryinfo import CountryInfo
from discord.ext import commands


class Tradutor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):

        if user.bot:
            return

        if reaction.message.author.bot:
            return

        if reaction.message.content == None or reaction.message.content == '':
            return

        for react in reaction.message.reactions:
            if react.emoji == reaction.emoji and react.count > 1:
                return

        
        translator = Translator()
        try:
            flag:str = dflagize(reaction.emoji)
            idioma = CountryInfo(flag.replace(':','')).languages()[0]

            try:
                traduzido = translator.translate(reaction.message.content, idioma)

                em = discord.Embed(color=config.amarelo,
                                description=f'''
                                            **{traduzido.dest}:**
                                            {traduzido.text}''')

                em.set_author(name=user, icon_url=user.display_avatar.url)

                await reaction.message.add_reaction(reaction.emoji)
                await reaction.message.channel.send(embed=em)
                return

            except:
                return
        except:
            return


async def setup(bot):
    await bot.add_cog(Tradutor(bot))
