# logging-bot

Simple Discord bot which logs several events in your server, including:
 - Message Edits
 - Message Deletes
 - Role Adds
 - Role Removes
 - Member joins
 - Member leaves


The bot is also able to perform sending messages at a specified interval periodically.


## Config

The configuration file is `config.py` <br>
The channel where the logs are sent can be set in the LOG_CHANNELS dict
```python
LOG_CHANNELS = {
    # guild_id: channel_id
    715507174167806042: 942176153727287346
}
```

Additionally you can define a list of roles which will be excluded from loggings.
```python
WHITELIST_ROLES = [
    715567086642135061
]
```
The automatic messages are defined like this
```python
AUTO_MESSAGES = [
    {
        'guild_id': 443583326507499520,
        'channel_id': 641597836647202838,
        'message': '!d bump',
        'interval': '2h 1m'
    }
]
```