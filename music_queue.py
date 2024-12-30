import discord
import logging
import time
import asyncio
import os

from discord.ext import commands
from discord import FFmpegPCMAudio, Embed, Color, ClientException, PCMVolumeTransformer

"""
Wrapper class for PCMVolumeTransformer objects
allows you to easily retrive information about a song currently in queue.
"""
class QueueItem:

    def __init__(self, info:tuple, audio:PCMVolumeTransformer):
        self.info = info
        self.audio = audio

    def __repr__(self):
        title = self.info[1]
        return title

    async def send_embed(self, ctx, info,  embed_title):
        # video info from yt_dlp
        video_id, title, duration, thumbnail, author = info

        em = Embed(title=embed_title, color=Color.random())
        em.set_thumbnail(url=thumbnail)
        em.add_field(name='Song', value=title, inline=False)
        em.add_field(name='Channel', value=author, inline=False)
        em.add_field(name='Duration', value=duration, inline=False)
        await ctx.send(embed=em)

"""
The actual queue data structure itself
resume() is called internally by MusicPlayer.play() after the inital audio file has finished playing.
"""
class MusicQueue:

    def __init__(self):
        self.items = []
        self.is_looping = False

    def __repr__(self):
        return f'{[x for x in self.items]}'

    def push(self, item:QueueItem):
        self.items.append(item)
        logging.info(f'Queue: {self.items}') # for debugging purposes (just the titles of the videos)

    def pop(self):
        self.items.pop(0)
        logging.info(f'Queue: {self.items}')


    def clear(self):
        self.items.clear()

    # Loop through the rest of the songs in queue
    async def resume(self, ctx, vc):
        while len(self.items) != 0:
            if not vc.is_playing() and not vc.is_paused():
                try:
                    vc.play(self.items[0].audio, after=lambda x: self.pop())
                except ClientException:
                    await ctx.send('An error occured while playing audio')

            await asyncio.sleep(1)

    async def loop(self, ctx, vc):
        self.is_looping = True
        while is_looping is True:
            if not vc.is_playing() and not vc.is_paused():
                try:
                    vc.play(self.items[0].audio)
                except ClientException:
                    await ctx.send('An error has occured while playing audio')
