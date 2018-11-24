from doctocnet.celery import app
from dm.retrieve import savedm

@app.task
def directmessages():
    savedm()