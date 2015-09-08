import cherrypy
import os
import json
import logging
from mako import exceptions
from mako.lookup import TemplateLookup
import app.pipe
import app.settings

logger = logging.getLogger(__name__)
_settings = app.settings.Settings()
_pipe = app.pipe.Pipe(_settings)

path = os.path.dirname(os.path.realpath(__file__))
logger.debug('path: %s ' % path)
lookup = TemplateLookup(directories=['%s/html' % path])


class Parent(object):
    """parent class for the webapp classes. attaches pipe
    to each object"""
    def __init__(self):
        super().__init__()


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


# service mounted on /data
# renders interactive data table
class Data(Parent):
    """displays mysql data in a table
    mounted on /data and /table"""
    exposed = True

    def fixSliderInit(self, kwargs):
        """changes slider init to string for slider jquery

        Returns:
            dict: sliders
        """
        sliders = _settings.getTableSliders()
        for slider in sliders:
            init = slider['init']
            logger.debug('init object: %s type %s' % (init, type(init)))
            # checks if slider initial values were passed
            # in kwargs
            column = slider['column']
            if column in kwargs:
                value = json.loads(kwargs[column])
                init = value
            logger.debug('slider %s init %s' % (column, init))

            slider['init'] = str(init)
        logger.debug(sliders)
        logger.debug(_settings.getTableSliders())
        return sliders

    def getTable(self, **kwargs):
        """gets data from database

        Args:
            kwargs: (dict) same as for builQuery()
        Returns:
            dict: data from database
        """
        return _pipe.getDataTable(**kwargs)

    def serializeJSON(self, data):
        """changes Decimal() types to str for json
        Args:
            data: (dict)
        Returns:
            dict: data with Decimal() replaced
        """
        # TODO search for all unserializable
        # objects rather than specific
        for item in data:
            item['expr'] = str(item['expr'])
            item['expr_next'] = str(item['expr_next'])

        return data

    def GET(self, order='expr', **kwargs):
        """responds to data GET requests
        Args:
            None yet
        Returns:
            str: table.html
        """
        logger.info('/data GET request')
        logger.debug('GET kwargs: %s' % kwargs)
        data = {'Title': 'Data',
                'data': self.getTable(),
                'sliders': self.fixSliderInit(kwargs),
                'columnNames': _settings.getColumnNames(),
                'order': order}
        tmpl = lookup.get_template("table.html")
        logger.debug('kwargs sent to mako for data table: %s' % data)
        try:
            return tmpl.render(**data)
        except:
            return exceptions.html_error_template().render()

    def POST(self, method='data_table', **kwargs):
        """responds to POST requests, currently has two
        methods. data_table returns
        Args:
            direction: (bool,str)
                bool: True = ASC, False = DESC
                str: ASC/DESC
            sliders: (bool) true if sliders present in kwargs
            <SLIDER_NAME>[]: {'min', 'max'} dictionary containing
                             min/max from range sliders
            limit: (int) limits number of rows returned in table
        Returns:
            JSON: table rows serialized in json
        """
        logger.info('/data POST request')
        logger.debug('POST kwargs: %s' % str(kwargs))
        if 'sliders' in kwargs and kwargs['sliders'] == 'true':
            logger.info('found sliers in POST')
            ranges = dict()
            for slider in self.fixSliderInit(dict()):
                if slider['column'] in kwargs:
                    key = slider['column']
                    slider_data = json.loads(kwargs.pop(key))
                    if type(slider_data) is not list:
                        continue
                    translated = _settings.translate(key)
                    ranges[translated] = {'min': slider_data[0],
                                          'max': slider_data[1]}

            kwargs['ranges'] = ranges
        if 'direction' in kwargs:
            logger.info('found direction in POST')
            if kwargs['direction'] == 'true':
                kwargs['direction'] = True
            elif kwargs['direction'] == 'false':
                kwargs['direction'] = False
        new_data = _pipe.getDataTable(**kwargs)
        return json.dumps(self.serializeJSON(new_data))


class Gene(Parent):
    """webapp handling requests for specific genes
    mounted on /gene
    """
    exposed = True

    def GET(self, id=None, **kwargs):
        """responds to GET requests
        Args:
            id: (int) mysql row id number of gene
        Returns:
            html: gene.html with gene information and graphs
                rendered
        """
        logger.info('/gene GET request id: %s' % str(id))
        logger.debug('GET kwargs: %s' % kwargs)
        if id is None:
            return 'No id given'
        else:
            if not isinstance(id, int):
                try:
                    id = int(id)
                except ValueError as e:
                    print(e)
                    # TODO return proper error message
                    return 'invalid id given'
            tmpl = lookup.get_template("data.html")
            data = _pipe.getGene(id)
            data['Title'] = data['geneName']
            try:
                return tmpl.render(**data)
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
# cherrypy.config.update('%s/global.conf' % path)
cherrypy.tree.mount(Gene(), '/gene', config='%s/gene.conf' % path)
cherrypy.tree.mount(Data(), '/data', config='%s/data.conf' % path)
cherrypy.tree.mount(Data(), '/table', config='%s/data.conf' % path)
cherrypy.tree.mount(Search(), '/search', config='%s/search.conf' % path)
cherrypy.tree.mount(Root(), '/', config='%s/root.conf' % path)
# attaches config files to each webapp
for item in [v[1] for v in cherrypy.tree.apps.items()]:
    item.merge('%s/apps.conf' % path)


def application(environ, start_response):
    """passes application to wsgi"""
    return cherrypy.tree(environ, start_response)
