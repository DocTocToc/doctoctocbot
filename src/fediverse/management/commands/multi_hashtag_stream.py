import logging
import threading
import time

from django.core.management import call_command
from django.core.management.base import BaseCommand

from community.models import Community, Reblog

logger = logging.getLogger('__name__')


class CommandRunner(threading.Thread):
    def __init__(self, command, args):
        threading.Thread.__init__(self)
        self.command = command
        self.args = args
        self.stop_command = threading.Event()

    def run(self):
        while not self.stop_command.is_set():
            try:
                call_command(self.command, *self.args)
            except Exception as e:
                logging.error(e)
            time.sleep(1)

    def stop(self):
        self.stop_command.set()


class MultiTask:
    def __init__(self, tasks):
        self.threads = []
        for task, args in tasks:
            self.threads.append(CommandRunner(task, args))

    def start(self):
        for t in self.threads:
            t.start()

    def stop(self):
        for t in self.threads:
            t.stop()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'community',
            nargs='?',
            type=str
        )

    def handle(self, *args, **options):
        community = options["community"]
        if not community:
            return
        try:
            community = Community.objects.get(name=community)
            logger.debug(community)
        except Community.DoesNotExist:
            return
        t = "hashtag_stream"
        tasks = []
        for tag in (
            Reblog.objects
            .filter(community=community, reblog=True)
            .values_list("hashtag__hashtag", flat=True)
        ):
            logger.debug(f'{tag=}')
            tasks.append((t, [tag, f"--community={community}"]))
        logger.debug(tasks)
        if not tasks:
            self.stdout.write(
                self.style.SUCCESS(
                    "No Reblog objects with reblog==True found"
                    f"for Community '{community}'."
                )
            )
            return
        mt = MultiTask(tasks)
        mt.start()