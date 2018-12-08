from doctocnet.celery import app


@app.task
def handle_retweetroot(statusid: int):
    from .bin.thread import retweetroot
    retweetroot(statusid)