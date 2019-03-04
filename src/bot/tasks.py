from doctocnet.celery import app

@app.task
def handle_retweetroot(statusid: int):
    from .bin.thread import retweetroot
    retweetroot(statusid)
    
@app.task(bind=True)
def handle_question(self, statusid: int):
    from .bin.thread import question
    ok = question(statusid) 
    if not ok:
        self.retry(args=(statusid,), countdown=15, max_retries=20 )
        
@app.task
def handle_on_status(statusid: int):
    from .onstatus import triage
    triage(statusid)
    
@app.task
def handle_retweet(statusid: int):
    from bot.doctoctocbot import retweet
    retweet(statusid)