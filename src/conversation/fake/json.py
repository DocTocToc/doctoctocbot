import json
import datetime
from faker import Faker
from django.conf import settings
from bot.lib.datetime import datetime_twitter_str

fake = Faker()


def fake_json(statusid, user_id, user_screen_name, user_name, hashtag_list, created_at):
    hashtag_string = "#" + " #".join(hashtag_list)
    max_text_length = settings.TWEET_LENGTH - len(hashtag_string) - 1
    status_created_at = created_at
    days_delta = fake.pyint(min_value=1, max_value=730, step=1)
    user_created_at = created_at - datetime.timedelta(days=days_delta)
    status_dt_str = datetime_twitter_str(status_created_at)
    user_dt_str = datetime_twitter_str(user_created_at)
    tweet_object = {
        'id': statusid,
        'geo': None,
        'lang': 'und',
        'user': {
            'id': user_id,
            'url': None,
            'lang': None,
            'name': user_name,
            'id_str': str(user_id),
            'entities': {
                'description': {
                    'urls': []
                }
            },
            'location': '',
            'verified': False,
            'following': False,
            'protected': False,
            'time_zone': None,
            'created_at': user_dt_str,
            'utc_offset': None,
            'description': '',
            'followed_by': False,
            'geo_enabled': False,
            'screen_name': user_screen_name,
            'listed_count': 0,
            'can_media_tag': True,
            'friends_count': fake.random_int(min=0, max=1000),
            'is_translator': False,
            'notifications': False,
            'statuses_count': fake.random_int(min=0, max=1000),
            'default_profile': True,
            'followers_count': fake.random_int(min=0, max=100),
            'translator_type': 'none',
            'favourites_count': fake.random_int(min=0, max=1000),
            'profile_image_url': 'http://pbs.twimg.com/profile_images/985619564925997056/-5532fCc_normal.jpg',
            'profile_link_color': '1DA1F2',
            'profile_text_color': '333333',
            'follow_request_sent': False,
            'contributors_enabled': False,
            'has_extended_profile': False,
            'default_profile_image': False,
            'is_translation_enabled': False,
            'profile_background_tile': False,
            'profile_image_url_https': 'https://pbs.twimg.com/profile_images/985619564925997056/-5532fCc_normal.jpg',
            'profile_background_color': 'F5F8FA',
            'profile_sidebar_fill_color': 'DDEEF6',
            'profile_background_image_url': None,
            'profile_sidebar_border_color': 'C0DEED',
            'profile_use_background_image': True,
            'profile_background_image_url_https': None
        },
        'place': None,
        'id_str': str(statusid),
        'source': '<a href="https://freemedsoft.com" rel="nofollow">doctoctocbot2</a>',
        'entities': {
            'urls': [],
            'symbols': [],
            'hashtags': [{'text': 'doctoctoctest', 'indices': [21, 35]}],
            'user_mentions': [{
                'id': 1230312672,
                'name': 'physician',
                'id_str': '1230312672',
                'indices': [3, 19],
                'screen_name': 'HeliosRaspberry'
            }]
        },
        'favorited': False,
        'full_text': f"{hashtag_string} {fake.text(max_nb_chars=max_text_length)}",
        'retweeted': False, # if True, we must add retweeted_status
        'truncated': False,
        'created_at': status_dt_str,
        'coordinates': None,
        'contributors': None,
        'retweet_count': 1,
        'favorite_count': 0,
        'is_quote_status': False,
        'display_text_range': [0, 140],
        'in_reply_to_user_id': None,
        'in_reply_to_status_id': None,
        'in_reply_to_screen_name': None,
        'in_reply_to_user_id_str': None,
        'in_reply_to_status_id_str': None
    }
    #[{'text': 'doctoctoctest', 'indices': [21, 35]}]
    e_h = []
    for hashtag in hashtag_list:
        idx_start = tweet_object["full_text"].find(f"#{hashtag}")
        idx_end = idx_start + len(hashtag) + 1
        e_h.append({'text': hashtag, 'indices': [idx_start, idx_end]})
    tweet_object["entities"]["hashtags"]= e_h
    return tweet_object