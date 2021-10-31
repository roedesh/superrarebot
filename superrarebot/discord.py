import logging
from pathlib import Path

from discord import Activity, ActivityType, Embed
from discord.ext import commands, tasks

from superrarebot.config import (
    BASE_DIR,
    DISCORD_CHANNEL_ID,
    DISCORD_SERVER_ID,
    SUPERRARE_ARTIST,
    UPDATE_INTERVAL,
)
from superrarebot.datasources.superrare import (
    get_creations,
    get_local_creations,
    save_creations_to_file,
)

log = logging.getLogger(__name__)
bot = commands.Bot(command_prefix="!")
db_json = Path(BASE_DIR).joinpath("db.json")


@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    await bot.change_presence(
        activity=Activity(
            type=ActivityType.listening,
            name=f"@{SUPERRARE_ARTIST} updates on SuperRare",
        )
    )


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.creations = None
        self.broadcast_updates.start()

    def cog_unload(self):
        self.broadcast_updates.cancel()

    @tasks.loop(minutes=UPDATE_INTERVAL)
    async def broadcast_updates(self):
        log.info(f"Started <broadcast_updates> task")

        if self.creations == None:
            self.creations = get_local_creations()

        creations_from_superrare = get_creations(SUPERRARE_ARTIST)
        messages = []

        for creation in creations_from_superrare:
            new_actions = []

            if not self.creations:
                new_actions += creation.actions
            else:
                for old_creation in self.creations:
                    if creation.url == old_creation.url:
                        new_action_len = len(creation.actions)
                        old_action_len = len(old_creation.actions)

                        if new_action_len > old_action_len:
                            new_actions += creation.actions[old_action_len:]

            for action in new_actions:
                messages.append({"creation": creation, "action": action})

        self.creations = creations_from_superrare
        save_creations_to_file(self.creations)

        server = bot.get_guild(DISCORD_SERVER_ID)
        bid_channel = server.get_channel(DISCORD_CHANNEL_ID)

        for message in messages:
            creation = message["creation"]
            action = message["action"]

            embed = Embed(
                title=creation.name,
                description=action.description,
                url=creation.url,
                color=0x00FF00,
            )

            embed.set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar_url,
            )

            if creation.image_url:
                embed.set_thumbnail(url=creation.image_url)

            if action.transaction_id:
                embed.add_field(
                    name="Transaction",
                    value=f"[{action.transaction_id}](https://etherscan.io/tx/{action.transaction_id})",
                )

            await bid_channel.send(embed=embed)

        log.info(f"Finished <broadcast_updates> task")

    @broadcast_updates.before_loop
    async def before_broadcast_bids(self):
        await self.bot.wait_until_ready()


bot.add_cog(MainCog(bot))
