import json
import logging

from mako import exceptions
# from mako.lookup import TemplateLookup
import app.settings
from app.parent import Parent
import pprint

logger = logging.getLogger(__name__)


class Mouse(object):
    """
    container class for objects mounted under /mouse
    """
    def __init__(self, mako):
        self.lookup = mako
        self.session = app.settings.SESSION_KEY

        self.table = Table(mako)
        self.gene = Gene(mako)
        self.chart = Chart(mako)
        self.search = Search(mako)


class Gene(Parent):
    """webapp handling requests for specific genes
    mounted on /gene
    """
    exposed = True

    def GET(self, id=None, **kwargs):
        """responds to GET requests
        Args:
            id: (string) mysql row id number of gene
        Returns:
            html: gene.html with gene information and graphs
                rendered
        """
        logger.info('/gene GET request id: %s' % str(id))
        logger.info('GET kwargs: %s' % kwargs)
        logger.info('cherrypy session %s' % super().getSession())

        settings = app.settings
        pipe = self.pipe
        lookup = self.lookup

        if id is None:
            return 'No id given'
        tmpl = lookup.get_template("gene.html")
        kwargs['Title'] = id
        kwargs = self.mako_args(kwargs)

        gene = pipe.mouse.getGene(id)
        header = list()
        for key, value in gene.items():
            name = settings.translate_readable(key)
            if name == key:
                name = ' '.join(key.split('_')).title()

            item = dict()
            item = (name, key, value)
            header.append(item)
        kwargs['header'] = self.sort(header)
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()

    def sort(self, header):
        """
        sorts details in for header
        Args:
            header: (list(Visual name, variable name)) list of data displayed in header
        """
        order = app.settings.getOrder('mouse')

        ret = sorted(header, key=lambda i: order.index(i[1]))
        logger.debug('sorted mouse header values %s' % ret)
        return ret


class Table(Parent):
    """displays mysql data in a table
    mounted on /mouse/table"""
    exposed = True

    def GET(self, **kwargs):
        """responds to data GET requests
        Args:
            expression: (list(min,max)) constrains expression to bounds
            enrichment: (list(min,max)) constrains enrichment to bounds
            limit: (int) limits number of returned records
            sort: (list(column,direction)) sorts returned records
        Returns:
            html: table.html
        """
        logger.info('/data GET request')
        kwargs = self.fixInput(kwargs)
        logger.debug('GET kwargs: %s' % kwargs)
        # logger.debug('global test %s' % app.settings.Settings.test)
        data = self.pipe.mouse.getTable(**kwargs)

        kwargs = {'Title': 'Mouse Expression Table',
                  'data': data,
                  'filters': self.fixFilters(kwargs),
                  'columnNames': app.settings.getColumnNames('mouse'),
                  'sidebar': True}
        kwargs = self.mako_args(kwargs)

        tmpl = self.lookup.get_template("table.html")

        logger.debug('kwargs sent to mako for data table: %s' %
            pprint.pformat(kwargs))
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()

    def POST(self, **kwargs):
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
        _json = json.loads(kwargs['json'])
        logger.debug('json from request\n%s' % _json)

        if 'sliders' in _json and _json['sliders'] == 'true':
            logger.info('found sliders in POST')
            # for slider in _settings.getTableSliders():
            #     if slider['column'] in _json:
            #         key = slider['column']
            #         slider_data = json.loads(_json.pop(key))
            #         if type(slider_data) is list:
            #             _json[key] = slider_data

        new_data = self.pipe.mouse.getTable(**_json)

        return json.dumps(new_data)

    def fixFilters(self, kwargs):
        """changes slider init to string for slider jquery

        Returns:
            dict: sliders
        """
        filters = app.settings.getTableFilters('mouse')
        for item in filters:
            logger.debug(item)

            if item['type'] == 'selection':
                preset = list()
                if item['column'] in kwargs:
                    preset += kwargs[item['column']]
                options = item['options']
                for i, option in enumerate(options):
                    name = ' '.join(option.split('_')).title()

                    checked = True
                    if option in preset:
                        checked = False

                    options[i] = (option, name, checked)
                item['options'] = sorted(options, key=lambda item: item[1])

                logger.debug('selection options %s' % item['options'])

            if item['type'] == 'slider':
                if item['column'] in kwargs:
                    item['init'] = str(kwargs[item['column']])
        logger.debug(filters)
        logger.debug(pprint.pformat(app.settings.getTableSliders('mouse')))
        return filters

    def getTable(self, **kwargs):
        """gets data from database

        Args:
            kwargs: (dict) same as for builQuery()
        Returns:
            dict: data from database
        """
        return self.pipe.getDataTable(**kwargs)


class Chart(Parent):
    """
    processes and returns data for mouse celltype
    expression chart
    """
    exposed = True

    def GET(self, **kwargs):
        data = self.getData(kwargs['gene_id'])
        return json.dumps(data)

    def POST(self, **kwargs):
        logger.debug('Charts POST')
        logger.debug(pprint.pformat(kwargs))
        data = self.getData(kwargs['gene_id'])
        return json.dumps(data)

    def getData(self, mouse_id):
        """
        responds to data GET requests
        Args:
            gene_id: (int) mouse gene id
        Returns:
            dict:
                title: (string)  chart title
                names: (list(string)) list of axis names for axis
                colors: (list(string)) strings to group colors by
                max: (float) max expression
                min: (float) min expression
                axis_length: (int) length of longest column name
                    used to calculate bottom margin to fit name
                values: (list(string, string, string, float))
                    data to be rendered
                    (Name, region, color group, value)
        """
        logger.debug('getting charts for %s' % mouse_id)

        annotations = self.pipe.mouse.celltypeAnnotations(self.isSuper())
        mouse = self.pipe.mouse.plotExpression(mouse_id, self.isSuper())
        values = list()
        columns = list()

        for cellType in mouse:
            _id = cellType['_id']
            name = ' '.join(_id.split('_')).title()
            values.append((name, cellType['region'], annotations[_id], cellType['value']))
            columns.append((cellType['_id'], name))

        order = app.settings.getOrder('celltypes')
        columns = sorted(columns, key=lambda i: order.index(annotations[i[0]]))
        names = [x[1] for x in columns]

        ret = {'values': values, 'names': names, 'colors': order}
        ret['title'] = 'Celltype Expression in Mice'
        ret['min'] = min([x[-1] for x in values])
        ret['max'] = max([x[-1] for x in values])
        ret['axis_length'] = max(len(x) for x in names)

        return ret


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
            data = self.pipe.mouse.textSearch(query)

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
