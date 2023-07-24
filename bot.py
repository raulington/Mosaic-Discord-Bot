import discord
from discord.ext import commands
import requests
from generate_mosaic import generator
import io
from private import TOKEN
from PIL import Image
import time
import concurrent.futures
from asyncio import ensure_future, sleep

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

valid_themes = ['amongus','berserk', 'chainsawman', 'dragonball', 'food', 'onepunchman', 'spiderman', 'splatoon', 'streetfighter', 'TaylorSwift', 'jojo', 'metroid', 'zelda']

def compress_image(image_bytes, max_size):
    img = Image.open(io.BytesIO(image_bytes))
    while len(image_bytes) > max_size:
        width, height = img.size
        img = img.resize((int(width * 0.9), int(height * 0.9)), Image.Resampling.LANCZOS)
        bytes_io = io.BytesIO()
        img.save(bytes_io, format='PNG')
        image_bytes = bytes_io.getvalue()
        bytes_io.close()
    return image_bytes

async def delayed_message(ctx):
    await sleep(40)
    await ctx.send("Still compressing the image until the image size is below Discord's file sharing limits. Please wait...")

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
    
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as pool:
        start_time = time.time()
        
        # Convert bytes to Image to check size
        img = Image.open(io.BytesIO(output_image_bytes))
        if img.size[0] * img.size[1] > 178956970:  # If total pixels exceeds limit
            await ctx.send("The resulting mosaic is too large to process.")
            return
        
        if len(output_image_bytes) > 8*1024*1024:
            await ctx.send("The resulting mosaic is too large and will need to be compressed due to Discord's file sharing limits. This will reduce the image quality. Please wait.")
        
        # Start delayed_message task
        delayed_message_task = ensure_future(delayed_message(ctx))
        
        output_image_bytes = await bot.loop.run_in_executor(pool, compress_image, output_image_bytes, 8*1024*1024)
        end_time = time.time()
        
        # If delayed_message task has not finished, cancel it
        if not delayed_message_task.done():
            delayed_message_task.cancel()
    
    compression_time = end_time - start_time
    print(f"Time taken to compress image: {compression_time} seconds")
    
    new_img = discord.File(io.BytesIO(output_image_bytes), 'new_image.png')
    await ctx.send(file=new_img)

@bot.command(name='help')
async def custom_help(ctx):
    help_embed = discord.Embed(title="Help for Bot", description="This bot creates a mosaic image based on the provided parameters.", color=0x5865F2)

    help_embed.add_field(name='create_img <renderedTileSize> <tilesAcross> <theme>', value='Creates a mosaic image. <tilesAcross> and <renderedTileSize> describe how many tiles you want across the image and how many pixels each tile size should be. <theme> should be one of the following: ' + ', '.join(valid_themes), inline=False)

    await ctx.send(embed=help_embed)

bot.run(TOKEN)
