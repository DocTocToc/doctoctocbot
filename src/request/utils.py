import logging

from request.models import Queue

logger = logging.getLogger(__name__) 

def accept_delete_queue(uid, community):
    state = Queue.ACCEPT
    delete_queue(uid, community, state)
    
def decline_delete_queue(uid, community):
    state = Queue.DECLINE
    delete_queue(uid, community, state)

def delete_queue(uid, community, state):
    for q in Queue.objects.current.filter(uid=uid,community=community):
        q = q.clone()
        q.state = state
        q.save()
        q.delete()