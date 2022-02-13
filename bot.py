import discord
from discord.ext import commands
from discord_slash import SlashCommand
from config import LOG_CHANNELS, WHITELIST_ROLES
from key import KEY

intents = discord.Intents().default()
intents.members = True
intents.guilds = True

client = commands.Bot(command_prefix='E', intents=intents)
slash = SlashCommand(client, sync_commands=True)


def should_be_logged(member):
    return all(
        all(
            role.id != whitelist_role for role in member.roles
        )
        for whitelist_role in WHITELIST_ROLES
    )


@client.event
async def on_ready():
    print('Bot Ready')


def add_member_information(embed, member: discord.Member):
    add_user(embed, member)
    embed.add_field(name="Created at", value=member.created_at, inline=False)
    embed.add_field(name="Joined at", value=member.joined_at)
    embed.add_field(name="Members", value=member.guild.member_count)
    embed.set_thumbnail(url=f'{member.avatar_url}')


def add_user(embed, user: discord.Member):
    embed.add_field(name="User", value=f'<@{user.id}>\n{user.id}')


def add_channel(embed, channel: discord.TextChannel):
    embed.add_field(name="Channel", value=f'<#{channel.id}>\n{channel.id}')


def add_message(embed, message: discord.Message):
    embed.add_field(name="Message", value=f'[Click here](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}])')


@client.event
async def on_message_edit(before, after):
    if should_be_logged(before.author):
        embed = discord.Embed(title='__Message Edit__', colour=discord.Colour.dark_orange())
        add_user(embed, before.author)
        add_channel(embed, before.channel)
        add_message(embed, before)
        embed.add_field(name="Original", value=before.content)
        embed.add_field(name="Edited", value=after.content)
        await log_embed(before.guild.id, embed)


@client.event
async def on_message_delete(message):
    if should_be_logged(message.author):
        embed = discord.Embed(title='__Message Delete__', colour=discord.Colour.magenta())
        add_user(embed, message.author)
        add_channel(embed, message.channel)
        embed.add_field(name="Content", value=message.content)
        await log_embed(message.guild.id, embed)


@client.event
async def on_member_join(member):
    embed = discord.Embed(title="__Member Joined__", colour=discord.Colour.green())
    add_member_information(embed, member)
    await log_embed(member.guild.id, embed)


@client.event
async def on_member_remove(member):
    embed = discord.Embed(title="__Member Left__", colour=discord.Colour.red())
    add_member_information(embed, member)
    await log_embed(member.guild.id, embed)


@client.event
async def on_member_update(before, after):
    if should_be_logged(before):
        remove = set(before.roles) - set(after.roles)
        add = set(after.roles) - set(before.roles)
        if remove:
            embed = discord.Embed(title="__Role Removed__", colour=discord.Colour.blurple())
            role = list(remove)[0]
        elif add:
            embed = discord.Embed(title="__Role Added__", colour=discord.Colour.blurple())
            role = list(add)[0]
        else:
            return
        add_user(embed, before)
        embed.add_field(name="Role", value=f'<@&{role.id}>\n{role.id}')
        await log_embed(before.guild.id, embed)


async def log_embed(guild_id, embed):
    guild = client.get_guild(guild_id)
    channel = guild.get_channel(LOG_CHANNELS[guild_id])
    await channel.send(content='', embed=embed)


client.run(KEY)
