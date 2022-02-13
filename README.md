# logging-bot

Simple Discord bot which logs several events in your server, including:
 - Message Edits
 - Message Deletes
 - Role Adds
 - Role Removes
 - Member joins
 - Member leaves


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
