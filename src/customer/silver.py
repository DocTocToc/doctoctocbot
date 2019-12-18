from django.conf import settings

def get_protocol():
    if settings.DEBUG:
        return "http://"
    else:
        return "https://"
    
def get_headers():
    assert settings.SILVER_TOKEN, "To use Silver, you must set SILVER_TOKEN in your .env file."
    authorization = f"Token {settings.SILVER_TOKEN}"
    return {
        'content-type': 'application/json',
        'Authorization': authorization,    
    }

def get_api_endpoint(endpoint: str, _id=None):
    if _id is None:
        _id = ""
    else:
        _id = f"{_id}/"
    return f"{get_protocol()}{settings.SILVER_URL}/{endpoint}/{_id}"
