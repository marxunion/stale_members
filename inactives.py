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


async def get_poll_voters_ids(msg):
    if isinstance(msg.media, MessageMediaPoll):
        votes = await client(GetPollVotesRequest(chat_id, msg.id, limit=100))
        return [user.id for user in votes.users]
    else:
        return []


async def get_message_authors_ids(msg):
    if msg.media is None and msg.from_id is not None:
        return [msg.from_id.user_id]
    else:
        return []


async def get_reaction_makers_ids(msg):
    reactions = await client(GetMessagesReactionsRequest(chat_id, [msg.id]))
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


async def get_inactive_users():
    cutoff_date = datetime.today() - timedelta(days=cutoff_days)

    [all_users, admins, messages] = await asyncio.gather(
        client.get_participants(chat_id),
        client.get_participants(chat_id, filter=ChannelParticipantsAdmins),
        client.get_messages(chat_id, reverse=True, offset_date=cutoff_date, limit=None),
    )

    print(f"Total number of participants: {len(all_users)}")
    print(f"Admin users: {len(admins)}")

    normies = [p for p in all_users if p.id not in (admin.id for admin in admins)]
    print(f"Regular participants: {len(normies)}")

    active_user_ids_nested = await asyncio.gather(*map(get_active_user_ids, messages))
    active_user_ids = [user_id for users in active_user_ids_nested for user_id in users]
    inactive_users = [user for user in normies if user.id not in active_user_ids]

    # Filter out users who joined the chat after the cutoff date
    inactive_participants = await asyncio.gather(
        *map(lambda user: client(GetParticipantRequest(chat_id, user.id)), inactive_users)
    )
    inactive_participants = filter(
        lambda participant: participant.participant.date.timestamp() < cutoff_date.timestamp(),
        inactive_participants,
    )
    inactive_users = [participant.users[0] for participant in inactive_participants]
    inactive_users = [user for user in inactive_users if user.username not in allowlist]

    print(f"Among the regular participants, inactive users: {len(inactive_users)}")

    for idx, user in enumerate(inactive_users):
        print(idx + 1, display(user))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_inactive_users())
