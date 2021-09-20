from django.core.management.base import BaseCommand, CommandError
import time
from conversation.tasks import handle_retweeted_by
from conversation.models import Tweetdj
from moderation.social import get_socialuser_from_screen_name

current_time = int(time.time())

class Command(BaseCommand):
    help = 'Update retweeted_by'

    def add_arguments(self, parser):
        parser.add_argument('screen_name', type=str)
        parser.add_argument('--batch', '-b', type=int)
        
    def handle(self, *args, **options):
        screen_name = options["screen_name"]
        su = get_socialuser_from_screen_name(screen_name)
        if not su:
            self.stdout.write(
                self.style.ERROR(
                    'No SocialUser found for {}'.format(screen_name)
                )
            )
            return
        batch = options['batch'] or 1000
        added=0
        qs = Tweetdj.objects.filter(
            retweetedstatus=True,
            json__isnull=False,
            socialuser=su,
        ).order_by('statusid')
        count = qs.count()
        self.stdout.write(
            self.style.WARNING(
                    'Tweetdj objects found: {}'.format(count)
            )
        )
        for i in range(0, count, batch):
            for status in qs[i:i+batch]:
                try:
                    rt_statusid = status.json["retweeted_status"]["id"]
                except KeyError:
                    continue
                try:
                    rt_userid = status.json["retweeted_status"]["user"]["id"]
                except KeyError:
                    continue
                handle_retweeted_by(
                    rt_statusid = rt_statusid,
                    rt_userid = rt_userid,
                    by_socialuserid = status.socialuser.id,
                )
                added+=1
                self.stdout.write(
                    self.style.SUCCESS('{} rt_by added...'.format(added))
                )
        self.stdout.write(
            self.style.SUCCESS('Done. {} rt_by added'.format(added))
        )