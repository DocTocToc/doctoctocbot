import logging
from doctocnet.celery import app

logger = logging.getLogger(__name__)

@app.task
def handle_normalize(statusid):
    from .utils import normalize
    normalize(statusid)
    
@app.task
def handle_allnormalize():
    from .utils import allnormalize
    allnormalize()
    

        