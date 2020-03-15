from django.contrib.auth import get_user_model


def add_email_if_not_exist(backend, details, user, response, *args, **kwargs):
    """
    This function is called in the SOCIAL_AUTH_TWITTER_PIPELINE of social_django app.
    If the email of the user if empty, it will try to get the email from Twitter
    and add it to the user object.
    """
    User = get_user_model()
    email_field = User.get_email_field_name()
    email = getattr(user, email_field, None)
    if email:
        return
    if backend.name == 'twitter':
        twitter_email = details.get("email", None)
        if not twitter_email:
            return   
        setattr(user, email_field, twitter_email)
        user.save()

        