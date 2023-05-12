import asyncio
import tomllib
from telethon import TelegramClient
from telethon.tl.functions.messages import (
    GetPollVotesRequest,
    GetMessagesReactionsRequest,
)
from telethon.tl.types import ChannelParticipantsAdmins, MessageMediaPoll
from datetime import datetime, timedelta

# See config_template.toml for hints
config = None
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

client = TelegramClient("stale_members", config["api_id"], config["api_hash"])
client.start()

async def get_poll_voters_ids(msg):
    if isinstance(msg.media, MessageMediaPoll):
        votes = await client(GetPollVotesRequest(config["chat_id"], msg.id, limit=100))
        return [user.id for user in votes.users]
    else:
        return []


async def get_message_authors_ids(msg):
    if msg.media is None and msg.from_id is not None:
        return [msg.from_id.user_id]
    else:
        return []


async def get_reaction_makers_ids(msg):
    reactions = await client(GetMessagesReactionsRequest(config["chat_id"], [msg.id]))
    return [user.id for user in reactions.users]


async def get_active_user_ids(msg):
    poll_voters = []
    message_authors = []

    [poll_voters, message_authors, reaction_makers] = await asyncio.gather(
        get_poll_voters_ids(msg),
        get_message_authors_ids(msg),
        get_reaction_makers_ids(msg),
    )

    return reaction_makers + poll_voters + message_authors


def display(user):
    str = user.first_name or ""
    if user.last_name:
        str += f" {user.last_name}"

    if user.username:
        str += f" [{user.username}]"

    return str


async def main():
    days_ago = datetime.today() - timedelta(days=config["offset_days"])

    [all_users, admins, messages] = await asyncio.gather(
        client.get_participants(config["chat_id"]),
        client.get_participants(config["chat_id"], filter=ChannelParticipantsAdmins),
        client.get_messages(config["chat_id"], reverse=True, offset_date=days_ago, limit=None),
    )

    print(f"Total number of participants: {len(all_users)}")
    print(f"Admin users: {len(admins)}")

    normies = [p for p in all_users if p.id not in (admin.id for admin in admins)]
    print(f"Regular participants: {len(normies)}")

    active_user_ids_nested = await asyncio.gather(*map(get_active_user_ids, messages))
    active_user_ids = [user_id for users in active_user_ids_nested for user_id in users]
    inactive_users = [user for user in normies if user.id not in active_user_ids]

    print(f"Among the regular participants, inactive users: {len(inactive_users)}")

    for idx, user in enumerate(inactive_users):
        print(idx + 1, display(user))


asyncio.get_event_loop().run_until_complete(main())
