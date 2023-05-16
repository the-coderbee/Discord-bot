import asyncio

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from classes.music_player import GookyPlayer, ControlsView
from settings import logging, l_host, l_port, l_pass, BOT_COLOR
from utils import checks

logger = logging.getLogger(__name__)

no_player_msg = f'*```Bot is not in a voice channel. Play something first.```*'  # message sent when player is none


class Music(commands.Cog):
    _player: GookyPlayer = None
    _music_cmd_channel: discord.TextChannel = None

    def __init__(self, bot):
        self.bot = bot

    async def setup(self):
        node: wavelink.Node = wavelink.Node(id='yt_music_node', uri=f'{l_host}:{l_port}', password=l_pass, retries=5)
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f'(NODE - {node.id}) ........... IS READY')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload):
        await self._display_song_embed(payload)
        await self._controls()
        if len(self._player.history) > 0 and self._player.history[-1] == payload.track:
            return
        self._player.history.append(payload.track)
        if len(self._player.history) > 30:
            self._player.history.pop(0)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        await self._music_cmd_channel.send(f'*```{payload.track.title} by {payload.track.author} ended```*')
        if self._player.queue.is_empty:
            await asyncio.sleep(8)
            if self._player.is_playing():
                return
            if len(self._player.channel.members) < 2:
                time = 1
            else:
                time = 300
            await asyncio.sleep(time)
            if self._player.is_playing():
                return
            self._player.cleanup()
            await self._player.disconnect()
            self._player = None

    async def _display_song_embed(self, payload: wavelink.TrackEventPayload):
        song_details = f"**{payload.track.title}** by *{payload.track.author}*"
        song_length = payload.track.length // 1000
        thumbnail_url = await wavelink.YouTubeTrack.fetch_thumbnail(payload.track)
        emb = discord.Embed(title="Playing ..\t\t\t\t♫♫", color=BOT_COLOR)
        emb.set_thumbnail(url=self.bot.user.avatar.url)
        emb.add_field(name="", value=song_details)
        emb.set_image(url=thumbnail_url)
        emb.add_field(name="", value=f"`{song_length // 60}m {song_length % 60}s`")
        await self._music_cmd_channel.send(embed=emb)

    async def _connect(self, channel):
        self._player = await channel.connect(cls=GookyPlayer, self_deaf=True, self_mute=False)
        self._player.queue.loop = False
        await self._player.set_volume(75)

    async def _add(self, query):
        if self._player is not None:
            try:
                track = await wavelink.YouTubeTrack.search(
                    query, return_first=True, node=self._player.current_node)
            except wavelink.NoTracksError:
                track = await wavelink.YouTubeTrack.search(
                    query, return_first=True, node=self._player.current_node)
            except ValueError:
                track = await wavelink.YouTubeTrack.search(
                    query, return_first=True, node=self._player.current_node)
            except wavelink.InvalidLavalinkResponse:
                await self._music_cmd_channel.send('*```Server Busy. Playing after 10s```*')
                await asyncio.sleep(8)
                track = await wavelink.YouTubeTrack.search(
                    query, return_first=True, node=self._player.current_node)
            self._last_added_track = track
            await self._player.queue.put_wait(track)
        else:
            return

    async def _controls(self):
        view = ControlsView(timeout=None)
        view.player = self._player
        await self._music_cmd_channel.send(f'Controls', view=view)

    # Player commands
    @commands.hybrid_command(name='autoplay', description='Set autoplay of music player')
    @checks.is_music_channel()
    async def set_autoplay(self, ctx, value: bool):
        if not self._player:
            return await ctx.send(no_player_msg)
        if self._player.autoplay == value:
            return await ctx.send(f'*```Autoplay is already set to {value}```*')
        self._player.autoplay = value
        await ctx.send(f'*```Autoplay: Set to {value}```*')

    @commands.hybrid_command(name='loop', description='Turn loop on or off for current song ')
    @checks.is_music_channel()
    async def loop_song(self, ctx, value: bool):
        if not self._player:
            return await ctx.send(no_player_msg)
        if self._player.queue.loop == value:
            return await ctx.send(f'*```Loop is already set to {value}```*')
        self._player.queue.loop = value
        await ctx.send(f'*```Loop: Set to {value}```*')

    @commands.hybrid_command(name='play', description='Play song from youtube')
    @app_commands.describe(song='The song you wish to play', channel='The channel in which you wish to play the song')
    @checks.is_music_channel()
    async def play(self, ctx, song: str,
                   channel: discord.VoiceChannel | discord.StageChannel = None):
        self._music_cmd_channel = ctx.channel
        # connect to a voice channel
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            return await ctx.send(f'*```Either provide a voice channel or join one first.```*')
        if self._player is None:
            try:
                await self._connect(channel)
            except asyncio.TimeoutError:
                return await ctx.send(f'*```Unable to connect. Try again.```*')
        if self._player and self._player.channel != channel:
            await self._voice_client.move_to(channel)
            await ctx.send(f'*```Moved to {channel}```*')
        if self._player.is_playing() or self._player.is_paused():
            await ctx.send(f'*```♫♫ searching ....```*')
        else:
            msg = await ctx.send(f'*```♫♫\t Enjoy your music```*')
        # add song
        try:
            await self._add(song)
        except discord.NotFound:
            return await ctx.send(f'*```Oops! Song not found. Try playing the song again```*')
        except AttributeError:
            return await ctx.send(f'*```Command error!! Try again.```*')
        except wavelink.NoTracksError:
            return await ctx.send(f'*```Track not found! Try again.```*')

        # check if player is playing
        if self._player.is_playing():
            return await ctx.send(f'*```{self._last_added_track.title} by {self._last_added_track.author} has been '
                                  f'added to queue.```*')
        elif self._player.is_paused():
            # if queue empty
            if not self._player.queue.is_empty:
                return await ctx.send(f'*```{self._last_added_track.title} by {self._last_added_track.author} has been '
                                      f'added to queue.```*')
        self._player.current_track = await self._player.queue.get_wait()
        await self._player.play(self._player.current_track)

    @commands.hybrid_command(name='next', description='Play next song')
    @checks.is_music_channel()
    async def skip(self, ctx):
        if not self._player:
            return await ctx.send(no_player_msg)
        if self._player.queue.loop:
            self._player.queue.loop = False
            await ctx.send(f'*```Not looping anymore```*')
        try:
            self._player.current_track = self._player.queue.get()
        except wavelink.QueueEmpty:
            return await ctx.send(f'*```Queue is empty```*')
        await self._player.play(self._player.current_track)
        await ctx.send(f'*```Skipped track```*')

    @commands.hybrid_command(name='pause', description='Pause track')
    @checks.is_music_channel()
    async def pause(self, ctx):
        if not self._player:
            return await ctx.send(no_player_msg)
        await self._player.pause()
        await ctx.send(f'*```Paused```*')

    @commands.hybrid_command(name='resume', description='Resume track')
    @checks.is_music_channel()
    async def resume(self, ctx):
        if not self._player:
            return await ctx.send(no_player_msg)
        await self._player.resume()
        await ctx.send(f'*```Resumed```*')

    @commands.hybrid_command(name='ff', description='Seek ahead')
    @app_commands.describe(seconds='Amount of seconds you wish to seek')
    @checks.is_music_channel()
    async def seek_forward(self, ctx, seconds: int = 10):
        if not self._player:
            return await ctx.send(no_player_msg)
        new_pos = int(self._player.position + seconds * 1000)
        await self._player.seek(new_pos)
        await ctx.send(f'**```+{seconds}s```**')

    @commands.hybrid_command(name='bb', description='Seek back')
    @app_commands.describe(seconds='Amount of seconds you wish to seek')
    @checks.is_music_channel()
    async def seek_backward(self, ctx, seconds: int = 10):
        if not self._player:
            return await ctx.send(no_player_msg)
        new_pos = int(self._player.position - seconds * 1000)
        await self._player.seek(new_pos)
        await ctx.send(f'**```-{seconds}s```**')

    @commands.hybrid_command(name='volume', description='Set volume of music player')
    @checks.is_music_channel()
    async def set_vol(self, ctx, volume: int):
        if volume < 0:
            volume = 0
        if volume > 1000:
            volume = 1000
        if not self._player:
            return await ctx.send(no_player_msg)
        await self._player.set_volume(volume)
        await ctx.send(f'*```Volume: Set to {volume}```*')

    @commands.hybrid_command(name='stop', desription='Stop track')
    @checks.is_music_channel()
    async def stop(self, ctx):
        if not self._player:
            return await ctx.send(no_player_msg)
        if not self._player.is_playing():
            return await ctx.send(f'*```No song is playing```*')
        if self._player.queue.loop:
            self._player.queue.loop = False
        await self._player.stop()
        await ctx.send(f'*```Stopped```*')

    @commands.hybrid_command(name='leave', description='Leave the channel the bot is connected to')
    @checks.is_music_channel()
    async def disconnect(self, ctx):
        if not self._player:
            return await ctx.send(no_player_msg)
        channel = self._player.channel
        self._player.cleanup()
        await self._player.disconnect()
        await ctx.send(f'*```Left {channel}```*')

    @commands.hybrid_command(name='history', description='Show (temporary) history of songs played in the music player')
    @app_commands.describe(number='Number of tracks to show in history (max 15)')
    @checks.is_music_channel()
    async def fetch_history(self, ctx, number: int = 10):
        if not self._player:
            return await ctx.send(no_player_msg)
        if number > 15:
            number = 15
            await ctx.send(f'*```Cannot fetch more than 15 track history.```*')
        emb = discord.Embed(title="Song History", color=BOT_COLOR)
        emb.set_thumbnail(url=self.bot.user.avatar.url)
        track: wavelink.Playable
        output = "```"
        for index, track in enumerate(reversed(self._player.history)):
            song_det = f'{index + 1}. {track.title} by {track.author}'
            song_len = f'{(track.length // 1000) // 60}m {(track.length // 1000) % 60}s'
            output += f"{song_det:30} -- {song_len}\n"
        output += "```"
        emb.add_field(name="Tracks", value=output, inline=False)
        await ctx.send(f'Song history for last {number} songs', embed=emb)


async def setup(bot):
    music_bot = Music(bot)
    await bot.add_cog(music_bot)
    await music_bot.setup()
