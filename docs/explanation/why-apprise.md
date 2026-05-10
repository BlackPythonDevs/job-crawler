# Why Apprise instead of Discord directly

The first version of this bot used `discord.py` and posted embeds straight to a channel. It worked, but it built in two assumptions that turned out to be wrong:

1. **The destination is always Discord.** Some users wanted Slack. Some wanted email. Some wanted multiple destinations.
2. **The bot needs a Discord client connection.** Maintaining a gateway connection is expensive for a service that posts a few messages every four hours.

[Apprise](https://github.com/caronc/apprise) is a notification library with broad destination support — Discord, Slack, Telegram, email, push services, etc. The companion [Apprise API](https://github.com/caronc/apprise-api) wraps it in an HTTP server you POST to.

## What changed

- The bot no longer has a `discord-py` dependency.
- There's no `DISCORD_TOKEN`, no `DISCORD_CHANNEL_ID`, no gateway connection.
- The bot makes one POST per job. That's it.
- Destinations are configured **on the Apprise side**, not in the bot. Adding a Slack channel doesn't require redeploying the bot.

## Trade-offs

- You now have to run an Apprise API instance. For a Compose-only setup this is a third container.
- Rich-format support depends on Apprise's translation layer. Discord embeds via Apprise look slightly different from native `discord.py` embeds.
- If you wanted features specific to one destination (Discord slash commands, Slack interactive messages), you don't get them. That's not what this bot does.

## When this would be the wrong call

If you needed bidirectional Discord interactions (commands, reactions, threading), you would want to keep `discord.py` and lose the Apprise abstraction. This bot is one-way: jobs flow out, nothing comes back.
