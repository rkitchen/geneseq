import json
import logging
from mako import exceptions
import app.settings
from app.parent import Parent
import pprint

logger = logging.getLogger(__name__)


class Human(object):

    def __init__(self, mako):
        self.lookup = mako
        self.gene = Gene(self)
        self.chart = Chart(self)


class Gene(Parent):
    """webapp handling requests for specific genes
    mounted on /gene
    """

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

        settings = app.settings
        pipe = self.pipe
        lookup = self.lookup

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
        gene = pipe.human.getGene(id)
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
        order = app.settings.getOrder('human')

        ret = sorted(header, key=lambda i: order.index(i[1]))
        logger.debug('sorted mouse header values %s' % ret)
        return ret


class Table(Parent):

    def GET(self, **kwargs):
        """responds to data GET requests
        Args:
            None yet
        Returns:
            str: table.html
        """
        logger.info('/data GET request')
        kwargs = self.fixInput(kwargs)
        logger.debug('GET kwargs: %s' % kwargs)
        # logger.debug('global test %s' % app.settings.Settings.test)
        data = self.pipe.table.getTable(**kwargs)

        kwargs = {'Title': 'Mouse Expression Table',
                  'data': data,
                  'filters': self.fixFilters(kwargs),
                  'columnNames': app.settings.getColumnNames(),
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

        return json.dumps(new_data)


class Chart(Parent):

    def GET(self, **kwargs):
        data = self.getData(kwargs['gene_id'])
        return json.dumps(data)

    def POST(self, **kwargs):
        logger.debug('Charts POST')
        logger.debug(pprint.pformat(kwargs))
        data = self.getData(kwargs['gene_id'])
        return json.dumps(data)

    def getData(self, human_id):
        logger.debug('getting charts for %s' % human_id)

        # TODO multiple charts
        tissues = self.pipe.human.plotBodymap(human_id)
        values = list()
        columns = list()
        for tissue in tissues:
            name = ' '.join(tissue['name'].split('_')).title()
            values.append((name, tissue['value']))
            columns.append(name)
        ret = {'values': values, 'names': columns}
        ret['min'] = min([x[1] for x in values])
        ret['max'] = max([x[1] for x in values])
        ret['axis_length'] = max(len(x) for x in columns)
        logger.debug('data to return: %s' % pprint.pformat(ret))
        return ret
