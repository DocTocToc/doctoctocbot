def webfinger_url(acct):
    try:
        username, host = acct.split('@')
    except:
        return
    return f"https://{host}/users/{username}"