# Purpose

In our organization we need to monitor inactive users. Some of those inactive users are admins which must be manually approached, others are the regular members of the chat.

First scripy `inactives.py` analyzes the chat or group in Telegram and returns you a list of **recently inactive** chat members. By **recently inactive** we mean:
1. no messages in the chat
2. no reactions
3. no votes in the polls
4. user is not an admin
in last X days (where X is configurable).

Second script `admins.py` just returns you the list of the admin users for an investigation.

# How it works

The scripts use `telethon` library to access the telegram API. It gets the members of the chat, excludes admins, gets last messages in the chat and checks excludes members who sent at least one message, voted on the polls or reacted on the messages with emojis.

# Setup

In order to use the script you need to:

1. Create and register an application in telegram
2. Be an admin of the group or chat
3. Find out the ID of your chat
4. Install git and python and even pipenv (if you wish, you can use any other dependency management if you need)

## Register new app

Go to https://my.telegram.org/ and create new application.

## Find the chat ID

For that you need to:
1. login into https://web.telegram.org/
2. open your chat and copy the last part of the URL. For example, if the URL to your chat is https://web.telegram.org/k/#-123456789 then `123456789` is the value you need.
3. Then add `-100` in front - this will be the `chat_id`. In our example, `-100123456789` is the `chat_id`.

## Setup the script

1. Clone the project
2. Install dependencies - I used `pipenv`, so `pipenv install` should work correctly
3. Setup configs
    1. Create file `config.toml` (use `config_template.toml`) and copy the values of the `api_id` and `api_hash` from https://my.telegram.org/apps
    2. Get the `chat_id` and add it to the config as well. you should have something like:
        ```toml
        api_id = "33355555"
        api_hash = "blablablablabla"
        chat_id = -100123456789
        ```

## Run the script

If you used `pipenv` to install dependencies you can run next command:

```bash
pipenv run python inactives.py
```

or if you installed the dependencies globally then just

```bash
python inactives.py
```