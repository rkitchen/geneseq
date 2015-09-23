import cherrypy
import os
import logging
from mako import exceptions
from mako.lookup import TemplateLookup
from app.data import Charts
import app.mouse
import app.human
from app.parent import Parent
import app.mongo_pipe
import app.settings
import pprint

logger = logging.getLogger(__name__)
app.settings.init(cherrypy)
_pipe = app.mongo_pipe.Pipe()

path = os.path.dirname(os.path.realpath(__file__))
logger.debug('path: %s ' % path)
lookup = TemplateLookup(directories=['%s/html' % path])

celltypes = _pipe.mouse.getCellTypes()
app.settings.setCellTypes('mouse', celltypes)


# service mounted on /
# currently renders nothing, eventually some kind of landing page
class Root(object):
    """service mounted on /
    currently renders nothing, will be landing page
    """
    exposed = True

    def __init__(self):
        self.login = Login()
        self.logout = Logout()

    def GET(self, **kwargs):
        logger.info('/ GET request')
        logger.debug('GET kwargs: %s' % str(kwargs))
        logger.debug('session %s' % cherrypy.session.get(app.settings.SESSION_KEY))
        kwargs['Title'] = 'Home'
        tmpl = lookup.get_template("index.html")
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()


class Login(object):
    exposed = True

    def GET(self, **kwargs):
        logger.info('/ GET request')
        logger.debug('GET kwargs: %s' % str(kwargs))
        kwargs['Title'] = 'Login'
        tmpl = lookup.get_template("login.html")
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()

    def POST(self, **kwargs):
        if 'user' in kwargs and 'pass' in kwargs:
            self.login(kwargs['user'], kwargs['pass'])
        return 'success'

    def login(self, user, password):
        if _pipe.auth.auth(user, password):
            cherrypy.session[app.settings.SESSION_KEY] = user
        else:
            _pipe.auth.register(user, password)
            # self.login(user, password)


class Logout(object):
    exposed = True

    def GET(self, **kwargs):
        cherrypy.session[app.settings.SESSION_KEY] = None
        logger.debug('logged out, session now %s' % cherrypy.session.get(app.settings.SESSION_KEY))


# mounts all webapps to cherrypy tree
cherrypy.config.update({'tools.staticdir.root': path})
cherrypy.config.update('%s/conf/global.conf' % path)
cherrypy.tree.mount(app.mouse.Mouse(lookup), '/mouse', config='%s/conf/gene.conf' % path)
cherrypy.tree.mount(app.human.Human(lookup), '/human', config='%s/conf/gene.conf' % path)
cherrypy.tree.mount(Charts(), '/data', config='%s/conf/data.conf' % path)
# cherrypy.tree.mount(Search(lookup), '/search', config='%s/conf/search.conf' % path)
cherrypy.tree.mount(Root(), '/', config='%s/conf/root.conf' % path)
# attaches config files to each webapp
for item in [v[1] for v in cherrypy.tree.apps.items()]:
    item.merge('%s/conf/apps.conf' % path)


def application(environ, start_response):
    """passes application to wsgi"""
    return cherrypy.tree(environ, start_response)
