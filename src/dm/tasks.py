from dm.retrieve import savedm
from doctocnet.celery import app


@app.task
def directmessages():
    savedm()