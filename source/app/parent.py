import json
import logging
from app import mongo_pipe as pipe
import app.settings

logger = logging.getLogger(__name__)


class MouseParent(object):
    exposed = True

    def __init__(self, mouse):
        self.lookup = mouse.lookup
        self.pipe = pipe.Pipe()
        self.session = app.settings.SESSION_KEY

    def fixInput(self, kwargs):
        for k, v in kwargs.items():
            if '[' in v and ']' in v:
                kwargs[k] = v[1:-1].split(',')
                for i, number in enumerate(kwargs[k]):
                    try:
                        kwargs[k][i] = int(number)
                    except (ValueError):
                        pass
            elif v == 'true' or v == 'false':
                kwargs[k] = json.loads(v)
        return kwargs


class Parent(object):
    exposed = True

    def __init__(self, lookup):
        self.lookup = lookup
        self.pipe = pipe.Pipe()

    def fixInput(self, kwargs):
        for k, v in kwargs.items():
            if '[' in v and ']' in v:
                kwargs[k] = v[1:-1].split(',')
                for i, number in enumerate(kwargs[k]):
                    try:
                        kwargs[k][i] = int(number)
                    except (ValueError):
                        pass
            elif v == 'true' or v == 'false':
                kwargs[k] = json.loads(v)
        return kwargs
