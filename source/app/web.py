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
import json

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
class Root(Parent):
    """service mounted on /
    currently renders nothing, will be landing page
    """
    exposed = True

    def __init__(self):
        self.login = Login(lookup)
        self.logout = Logout(lookup)
        self.session = app.settings.SESSION_KEY

    def GET(self, **kwargs):
        logger.info('/ GET request')
        logger.debug('GET kwargs: %s' % str(kwargs))
        logger.debug('session %s' % cherrypy.session.get(app.settings.SESSION_KEY))
        kwargs['Title'] = 'Home'
        kwargs = self.mako_args(kwargs)
        tmpl = lookup.get_template("index.html")
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()


class Login(Parent):
    exposed = True

    def GET(self, **kwargs):
        logger.info('/ GET request')
        logger.debug('GET kwargs: %s' % str(kwargs))
        kwargs['Title'] = 'Login'
        if 'ref' not in kwargs:
            kwargs['ref'] = '/'
        kwargs = self.mako_args(kwargs)
        tmpl = lookup.get_template("login.html")
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()

    def POST(self, **kwargs):
        logger.info('/login POST request')
        logger.debug('POST kwargs: %s' % str(kwargs))

        if 'method' in kwargs:
            if kwargs['method'] == 'login':
                if set(['user', '_pass']).issubset(kwargs):
                    ret = self.login(**kwargs)
                    return json.dumps(ret)

            elif kwargs['method'] == 'register':
                if set(['user', '_pass', '_pass2', 'email']).issubset(kwargs):
                    ret = self.register(**kwargs)
                    return json.dumps(ret)
        return json.dumps({'success': False})

    def login(self, user, _pass, **kwargs):
        if _pipe.auth.auth(user, _pass):
            cherrypy.session[app.settings.SESSION_KEY] = user
            return {'success': True}
        else:
            # _pipe.auth.register(user, password)
            return {'success': False, 'invalid': 'Invalid Username or Password'}

    def register(self, user, _pass, _pass2, email, **kwargs):
        if _pass != _pass2:
            return {'success': False, 'invalid': 'Passwords must match'}

        logger.debug('username %s email %s' % (user, email))
        if _pipe.auth.register(user, _pass, email):
            cherrypy.session[app.settings.SESSION_KEY] = user
            return {'success': True}
        else:
            return {'success': False, 'invalid': 'Username already exists'}


class Logout(Parent):
    exposed = True

    def GET(self, **kwargs):
        cherrypy.session[app.settings.SESSION_KEY] = None
        logger.debug('logged out, session now %s' % cherrypy.session.get(app.settings.SESSION_KEY))
        if 'ref' not in kwargs:
            kwargs['ref'] = '/'
        raise cherrypy.HTTPRedirect(kwargs['ref'])


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
    item.merge({'/': {'tools.sessions.storage_path': '%s/session' % path}})


def application(environ, start_response):
    """passes application to wsgi"""
    return cherrypy.tree(environ, start_response)
