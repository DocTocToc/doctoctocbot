from doctocnet.celery import app
from bot.bin.timeline import record_timeline

@app.task
def handle_record_timeline():
    record_timeline()