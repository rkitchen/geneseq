import json
import logging
from app import mongo_pipe as pipe
import app.settings

logger = logging.getLogger(__name__)


class Parent(object):
    """
    Parent class for webapp classes. Provides common functions
    """
    exposed = True

    def __init__(self, lookup):
        """
        initializes class variables pipe, session, and mako lookup
        Args
            lookup: (mako.TemplateLookup)
        """
        self.lookup = lookup
        self.pipe = pipe.Pipe()
        self.session = app.settings.SESSION_KEY

    def fixInput(self, kwargs):
        """
        fixes data passed to webapp through POST JSON
        Args:
            kwargs: (dict) key/value pairs to be processed
        Returns:
            dict: processed key/value pairs
        """
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
        """
        gets user's cherrypy session value of SESSION_KEY
        Returns:
            cherrypy.session
        """
        session = app.settings.cherrypy.session.get(self.session)
        return session

    def isLoggedIn(self):
        """
        checks if user is logged in
        Returns:
            boolean: true if logged in
        """
        session = self.getSession()
        if session is not None:
            return True
        return False

    def isSuper(self):
        """
        checks if user has access to protected data
        Returns:
            boolean: true if has access
        """
        user = self.getSession()
        return self.pipe.auth.isSuper(user)

    def url(self):
        """
        Gets current url from cherrypy
        Returns:
            string: current url
        """
        return app.settings.cherrypy.url()

    def mako_args(self, kwargs):
        """
        ensures common variables required by mako are set
        Args:
            kwargs: (dict) kwargs for mako_args
        Returns:
            kwargs: (dict) kwargs for mako_args
        """
        kwargs['login'] = self.isLoggedIn()
        kwargs['url'] = self.url()
        return kwargs
