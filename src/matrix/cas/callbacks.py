from constance import config

def matrix_attributes(user, service):
    """Return all available user name related fields and methods."""
    required_attribute_key = config.matrix__cas__callbacks__attribute_key
    required_attribute_value = config.matrix__cas__callbacks__attribute_value
    attributes = {}
    attributes['username'] = user.get_username()
    attributes['name'] = user.get_username()
    attributes[required_attribute_key] = required_attribute_value
    #attributes['full_name'] = user.get_full_name()
    #attributes['short_name'] = user.get_short_name()
    return attributes