def status_json_log(json):
    return (
        f"Id: {json['id']}; "
        f"Created_at: {json['created_at']}; "
        f"Screen_name: {json['user']['screen_name']}; "
        f"Text: {json['text']} \n")