import logging
from datetime import datetime, timedelta
from threading import Timer
from typing import Optional

import discord
from discord.ext import commands
from config import LOG_CHANNELS, WHITELIST_ROLES, AUTO_MESSAGES
from key import KEY
from dataclasses import dataclass

intents = discord.Intents().default()
intents.members = True
intents.guilds = True

client = commands.Bot(command_prefix='E', intents=intents)


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
    embed.add_field(name="User", value=f'{user}\n<@{user.id}>\n{user.id}')


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


def send_forever(interval: timedelta, message: str, guild_id: int, channel_id: int):
    async def wrapper():
        try:
            guild = client.get_guild(guild_id)
            channel = guild.get_channel(channel_id)
            await channel.send(message)
        except AttributeError as e:
            logging.error(f'Invalid guild configuration. {e}')
        timer = Timer(interval=interval.total_seconds(), function=wrapper)
        timer.daemon = True
        timer.start()


def calc_time_from_time_args(time_str: str) -> Optional[timedelta]:
    """
    Calculates time from given time args.
    Arg Format:
      <n><f>
      where <f> can be m (minutes), h (hours), d (days) or w (weeks)

    :raise:
      ValueError if invalid arg is given
    :return:
      Calculated timedelta or None if None was passed in
    """

    if not time_str:
        return None

    time_str = time_str.lower()
    minute, hour, day, week = 0, 0, 0, 0
    args = time_str.split(' ')
    if len(args) > 0:
        for arg in args:
            try:
                if 'h' in arg:
                    hour += int(arg.rstrip('h'))
                elif 'm' in arg:
                    minute += int(arg.rstrip('m'))
                elif 'w' in arg:
                    week += int(arg.rstrip('w'))
                elif 'd' in arg:
                    day += int(arg.rstrip('d'))
                else:
                    raise ValueError(f'Invalid time argument: {arg}')
            except ValueError:  # Make sure both cases are treated the same
                raise ValueError(f'Invalid time argument: {arg}')
    return timedelta(hours=hour, minutes=minute, days=day, weeks=week)


for message in AUTO_MESSAGES:
    send_forever(interval=calc_time_from_time_args(message['interval']),
                 message=message['message'],
                 guild_id=message['guild_id'],
                 channel_id=message['channel_id'])


client.run(KEY)
