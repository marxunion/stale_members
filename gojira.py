import asyncio
import requests
from prelude import get_config, get_client
from telethon.tl.types import ChannelParticipantsAdmins

async def get_active_tg_users(client, config):
    chat_id = config["chat_id"]

    [all_users, admins] = await asyncio.gather(
        client.get_participants(chat_id),
        client.get_participants(chat_id, filter=ChannelParticipantsAdmins),
    )

    normies = [p for p in all_users if p.id not in (admin.id for admin in admins)]
    return [user for user in normies if user.username is not None]


def strip_username(username):
    return username.strip('@')


def mk_jql(usernames):
    subqueries = [f"text~{strip_username(username)}" for username in usernames]
    return "project=RECRUT and " + " or ".join(subqueries)


def display(user, issue):
    str = user.first_name or ""
    if user.last_name:
        str += f" {user.last_name}"

    if user.username:
        str += f" [{user.username}]"

    return f"{str} | {issue['key']} | "


async def main(client, config):
    tg_users = await get_active_tg_users(client, config)
    tg_usernames = [user.username for user in tg_users]
    jql = mk_jql(usernames=tg_usernames)

    url = "https://task.marxunion.org/rest/api/2/search"
    res = requests.get(url=url, params={"jql": jql}, auth=auth)
    res = res.json()
    completed_users = find_completed_candidates(tg_users, res["issues"])

    for (user, issue) in completed_users:
        print(display(user, issue))

def find_candidate_issue(user, issues):
    stripped_username = strip_username(user.username)
    for issue in issues:
        tg_username = issue["fields"]["customfield_10622"]
        if tg_username is not None and stripped_username in tg_username:
            return issue
    return None

def find_completed_candidates(tg_users, issues) -> list:
    completed = []
    for user in tg_users:
        recruit_issue = find_candidate_issue(user, issues)
        # if no ticket is found
        if recruit_issue is None:
            continue
        # if ticket is done (closed, completed, finished - any green status)
        if recruit_issue["fields"]["status"]["statusCategory"]["key"] != "done":
            continue
        completed.append((user, recruit_issue))
    return completed


if __name__ == "__main__":
    config = get_config()
    jiraconf = config["jira"]
    auth = (jiraconf["username"], jiraconf["password"])

    client = get_client(config)
    client.start()

    asyncio.get_event_loop().run_until_complete(main(client, config))
