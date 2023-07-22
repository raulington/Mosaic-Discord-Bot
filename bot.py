import discord
from discord.ext import commands
import requests
from generate_mosaic import generator
import io
from private import TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

valid_themes = ['amongus','berserk', 'chainsawman', 'dragonball', 'food', 'onepunchman', 'spiderman', 'splatoon', 'streetfighter', 'TaylorSwift', 'jojo', 'metroid', 'zelda']

@bot.command(name='create_img')
async def create_img(ctx, renderedTileSize: int, tilesAcross: int, theme: str):
    if theme not in valid_themes:
        await ctx.send('Invalid theme. Please use one of the following: ' + ', '.join(valid_themes))
        return

    if not ctx.message.attachments:
        await ctx.send('Please attach an image.')
        return

    image_url = ctx.message.attachments[0].url
    image_bytes = requests.get(image_url).content

    output_image_bytes = generator(renderedTileSize, tilesAcross, theme, io.BytesIO(image_bytes))
    new_img = discord.File(io.BytesIO(output_image_bytes), 'new_image.png')
    print('Finished Mosaic')
    await ctx.send(file=new_img)

bot.run(TOKEN)
