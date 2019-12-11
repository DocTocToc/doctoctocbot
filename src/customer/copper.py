from django.conf import settings

def get_protocol():
    if settings.DEBUG:
        return "http://"
    else:
        return "https://"
    
def get_headers():
    assert settings.COPPER_TOKEN, "To use Copper, you must set COPPER_TOKEN in your .env file."
    authorization = f"Token {settings.COPPER_TOKEN}"
    return {
        'content-type': 'application/json',
        'Authorization': authorization,    
    }

def get_api_endpoint(endpoint: str, _id=None):
    if _id is None:
        _id = ""
    else:
        _id = f"{_id}/"
    return f"{get_protocol()}{settings.COPPER_URL}/{endpoint}/{_id}"
