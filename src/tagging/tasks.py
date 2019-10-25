from tagging.models import Process, Queue
from dm.api import senddm

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

def quickreply(process_id):
    qr = {
           "type": "options",
           "options": []
          }
    options = []
    option = {
                "label": "?",
                "description": "?",
                "metadata": "?"
             }
    
    try:
        moderation_instance=Moderation.objects.get(id=moderation_instance_id)
    except Moderation.DoesNotExist:
        return
    community=moderation_instance.queue.community
    for ccr in CommunityCategoryRelationship.objects.filter(
        quickreply=True,
        community=community
        ):
        logger.debug(f"Category name: {ccr.category.name}")
        opt = dict(option)
        opt["label"] = ccr.category.label
        opt["metadata"] = f"moderation{moderation_instance_id}{ccr.category.name}"
        opt["description"] = ccr.category.description or ccr.category.label
        options.append(opt)

    qr["options"] = options
    logger.debug(f"qr: {qr}")
    return qr

@shared_task(bind=True)
def send_tag_dm(self, process_id):
    process_mi = Process.objects.get(pk=process_id)
    qr = quickreply(process_id)
    logger.info(f"process_mi.processor.user_id: {process_mi.processor.user_id}")
    process_mi.refresh_from_db()
    logger.info(f"mod_mi.queue.user_id {mod_mi.queue.user_id}")
    handle_create_update_profile.apply_async(args=(mod_mi.queue.user_id,))
    sn = screen_name(mod_mi.queue.status_id)
    status_id = mod_mi.queue.status_id
    dm_txt = (_("Please moderate this user: @{screen_name} "
              "Tweet: https://twitter.com/{screen_name}/status/{status_id}")
              .format(screen_name=sn, status_id=status_id))

    logger.info(ok)
    if not ok:
        self.retry(countdown= 2 ** self.request.retries)
    ok = senddm(dm_txt,
           user_id=mod_mi.moderator.user_id,
           screen_name=mod_mi.queue.community.account.username,
           return_json=True,
           quick_reply=qr)
    logger.info(ok)
    if not ok:
        self.retry(countdown= 2 ** self.request.retries)