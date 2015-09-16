import json
import logging
from app import mongo_pipe as pipe

logger = logging.getLogger(__name__)


class Parent(object):

    def __init__(self, mouse):
        self.lookup = mouse.lookup
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
