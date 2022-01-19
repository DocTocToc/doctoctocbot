import logging
from typing import List
from django.core.management.base import BaseCommand, CommandError
from hcp.models import Taxonomy, HealthCareProvider
from moderation.models import Follower
from moderation.social import get_socialuser

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = (
        'Return a list of Twitter screen_name(s) that belong to given '
        'specialty taxonomy'
    )
    def add_arguments(self, parser):
        parser.add_argument(
            'taxonomy',
            type=int
        )
        parser.add_argument(
            '-f',
            '--friend',
            type=str,
            help='Must have this screen_name as friend'
        )

    def handle(self, *args, **options):
        taxonomy_pk = options['taxonomy']
        logger.debug(f"{type(taxonomy_pk)=}")
        friend = options['friend']
        
        try:
            taxonomy = Taxonomy.objects.get(pk=taxonomy_pk)
        except Taxonomy.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    'No Taxonomy object with pk = "%s"' % taxonomy_pk
                )
            )
            return
        hcp_qs = HealthCareProvider.objects.filter(taxonomy=taxonomy)
        if not hcp_qs:
            self.stdout.write(
                self.style.ERROR(
                    'No healthcare providers belonging to %s' % taxonomy
                )
            )
            return
        su_lst = []
        for hcp in hcp_qs:
            su = hcp.human.socialuser.filter(active=True).last()
            su_lst.append(su)
        su_lst = list(filter(None, su_lst))
        if not friend:
            screen_name_lst = [
                su.screen_name_tag() for su in su_lst if su.screen_name_tag()
            ]
            result = (
                f"Taxonomy: {taxonomy.code} | {taxonomy.classification_en} "
                f"{taxonomy.specialization_en} "
                "\n"
                f"{len(screen_name_lst)} "
                f"user{'s' if len(screen_name_lst)>1 else ''} "
                "\n"
                f"{' '.join(screen_name_lst)}"
            )
        else:
            friend_su = get_socialuser(friend)
            try:
                follower_mi = Follower.objects.filter(user=friend_su).latest()
            except Follower.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        'No Follower object found for %s' % friend_su
                    )
                )
                return
            su_friend_lst = []
            su_nofriend_lst = []
            for su in su_lst:
                if su.user_id in follower_mi.id_list:
                    su_friend_lst.append(su)
                else:
                    su_nofriend_lst.append(su)
            f_sn_lst = [f'@{su.screen_name_tag()}' for su in su_friend_lst if su.screen_name_tag()]
            nof_sn_lst = [f'@{su.screen_name_tag()}' for su in su_nofriend_lst if su.screen_name_tag()]
            f_count = len(f_sn_lst)
            nof_count = len(nof_sn_lst)
            result = (
                f"Taxonomy: {taxonomy.code} | {taxonomy.classification_en} "
                f"{taxonomy.specialization_en} "
                "\n"
                f"Follower{'s' if f_count>1 else ''} of @{friend}: "
                "\n"
                f"{f_count} user{'s' if f_count>1 else ''} "
                "\n"
                f"{' '.join(f_sn_lst)} "
                "\n"
                f"NOT follower{'s' if nof_count>1 else ''} of @{friend}: "
                "\n"
                f"{nof_count} user{'s' if nof_count>1 else ''} "
                "\n"
                f"{' '.join(nof_sn_lst)}"
            )
        self.stdout.write(self.style.SUCCESS(result))