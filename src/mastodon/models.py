from django.db import models


class MastodonInvitation(models.Model):
    uid = models.CharField(
        max_length=8,
        unique=True
    )
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    autofollow = models.ForeignKey(
        'moderation.MastodonUser',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    
    def __str__(self):
        return (
            f'MastodonInvitation {self.uid} {self.socialuser} '
            f'{self.autofollow}'
        )


    class Meta:
        unique_together = [['uid', 'socialuser']]