import os
import discord
from discord import app_commands
from dotenv import load_dotenv

from database import init_database, set_update_channel, get_update_channel

from sources import (
    get_latest_arena_patch,
    get_latest_mtgo_announcement,
    get_arena_status,
    get_mtgo_status,
)

load_dotenv()
init_database()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN. Add it to your .env file.")

class MagicDigitalBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} command(s).")


bot = MagicDigitalBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong. Magic Digital Bot is alive.")

@bot.tree.command(name="arena_latest", description="Show the latest MTG Arena patch notes.")
async def arena_latest(interaction: discord.Interaction):
    await interaction.response.defer()

    patch = await get_latest_arena_patch()

    embed = discord.Embed(
        title=patch["title"],
        url=patch["url"],
        description=patch["note"],
        color=0x7B3FCE,
    )

    embed.set_footer(text="Source: Wizards of the Coast")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="mtgo_latest", description="Show the latest Magic Online announcement.")
async def mtgo_latest(interaction: discord.Interaction):
    await interaction.response.defer()

    announcement = await get_latest_mtgo_announcement()

    embed = discord.Embed(
        title=announcement["title"],
        url=announcement["url"],
        description=announcement["note"],
        color=0x2F80ED,
    )

    embed.set_footer(text="Source: Magic Online")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="digital_magic_latest", description="Show latest MTG Arena and MTGO updates.")
async def digital_magic_latest(interaction: discord.Interaction):
    await interaction.response.defer()

    arena = await get_latest_arena_patch()
    mtgo = await get_latest_mtgo_announcement()

    embed = discord.Embed(
        title="Digital Magic Latest Updates",
        description="Latest official update links for MTG Arena and Magic Online.",
        color=0x00AA88,
    )

    embed.add_field(
        name="MTG Arena",
        value=f"[{arena['title']}]({arena['url']})\n{arena['note']}",
        inline=False,
    )

    embed.add_field(
        name="Magic Online",
        value=f"[{mtgo['title']}]({mtgo['url']})\n{mtgo['note']}",
        inline=False,
    )

    embed.set_footer(text="Sources: Wizards of the Coast / Magic Online")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="arena_status", description="Show the current MTG Arena service status.")
async def arena_status(interaction: discord.Interaction):
    await interaction.response.defer()

    arena_status_data = await get_arena_status()

    embed = discord.Embed(
        title=arena_status_data["title"],
        url=arena_status_data["url"],
        description=arena_status_data["note"],
        color=0xF2C94C,
    )

    embed.add_field(
        name="Status",
        value=arena_status_data["status"],
        inline=False,
    )

    embed.set_footer(text="Source: Official MTG Arena Status Page")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="mtgo_status", description="Show the current Magic Online server status.")
async def mtgo_status(interaction: discord.Interaction):
    await interaction.response.defer()

    mtgo_status_data = await get_mtgo_status()

    embed = discord.Embed(
        title=mtgo_status_data["title"],
        url=mtgo_status_data["url"],
        description=mtgo_status_data["note"],
        color=0xF2994A,
    )

    embed.add_field(
        name="Status",
        value=mtgo_status_data["status"],
        inline=False,
    )

    embed.set_footer(text="Source: Official Magic Online website")

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="set_updates_channel", description="Set the channel for future Magic update notifications.")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_updates_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    set_update_channel(interaction.guild.id, channel.id)

    await interaction.response.send_message(
        f"Update channel set to {channel.mention}.",
        ephemeral=True,
    )

@bot.tree.command(name="updates_channel", description="Show the configured Magic updates channel.")
async def updates_channel(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    channel_id = get_update_channel(interaction.guild.id)

    if channel_id is None:
        await interaction.response.send_message(
            "No updates channel has been configured yet. Use `/set_updates_channel` first.",
            ephemeral=True,
        )
        return

    channel = interaction.guild.get_channel(channel_id)

    if channel is None:
        await interaction.response.send_message(
            "An updates channel was configured, but I cannot find it anymore. It may have been deleted.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Current updates channel: {channel.mention}",
        ephemeral=True,
    )

bot.run(DISCORD_TOKEN)