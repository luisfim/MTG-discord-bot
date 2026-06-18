import os
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from database import (
    init_database,
    set_update_channel,
    get_update_channel,
    set_update_sources,
    get_update_settings,
    get_all_update_settings,
    set_last_arena_url,
    set_last_mtgo_url,
)

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

        if not automatic_update_check.is_running():
            automatic_update_check.start()


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

@bot.tree.command(name="update_settings", description="Show this server's Magic update settings.")
async def update_settings(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    settings = get_update_settings(interaction.guild.id)

    channel_text = "Not configured"

    if settings["update_channel_id"] is not None:
        channel = interaction.guild.get_channel(settings["update_channel_id"])

        if channel is not None:
            channel_text = channel.mention
        else:
            channel_text = "Configured channel was not found"

    embed = discord.Embed(
        title="Magic Update Settings",
        color=0x00AA88,
    )

    embed.add_field(
        name="Updates Channel",
        value=channel_text,
        inline=False,
    )

    embed.add_field(
        name="MTG Arena Updates",
        value="Enabled" if settings["arena_enabled"] else "Disabled",
        inline=True,
    )

    embed.add_field(
        name="Magic Online Updates",
        value="Enabled" if settings["mtgo_enabled"] else "Disabled",
        inline=True,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="send_test_update", description="Send a test Magic update to the configured updates channel.")
@app_commands.checks.has_permissions(manage_guild=True)
async def send_test_update(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        settings = get_update_settings(interaction.guild.id)

        print("DEBUG SETTINGS:", settings)

        channel_id = settings["update_channel_id"]

        if channel_id is None:
            await interaction.followup.send(
                "No updates channel has been configured yet. Use `/set_updates_channel` first.",
                ephemeral=True,
            )
            return

        if not settings["arena_enabled"] and not settings["mtgo_enabled"]:
            await interaction.followup.send(
                "Both Arena and MTGO updates are disabled. Use `/set_update_sources` first.",
                ephemeral=True,
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            await interaction.followup.send(
                "The configured updates channel could not be found. Use `/set_updates_channel` again.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Digital Magic Test Update",
            description="This is a test post for the configured Magic updates channel.",
            color=0x00AA88,
        )

        if settings["arena_enabled"]:
            try:
                arena = await get_latest_arena_patch()

                embed.add_field(
                    name="MTG Arena",
                    value=f"[{arena['title']}]({arena['url']})\n{arena['note']}",
                    inline=False,
                )

            except Exception as error:
                print(f"Error fetching Arena update: {error}")

                embed.add_field(
                    name="MTG Arena",
                    value="Could not fetch Arena update.",
                    inline=False,
                )

        if settings["mtgo_enabled"]:
            try:
                mtgo = await get_latest_mtgo_announcement()

                embed.add_field(
                    name="Magic Online",
                    value=f"[{mtgo['title']}]({mtgo['url']})\n{mtgo['note']}",
                    inline=False,
                )

            except Exception as error:
                print(f"Error fetching MTGO update: {error}")

                embed.add_field(
                    name="Magic Online",
                    value="Could not fetch MTGO update.",
                    inline=False,
                )

        if len(embed.fields) == 0:
            await interaction.followup.send(
                "No update sources are enabled.",
                ephemeral=True,
            )
            return

        embed.set_footer(text="Sources: Wizards of the Coast / Magic Online")

        await channel.send(embed=embed)

        await interaction.followup.send(
            f"Test update sent to {channel.mention}.",
            ephemeral=True,
        )

    except Exception as error:
        print(f"Error in /send_test_update: {error}")

        await interaction.followup.send(
            "Something went wrong while sending the test update. Check the Codespaces terminal for the error.",
            ephemeral=True,
        )
@bot.tree.command(name="set_update_sources", description="Choose whether this server receives Arena, MTGO, or both updates.")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_update_sources_command(
    interaction: discord.Interaction,
    arena: bool,
    mtgo: bool,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    set_update_sources(
        guild_id=interaction.guild.id,
        arena_enabled=arena,
        mtgo_enabled=mtgo,
    )

    await interaction.response.send_message(
        f"Update sources changed.\nMTG Arena: {'enabled' if arena else 'disabled'}\nMagic Online: {'enabled' if mtgo else 'disabled'}",
        ephemeral=True,
    )

@tasks.loop(hours=6)
async def automatic_update_check():
    await bot.wait_until_ready()

    print("Running automatic update check...")

    settings_list = get_all_update_settings()

    if not settings_list:
        print("No servers configured for updates.")
        return

    for settings in settings_list:
        guild = bot.get_guild(settings["guild_id"])

        if guild is None:
            print(f"Guild not found: {settings['guild_id']}")
            continue

        channel = guild.get_channel(settings["update_channel_id"])

        if channel is None:
            print(f"Update channel not found for guild: {guild.name}")
            continue

        embed = discord.Embed(
            title="Digital Magic Update",
            description="New official digital Magic update detected.",
            color=0x00AA88,
        )

        has_new_update = False

        if settings["arena_enabled"]:
            try:
                arena = await get_latest_arena_patch()

                if arena["url"] != settings["last_arena_url"]:
                    embed.add_field(
                        name="MTG Arena",
                        value=f"[{arena['title']}]({arena['url']})\n{arena['note']}",
                        inline=False,
                    )

                    set_last_arena_url(settings["guild_id"], arena["url"])
                    has_new_update = True

            except Exception as error:
                print(f"Automatic Arena check failed for {guild.name}: {error}")

        if settings["mtgo_enabled"]:
            try:
                mtgo = await get_latest_mtgo_announcement()

                if mtgo["url"] != settings["last_mtgo_url"]:
                    embed.add_field(
                        name="Magic Online",
                        value=f"[{mtgo['title']}]({mtgo['url']})\n{mtgo['note']}",
                        inline=False,
                    )

                    set_last_mtgo_url(settings["guild_id"], mtgo["url"])
                    has_new_update = True

            except Exception as error:
                print(f"Automatic MTGO check failed for {guild.name}: {error}")

        if has_new_update:
            embed.set_footer(text="Sources: Wizards of the Coast / Magic Online")
            await channel.send(embed=embed)
            print(f"Posted update to {guild.name}.")

        else:
            print(f"No new updates for {guild.name}.")


@bot.tree.command(name="check_updates_now", description="Manually run the automatic update check.")
@app_commands.checks.has_permissions(manage_guild=True)
async def check_updates_now(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        await automatic_update_check()

        await interaction.followup.send(
            "Manual update check completed. Check the configured updates channel.",
            ephemeral=True,
        )

    except Exception as error:
        print(f"Error in /check_updates_now: {error}")

        await interaction.followup.send(
            "Something went wrong while checking updates. Check the Codespaces terminal.",
            ephemeral=True,
        )

bot.run(DISCORD_TOKEN)