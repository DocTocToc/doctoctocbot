from django.db import models

class UserActive(models.Model):
    active = models.BooleanField(
        default=True,
        help_text=(
            "Is this Twitter SocialUser active? For Twitter, not active means "
            "deactivated or deleted."
        )
    )
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        related_name='active',
        on_delete=models.CASCADE
    )
    created =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Active: {self.active} '
            f'{self.socialuser.user_id} '
            f'{self.created.strftime("%Y-%m-%dT%H:%M:%S")}'
        )

    