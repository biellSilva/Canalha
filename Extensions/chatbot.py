import openai
import discord
import config

from discord.ext import commands
from discord.ext.commands import Context
from os import getenv
from asyncio import TimeoutError

openai.api_key = "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"


async def get_davinci_response(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text.strip()
    return message


async def get_chatgpt_response(message_log):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=message_log,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    for choice in response.choices:
        if "text" in choice:
            return choice.text

    return response.choices[0].message.content


class ChatGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(name='chatgpt')
    async def chat_chatgpt(self, ctx: Context):
        '''ChatGPT 3.5 model'''

        message_log = [
            {"role": "system", "content": f"using {ctx.guild.preferred_locale}, say hi and inform the user to type exit when is finished, {ctx.author.display_name} is the user username u need keep the original username letter case"}
        ]

        response = await get_chatgpt_response(message_log)
        message_log.append({"role": "assistant", "content": response})

        em = discord.Embed(color=config.cinza,
                           description=response)
        em.set_footer(text=f'{ctx.author.display_name} - {ctx.author.id}', icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=em)

        def check(message: discord.Message):
            return message.author == ctx.author and message.channel == ctx.channel

        while True:
                try:
                    message: discord.Message = await self.bot.wait_for('message', check=check, timeout=90)
                except TimeoutError:
                    em.description='Timed out'
                    await ctx.send(embed=em)
                    return
                
                if message.content.lower() == 'exit':
                    message_log.append({"role": "system", "content": "say goodbye to the user using the previous message language"})
                    response = await get_chatgpt_response(message_log)
                    message_log.append({"role": "assistant", "content": response})
                    em.description = response
                    return await message.reply(embed=em)
                    
                message_log.append({"role": "user", "content": message.content})
                response = await get_chatgpt_response(message_log)
                message_log.append({"role": "assistant", "content": response})
                em.description=response
                await message.reply(embed=em)

        
    @commands.hybrid_group(name='davinci')
    async def chat_davinci(self, ctx: Context):
        '''Text Davinci model'''

        await ctx.reply('iniciado')

        def check(message: discord.Message):
            return message.author == ctx.author and message.channel == ctx.channel

        while True:
            try:
                message: discord.Message = await self.bot.wait_for('message', check=check, timeout=90)

            except TimeoutError:
                await ctx.reply('o tempo de espera acabou')
                return

            if message.content.lower() == 'exit':
                break

            response = await get_davinci_response(message.content)
            await message.reply(response)

        return await ctx.reply('adeus')

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))
