import cherrypy
import os
import logging
from mako import exceptions
from mako.lookup import TemplateLookup
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


class Root(Parent):
    """service mounted on /
    currently renders nothing, will be landing page
    """
    exposed = True

    def __init__(self):
        """initializes class variables"""
        self.login = Login(lookup)
        self.logout = Logout(lookup)
        self.session = app.settings.SESSION_KEY
        self.gene = Gene(lookup)
        self.search = Search(lookup)

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


class Gene(Parent):
    def GET(self, id=None, **kwargs):
        """
        responds to GET requests. Determines if 
        human or mouse gene requested
        Args:
            id: (string) gene id
        Returns:
            HTTPRedirect
        """
        logger.info('/gene GET request id: %s' % str(id))
        logger.info('GET kwargs: %s' % kwargs)
        logger.info('cherrypy session %s' % super().getSession())

        if 'ENSMUSG' in id:
            raise cherrypy.HTTPRedirect('/mouse/gene?id=%s' % id)
        elif 'ENSG' in id:
            raise cherrypy.HTTPRedirect('/human/gene?id=%s' % id)


class Search(Parent):
    """handles search functionality
    mounted on /mouse/search
    """

    def GET(self, **kwargs):
        """responds to data GET requests
        Args:
            query (str): query string for database
        Returns:
            str: table.html
        """
        logger.info('/data GET request')
        logger.debug('GET kwargs: %s' % kwargs)
        # logger.debug('global test %s' % app.settings.Settings.test)

        if 'query' in kwargs:
            query = kwargs['query']
            data = self.pipe.textSearch(query)

            kwargs = {'Title': 'Mouse Expression Table',
                      'data': data,
                      'columnNames': app.settings.getColumnNames('mouse'),
                      'sidebar': False,
                      'query': query}
            kwargs = self.mako_args(kwargs)

        tmpl = self.lookup.get_template("table.html")

        logger.debug('kwargs sent to mako for data table: %s' %
            pprint.pformat(kwargs))
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()


class Login(Parent):
    """service mounted on /login and
    login authentication manager
    """
    exposed = True

    def GET(self, **kwargs):
        """responds to GET requests
        Args:
            ref: (string) url to return to after successful login
        Returns:
            html: login.html
        """
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
        """responds to GET requests
        Args:
            id: (int) mysql row id number of gene
        Returns:
            html: gene.html with gene information and graphs
                rendered
        """
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
        """authenticates user and adds to session
        Args:
            user: (string) username
            _pass: (string) password, would have used pass but
                thats a reserved keyword
        Returns:
            boolean: True if authentication was successful
        """
        if _pipe.auth.auth(user, _pass):
            cherrypy.session[app.settings.SESSION_KEY] = user
            return {'success': True}
        else:
            # _pipe.auth.register(user, password)
            return {'success': False, 'invalid': 'Invalid Username or Password'}

    def register(self, user, _pass, _pass2, email, **kwargs):
        """
        Registers a user in the database. New user does not get
            privileges to private data, those must be granted manually
        Args:
            user: (string) username
            _pass: (string) password
            _pass2: (string) make sure user entered matching passwords
            email: (string) email so sysadmin has a reference for each user
        Returns:
            boolean: True if successful
        """
        if _pass != _pass2:
            return {'success': False, 'invalid': 'Passwords must match'}

        logger.debug('username %s email %s' % (user, email))
        if _pipe.auth.register(user, _pass, email):
            cherrypy.session[app.settings.SESSION_KEY] = user
            return {'success': True}
        else:
            return {'success': False, 'invalid': 'Username already exists'}


class Logout(Parent):
    """service mounted on /logout. Manages a user logout"""
    exposed = True

    def GET(self, **kwargs):
        """responds to GET requests
        Args:
            ref: (string) url to return to after successful login
        Returns:
            redirect to ref
        """
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
cherrypy.tree.mount(Root(), '/', config='%s/conf/root.conf' % path)
# attaches config files to each webapp
for item in [v[1] for v in cherrypy.tree.apps.items()]:
    item.merge('%s/conf/apps.conf' % path)
    item.merge({'/': {'tools.sessions.storage_path': '%s/session' % path}})


def application(environ, start_response):
    """passes application to wsgi"""
    return cherrypy.tree(environ, start_response)
