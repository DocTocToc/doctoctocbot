from datetime import datetime
from bot.tweepy_api import get_api_2
import mytweepy

from django.core.management.base import  BaseCommand, CommandError

from conversation.tree.descendant import tree_search_crawl


def display_tweet(tweet):
    data=tweet.data
    text=(
        "Tweet:\n"
        f"id: {data.id}\n"
        f"text: {data.text}"
    )
    try:
        text+=(f"\nconversation_id: {data.conversation_id}")
    except:
        pass
    return text

class Command(BaseCommand):
    help = 'Find all tweets belonging to the same conversation'
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        parser.add_argument('t_id', type=int)

    def handle(self, *args, **options):
        username = options["username"]
        t_id = options["t_id"]
        client = get_api_2(username)
        tweet= client.get_tweet(
            t_id,
            tweet_fields=['conversation_id',]
        )
        self.stdout.write(
            self.style.NOTICE(
                f'{display_tweet(tweet)}\n\n'
            )
        )
        responses = []
        for response in mytweepy.Paginator(
            client.search_recent_tweets,
            query = f'conversation_id:{tweet.data.conversation_id}',
            tweet_fields=['referenced_tweets',]
        ).flatten():  
            responses.append(response)
        print(f'Count: {len(responses)}\n\n')
        for idx, tweet in enumerate(responses):
            self.stdout.write(
            self.style.NOTICE(
                f'{idx}\n{tweet["id"]}\n{tweet["text"]}\n{tweet["referenced_tweets"]}\n\n'
            )
        )
            
        """
        self.stdout.write(
            self.style.ERROR(
                f"tree_search_crawl('{community_name}', days={days}) "
                f"management command stopped at {datetime.utcnow()}."
            )
        )
        """