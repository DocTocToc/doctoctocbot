from doctocnet.celery import app


@app.task
def handle_retweetroot(statusid: int):
    from .bin.traverseroot import retweetroot
    retweetroot(statusid)