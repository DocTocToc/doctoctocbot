from model.model import Status, session
from datetime import datetime
from conf.cfg import getConfig
import requests

class addstatus:
    def __init__(self, json):
        self.json = json

    def addstatus(self):
        status = Status(id = self.id(),
                        userid = self.userid(),
                        json = self.json,
                        datetime = self.datetime())
        session.add(status)
        session.commit()
        if self.has_image():
            self.add_image()
        return True

    def datetime(self):
        """ Returns the UTC creation datetime of the status as a Python object.

        "created_at":"Thu Apr 06 15:24:15 +0000 2017"
        
        """
        datetime_string = self.json["created_at"]
        return datetime.strptime(datetime_string, "%a %b %d %H:%M:%S +0000 %Y")
    
    def userid(self):
        return self.json["user"]["id"]

    def id(self):
        return self.json["id"]
   
    def has_image(self):
        """ returns True if the status contains at least one image."""
        if "extended_entities" not in self.json:
            return False
        elif self.json["extended_entities"]["media"][0]["type"] == "photo":
            return True
        else:
            return False

    def add_image(self):
        """ Stores one or more images contained in the status.
        """
        for photo in self.json["extended_entities"]["media"]: 
            url = photo["media_url_https"]
            filename = url.rsplit('/', 1)[1]
            filepath = getConfig()["images"]["dir"] + filename
            r = requests.get(url, allow_redirects=True)
            open(filepath, 'wb').write(r.content)
