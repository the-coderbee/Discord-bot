import uuid

import discord
from PIL import Image, ImageFont, ImageDraw

from levelsystem.models import LevelModel
from settings import TEMP_AVT_DIR, STATIC_IMG_DIR, IMG_DIR
from users.models import User


class LevelCard:
    _avt_dir: str
    _level_card_dir: str

    def __init__(self, member: discord.Member, guild_id: int, total_xp: float):
        self._member = member
        self._guild_id = guild_id
        self._total_xp = total_xp

    async def save_user_avatar(self):
        self._avt_dir = TEMP_AVT_DIR / f'{self._member.id}.png'
        await self._member.avatar.save(self._avt_dir)

    def _fetch_user_data(self):
        rank = User.get_rank_from_leaderboard(self._member, self._guild_id)
        current_level = LevelModel.get_level_from_xp(self._total_xp)
        level_gap, progress = LevelModel.current_level_gap(self._total_xp)
        return rank, current_level, level_gap, progress

    def make_rank_card(self):
        uuid4 = str(uuid.uuid4())
        font_big = ImageFont.truetype('arial.ttf', 42)
        font_large = ImageFont.truetype('arial.ttf', 70)
        rank, current_level, level_gap, progress = self._fetch_user_data()

        background_img = Image.open(STATIC_IMG_DIR / 'bottom_card.png')
        foreground_img = Image.open(STATIC_IMG_DIR / 'rank_card.png')
        avatar_img = Image.open(self._avt_dir).convert("RGBA")
        avatar_img.thumbnail((340, 340), Image.Resampling.LANCZOS)

        background_img.paste(avatar_img, (68, 68), avatar_img)
        background_img.paste(foreground_img, (0, 0), foreground_img)

        draw = ImageDraw.Draw(background_img)
        draw.text(
            (1445, 119),
            f"{str(rank).rjust(2, '0')}",
            fill=(252, 186, 3),
            font=font_big,
            anchor="ls",
        )
        draw.text(
            (1732, 119),
            f"{str(current_level).rjust(2, '0')}",
            fill=(252, 186, 3),
            font=font_big,
            anchor="ls",
        )
        draw.text(
            (600, 400),
            f"{self._member.display_name}",
            fill=(252, 186, 3),
            font=font_large,
            anchor="ls",
        )
        draw.text(
            (1380, 400),
            f"{progress:4}  /  {level_gap:4}",
            fill=(252, 186, 3),
            font=font_large,
            anchor="ls",
        )

        # draw progress bar.
        # progress bar coord (422,440,1864,490)
        progress_percentage = progress / level_gap
        if progress_percentage == 1:
            progress_percentage = 0

        full_width = 1864 - 422
        if progress > 0:
            width = round((full_width * progress_percentage), 1)
            draw.rounded_rectangle(((422, 440), (422 + width, 490)), 10, fill=(252, 186, 3))

        # required_xp = self._next_level_xp_diff - self._level_progress
        # progress_percentage = round(progress * 100)

        self._level_card_dir = IMG_DIR / f"{uuid4}.png"
        background_img.save(self._level_card_dir)

        return self._level_card_dir, level_gap - progress

    def delete_image(self):
        try:
            self._avt_dir.unlink()
            self._level_card_dir.unlink()
        except PermissionError:
            return
