import asyncio
from telethon.tl.types import ChannelParticipantsAdmins, MessageMediaPoll
from prelude import get_client, get_config
from display import display

config = get_config()

client = get_client(config)
client.start()

chat_id = config["chat_id"]

async def get_admins():
    admins = await client.get_participants(chat_id, filter=ChannelParticipantsAdmins)
    for idx, user in enumerate(admins):
        print(idx + 1, display(user))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_admins())