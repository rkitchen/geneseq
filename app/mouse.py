import json
import logging

from mako import exceptions
# from mako.lookup import TemplateLookup
import pprint

logger = logging.getLogger(__name__)


class Mouse(object):

    def __init__(self, settings, pipe, mako):
        self.settings = settings
        self.pipe = pipe
        self.lookup = mako

        self.table = Table(self)
        self.gene = Gene(self)
        self.chart = Chart(self)


class Parent(object):

    def __init__(self, mouse):
        self.settings = mouse.settings
        self.pipe = mouse.pipe
        self.lookup = mouse.lookup


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

        pipe = self.pipe
        lookup = self.lookup
        settings = self.settings

        if id is None:
            return 'No id given'
        # else:
        #     if not isinstance(id, int):
        #         try:
        #             id = int(id)
        #         except ValueError as e:
        #             print(e)
        #             # TODO return proper error message
        #             return 'invalid id given'
        tmpl = lookup.get_template("gene.html")
        kwargs['Title'] = 'test'
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
        order = self.settings.getOrder('mouse')

        ret = sorted(header, key=lambda i: order.index(i[1]))
        logger.debug('sorted mouse header values %s' % ret)
        return ret

class Table(Parent):
    """displays mysql data in a table
    mounted on /data and /table"""
    exposed = True

    def fixSliderInit(self, kwargs):
        """changes slider init to string for slider jquery

        Returns:
            dict: sliders
        """
        sliders = self.settings.getTableSliders()
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
        logger.debug(self.settings.getTableSliders())
        return sliders

    def getTable(self, **kwargs):
        """gets data from database

        Args:
            kwargs: (dict) same as for builQuery()
        Returns:
            dict: data from database
        """
        return self.pipe.getDataTable(**kwargs)

    def GET(self, order='expression', **kwargs):
        """responds to data GET requests
        Args:
            None yet
        Returns:
            str: table.html
        """
        logger.info('/data GET request')
        logger.debug('GET kwargs: %s' % kwargs)
        data = self.pipe.table.getTable()
        kwargs = {'Title': 'Mouse Expression Table',
                  'data': data,
                  'sliders': self.fixSliderInit(kwargs),
                  'columnNames': self.settings.getColumnNames(),
                  'order': order}
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

        new_data = self.pipe.table.getTable(**_json)

        return json.dumps(self.serializeJSON(new_data))


class Chart(Parent):
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
        logger.debug('getting charts for %s' % mouse_id)

        # TODO multiple charts
        mouse = self.pipe.mouse.plotMouseExpression(mouse_id)
        values = list()
        columns = list()
        for cellType in mouse:
            name = ' '.join(cellType['_id'].split('_')).title()
            values.append((name, cellType['value']))
            columns.append(name)
        ret = {'values': values, 'names': columns}
        ret['min'] = min([x[1] for x in values])
        ret['max'] = max([x[1] for x in values])
        logger.debug('data to return: %s' % pprint.pformat(ret))
        return ret
