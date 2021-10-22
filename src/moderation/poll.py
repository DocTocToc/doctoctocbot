from moderation.dm import CommunityProcessor
from community.models import Community


def poll_moderation_dm(community):
    try:
        community_mi = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    cp = CommunityProcessor(community_mi)
    cp.process()