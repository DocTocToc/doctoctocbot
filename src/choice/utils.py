from constance import config


def room_url(obj):
    homeserver_url =  config.choice_matrix_homeserver_url
    room_url = config.choice_matrix_room_url
    return f"{room_url}{obj.room_alias}:{homeserver_url}"