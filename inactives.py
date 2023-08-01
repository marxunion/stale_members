import asyncio
from telethon.tl.functions.messages import (
    GetPollVotesRequest,
    GetMessagesReactionsRequest,
)
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsAdmins, MessageMediaPoll
from datetime import datetime, timedelta
from display import display
from prelude import get_client, get_config

# See config_template.toml for hints
config = get_config()

chat_id = config["chat_id"]
cutoff_days = config["cutoff_days"]
allowlist = config["allowlist"]

client = get_client(config)
client.start()


async def get_poll_votes(msg):
    try:
        if isinstance(msg.media, MessageMediaPoll):
            votes = await client(GetPollVotesRequest(chat_id, msg.id, limit=100))
            return [user.id for user in votes.users]
        else:
            return []
    except:
        print(f"WARINING: The user of this script did not put the vote on the poll: {msg.media.poll.question}")
        return []


async def get_message_authors(msg):
    if msg.from_id is not None:
        return [msg.from_id.user_id]
    else:
        return []


async def get_reactions(msg):
    reactions = await client(GetMessagesReactionsRequest(chat_id, [msg.id]))
    return [user.id for user in reactions.users]


async def get_active_interactions(msg):
    poll_voters = []
    message_authors = []

    [poll_voters, message_authors, reaction_makers] = await asyncio.gather(
        get_poll_votes(msg),
        get_message_authors(msg),
        get_reactions(msg),
    )

    return reaction_makers + poll_voters + message_authors


async def get_inactive_users():
    cutoff_date = datetime.today() - timedelta(days=cutoff_days)

    [all_users, admins] = await asyncio.gather(
        client.get_participants(chat_id),
        client.get_participants(chat_id, filter=ChannelParticipantsAdmins),
        # we cannot get all of the messages in parallel: it happens that there are a lot of messages
        # and getting them all at once is a very long operation
        # therefore we have to use client.iter_messages and handle every message separately (see below)
        # client.get_messages(chat_id, reverse=True, offset_date=cutoff_date, limit=None),
    )

    print(f"Total number of participants: {len(all_users)}")
    print(f"Admin users: {len(admins)}")

    normies = [p for p in all_users if p.id not in (admin.id for admin in admins)]
    print(f"Regular participants: {len(normies)}")

    # go through all of the messages
    # collect interactions with the messages
    # users who interacted with the chat (posted message, voted or reacted on the message) after the cutoff date are active
    active_user_ids = []
    i = 0
    async for msg in client.iter_messages(chat_id, reverse=True, offset_date=cutoff_date, limit=None):
        if (i + 1) % 100 == 0:
            print(f"handled {i + 1} messages")
        i += 1

        user_ids = await get_active_interactions(msg)

        if len(user_ids) == 0:
            print(f"No users involved into this message (event author was not found): {msg.message}")
        active_user_ids += user_ids

    # all users which are not active or not in the allowlist are inactive
    inactive_users = [user for user in normies if user.id not in active_user_ids and user.username not in allowlist]

    # Filter out users who joined the chat after the cutoff date
    # because they have just joined and probably haven't had a chance to interact with the chat
    inactive_participants = await asyncio.gather(
        *map(lambda user: client(GetParticipantRequest(chat_id, user.id)), inactive_users)
    )
    inactive_participants = filter(
        lambda participant: participant.participant.date.timestamp() < cutoff_date.timestamp(),
        inactive_participants,
    )
    inactive_users = [participant.users[0] for participant in inactive_participants]

    print(f"Among the regular participants, inactive users: {len(inactive_users)}")

    for idx, user in enumerate(inactive_users):
        print(idx + 1, display(user), user.id)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_inactive_users())
