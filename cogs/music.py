import discord
import logging
import time
from discord.ext import commands
from discord import FFmpegPCMAudio
from downloader import Downloader
from yt_dlp import DownloadError

class MusicPlayer(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queue = []

    def queue_player(self, player: FFmpegPCMAudio):
        self.queue.append(player)

    def continue_p(self, ctx):
        while len(self.queue) > 1:     
            if not ctx.voice_client.is_playing(): 
                del self.queue[0]
                ctx.voice_client.play(self.queue[0])
            
            time.sleep(1)


    @commands.command()
    async def play(self, ctx, url: str):
        
        if ctx.message.author.voice:
            await self.join(ctx)
            
            dl = Downloader(url)
            
            try: 
                info = dl.get_info()
                dl.download()
            except DownloadError as err:
                await ctx.send('Failed to download audio!')

            title = info[0]
            source = FFmpegPCMAudio(f'./music/{title}')

            if ctx.voice_client.is_playing():
                self.queue_player(source)
                embed = dl.create_embed('Queued', info)
                await ctx.send(embed=embed)
            else:
                self.queue_player(source)
                ctx.voice_client.play(source, after=lambda x: self.continue_p(ctx))
                embed = dl.create_embed(f'Now playing: {title}', info)
                await ctx.send(embed=embed)

        else:
            await ctx.send('you must be in a voice channel to use this command!')

    @commands.command()
    async def join(self, ctx):
        voice_clients = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice_clients is None:
            channel = ctx.message.author.voice.channel
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.message.author.voice:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                await ctx.voice_client.disconnect()
            else:
                await ctx.voice_client.disconnect()
        else:
            await ctx.send('You must be in a voice channel to use this command!')

    @commands.command()
    async def skip(self, ctx):
        if ctx.message.author.voice:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                
                if len(self.queue) > 1:
                    del self.queue[0]
                
                ctx.voice_client.play(self.queue[0], after=lambda x: self.continue_p(ctx))

                await ctx.send('Skipped!')
            else:
                await ctx.send('Nothing is playing in this channel')
        else:
            await ctx.send('You must be in a voice channel to use this command!')

    @commands.command()
    async def pause(self, ctx):
        if ctx.message.author.voice:
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                await ctx.send('Paused!')
            else:
                await ctx.send('Nothing is playing in this channel!')
        else:
            await ctx.send('You must be in a voice channel to use this command!')

    @commands.command()
    async def resume(self, ctx):
        if ctx.message.author.voice:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                await ctx.send('Resuming...')
            else:
                await ctx.send('Nothing is paused.')
        else:
            await ctx.send('You must be in a voice channel to use this command')

    # Halts all audio players and clears the queue
    @commands.command()
    async def stop(self, ctx):
        if ctx.message.author.voice:
            if ctx.voice_client.is_playing():
                self.queue.clear()
                ctx.voice_client.stop()
                await ctx.send('Stopped!')
                await ctx.send('Queue cleared!')
            else:
                await ctx.send('Nothing is currently playing!')
        else:
            await ctx.send('You must be in a voice channel to use this command!')


async def setup(client):
    await client.add_cog(MusicPlayer(client))
