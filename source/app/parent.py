import json
import logging
from app import mongo_pipe as pipe
import app.settings

logger = logging.getLogger(__name__)


class Parent(object):
    exposed = True

    def __init__(self, lookup):
        self.lookup = lookup
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
            else:
                try:
                    tmp = int(v)
                    kwargs[k] = tmp
                except ValueError:
                    pass
        return kwargs

    def getSession(self):
        session = app.settings.cherrypy.session.get(self.session)
        return session

    def isLoggedIn(self):
        session = self.getSession()
        if session is not None:
            return True
        return False

    def isSuper(self):
        user = self.getSession()
        return self.pipe.auth.isSuper(user)

    def url(self):
        return app.settings.cherrypy.url()

    def mako_args(self, kwargs):
        kwargs['login'] = self.isLoggedIn()
        kwargs['url'] = self.url()
        return kwargs


class MouseParent(Parent):
    exposed = True

    def __init__(self, mouse):
        self.lookup = mouse.lookup
        self.pipe = pipe.Pipe()
        self.session = app.settings.SESSION_KEY

    # def fixInput(self, kwargs):
    #     for k, v in kwargs.items():
    #         if '[' in v and ']' in v:
    #             kwargs[k] = v[1:-1].split(',')
    #             for i, number in enumerate(kwargs[k]):
    #                 try:
    #                     kwargs[k][i] = int(number)
    #                 except (ValueError):
    #                     pass
    #         elif v == 'true' or v == 'false':
    #             kwargs[k] = json.loads(v)
    #     return kwargs
