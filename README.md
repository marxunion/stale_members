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
pipenv run python main.py
```

or if you installed the dependencies globally then just

```bash
python main.py
```