def display(user):
    str = user.first_name or ""
    if user.last_name:
        str += f" {user.last_name}"

    if user.username:
        str += f" [{user.username}]"

    return str
