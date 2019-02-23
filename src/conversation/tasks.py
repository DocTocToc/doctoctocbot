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

@app.task
def handle_update_trees(hourdelta):
    from .utils import update_trees
    update_trees(hourdelta)

        