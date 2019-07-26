from .soup import raw_html, doc_from_raw_html

def get_url_for_screen_name(screen_name: str) -> str:
    if not screen_name:
        raise ValueError('screen_name is an empty string.')
    return f'https://twitter.com/{screen_name}'

def follower_count(screen_name: str) -> int:
    if not screen_name:
        raise ValueError('screen_name is an empty string.')
    raw = raw_html(get_url_for_screen_name(screen_name))
    if not raw:
        return
    soup = doc_from_raw_html(raw)
    return (
        soup
        .find_all(attrs={'data-nav':'followers'})[0]
        .find_all("span", class_="ProfileNav-value")[0]['data-count']
    )    
