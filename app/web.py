import cherrypy
import os
import logging
from mako import exceptions
from mako.lookup import TemplateLookup
from app.data import Charts
import app.mouse
import app.human
import app.mysql_pipe
import app.mongo_pipe
import app.settings
import pprint

logger = logging.getLogger(__name__)
app.settings.init()
_pipe = app.mongo_pipe.Pipe()

path = os.path.dirname(os.path.realpath(__file__))
logger.debug('path: %s ' % path)
lookup = TemplateLookup(directories=['%s/html' % path])

celltypes = _pipe.mouse.getCellTypes()
app.settings.setCellTypes('mouse', celltypes)


class Parent(object):
    """parent class for the webapp classes. attaches pipe
    to each object"""
    def __init__(self):
        pass


# service mounted on /
# currently renders nothing, eventually some kind of landing page
class Root(Parent):
    """service mounted on /
    currently renders nothing, will be landing page
    """
    exposed = True

    def GET(self, **kwargs):
        logger.info('/ GET request')
        logger.debug('GET kwargs: %s' % str(kwargs))
        kwargs['Title'] = 'Home'
        tmpl = lookup.get_template("index.html")
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()


class Search(Parent):
    """handles search functionality
    mounted on /search
    """
    exposed = True

    def GET(self, query=None, **kwargs):
        """responds to GET requests
        Args:
            query: (str) search query
        Returns
            html: search.html
        """
        logger.info('/search GET request')
        logger.debug('GET query: %s\n\t\tkwargs: %s' % (query, kwargs))
        tmpl = lookup.get_template("search.html")
        kwargs['Title'] = 'Search'
        # TODO create proper search functionality
        if query is not None:
            kwargs['geneID'] = _pipe.search_like(query)[0]
        return tmpl.render(**kwargs)

# mounts all webapps to cherrypy tree
cherrypy.config.update({'tools.staticdir.root': path})
# cherrypy.config.update('%s/conf/global.conf' % path)
cherrypy.tree.mount(app.mouse.Mouse(lookup), '/mouse', config='%s/conf/gene.conf' % path)
cherrypy.tree.mount(app.human.Human(lookup), '/human', config='%s/conf/gene.conf' % path)
cherrypy.tree.mount(Charts(), '/data', config='%s/conf/data.conf' % path)
cherrypy.tree.mount(Search(), '/search', config='%s/conf/search.conf' % path)
cherrypy.tree.mount(Root(), '/', config='%s/conf/root.conf' % path)
# attaches config files to each webapp
for item in [v[1] for v in cherrypy.tree.apps.items()]:
    item.merge('%s/conf/apps.conf' % path)


def application(environ, start_response):
    """passes application to wsgi"""
    return cherrypy.tree(environ, start_response)

