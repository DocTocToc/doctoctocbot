import logging
import threading
import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from constance import config

from community.models import Community

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
        parser.add_argument('--days', type=int)

    def handle(self, *args, **options):
        days = options["days"]
        if not days:
            days = (
                config.conversation__tree__descendant__tree_search_crawl__days
            )
        t = "tree_search"
        tasks = []
        for c in Community.objects.filter(active=True, tree_search=True):
            tasks.append((t, [c.name, f"--days={days}"]))
        logger.debug(tasks)
        if not tasks:
            self.stdout.write(
                self.style.SUCCESS(
                    "No community has activated tree_search. "
                    "No task to process. Returning."
                )
            )
            return
        mt = MultiTask(tasks)
        mt.start()