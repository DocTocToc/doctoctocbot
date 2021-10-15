from moderation.dm import CommunityProcessor
from community.models import Community
    
def poll_moderation_dm():
    for community in Community.objects.filter(active=True):
        cp = CommunityProcessor(community)
        cp.process()