from .soup import raw_html, doc_from_raw_html

def get_url_for_username(username: str) -> str:
    return f'https://twitter.com/{username}'

def follower_count(username):
    raw = raw_html(get_url_for_username(username))
    if not raw:
        return
    soup = doc_from_raw_html(raw)
    return (
        soup
        .find_all(attrs={'data-nav':'followers'})[0]
        .find_all("span", class_="ProfileNav-value")[0]['data-count']
    )    
