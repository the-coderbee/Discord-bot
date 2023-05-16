import asyncio

import discord
import wavelink

no_player_msg = f'*```Bot is not in a voice channel. Play something first.```*'  # message sent when player is none


class GookyPlayer(wavelink.Player):
    autoplay: bool = True
    history: list = list()
    current_track: wavelink.Playable = None


class ControlsView(discord.ui.View):
    player: GookyPlayer = None
    _player_vol_before_mute: int = 50

    @staticmethod
    async def _del_interaction(interaction: discord.Interaction):
        await asyncio.sleep(5)
        try:
            await interaction.delete_original_response()
        except discord.NotFound:
            return

    @discord.ui.button(label="+10s", style=discord.ButtonStyle.blurple, row=0)
    async def seek_f(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)
            return
        new_pos = int(self.player.position + 10000)
        await self.player.seek(new_pos)
        await interaction.response.send_message(f'*```Sought 10s ahead```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.blurple, row=0)
    async def resume_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if self.player.is_playing():
            await interaction.response.send_message(f'*```Already playing```*')
            await self._del_interaction(interaction)
            return
        await self.player.resume()
        await interaction.response.send_message(f'*```Resumed```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="❚❚", style=discord.ButtonStyle.blurple, row=0)
    async def pause_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```Already paused```*')
            await self._del_interaction(interaction)
            return
        await self.player.pause()
        await interaction.response.send_message(f'*```Paused```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="-10s", style=discord.ButtonStyle.blurple, row=0)
    async def seek_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)
            return
        new_pos = int(self.player.position - 10000)
        await self.player.seek(new_pos)
        await interaction.response.send_message(f'*```Sought 10s behind```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="◀◀", style=discord.ButtonStyle.blurple, row=1)
    async def previous_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if len(self.player.history) < 2:
            await interaction.response.send_message(f'*```No more track to play```*')
            await self._del_interaction(interaction)
            return
        if self.player.queue.loop:
            self.player.queue.loop = False
        self.player.current_track = self.player.history[-2]
        await self.player.play(self.player.current_track)
        await interaction.response.send_message(f'*```Playing previous track```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="▶▶", style=discord.ButtonStyle.blurple, row=1)
    async def next_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if self.player.queue.loop:
            self.player.queue.loop = False
        try:
            self.player.current_track = self.player.queue.get()
        except wavelink.QueueEmpty:
            await interaction.response.send_message(f'*```No more tracks to play```*')
            await self._del_interaction(interaction)
            return
        await self.player.play(self.player.current_track)
        await interaction.response.send_message(f'*```Playing next track```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="◼", style=discord.ButtonStyle.blurple, row=1)
    async def stop_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if self.player.is_playing():
            await self.player.stop()
            await interaction.response.send_message(f'*```Stopped```*')
            await self._del_interaction(interaction)
        else:
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)

    @discord.ui.button(label="⥁", style=discord.ButtonStyle.blurple, row=1)
    async def loop_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if self.player.queue.loop:
            self.player.queue.loop = False
            await interaction.response.send_message(f'*```Loop: Set to False```*')
            await self._del_interaction(interaction)
        else:
            self.player.queue.loop = True
            await interaction.response.send_message(f'*```Loop: Set to True```*')
            await self._del_interaction(interaction)

    @discord.ui.button(label="🔉", style=discord.ButtonStyle.blurple, row=2)
    async def vol_reduce(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)
            return
        if self.player.volume == 0:
            await interaction.response.send_message(f'*```Volume is at minimum```*')
            await self._del_interaction(interaction)
            return
        new_vol = int(self.player.volume - 10)
        await self.player.set_volume(new_vol)
        await interaction.response.send_message(f'*```Volume: Set to {new_vol}```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="🔇", style=discord.ButtonStyle.blurple, row=2)
    async def vol_mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)
            return
        self._player_vol_before_mute = self.player.volume
        await self.player.set_volume(0)
        await interaction.response.send_message(f'*```Volume: Set to mute```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="🔈", style=discord.ButtonStyle.blurple, row=2)
    async def vol_unmute(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)
            return
        await self.player.set_volume(self._player_vol_before_mute)
        await interaction.response.send_message(f'*```Volume: Set to unmute```*')
        await self._del_interaction(interaction)

    @discord.ui.button(label="🔊", style=discord.ButtonStyle.blurple, row=2)
    async def vol_increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player:
            await interaction.response.send_message(no_player_msg)
            await self._del_interaction(interaction)
            return
        if not self.player.is_playing():
            await interaction.response.send_message(f'*```No track is playing```*')
            await self._del_interaction(interaction)
            return
        if self.player.volume == 1000:
            await interaction.response.send_message(f'*```Volume is at maximum```*')
            await self._del_interaction(interaction)
            return
        new_vol = int(self.player.volume + 10)
        await self.player.set_volume(new_vol)
        await interaction.response.send_message(f'*```Volume: Set to {new_vol}```*')
        await self._del_interaction(interaction)
