from app import mongo_pipe
import app.settings
import logging
import json
import pprint

logger = logging.getLogger(__name__)


class Charts(object):
    exposed = True
    _mongo = None
    _settings = None

    def __init__(self, config):
        self._settings = config
        self.pipe = mongo_pipe.Pipe(config)

    # def serializeJSON(self, data):
    #     """changes Decimal() types to str for json
    #     Args:
    #         data: (dict)
    #     Returns:
    #         dict: data with Decimal() replaced
    #     """
    #     # TODO search for all unserializable
    #     # objects rather than specific
    #     for key, item in data.items():
    #         if isinstance(item, Decimal) | 1:
    #             logger.debug('converting decimal to string %s' % item)
    #             data[key] = [float(number) for number in item]
    #             logger.debug(data[key])
    #     return json.dumps(data)

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
        expr = self.pipe.gene.getAllMouseExpression(human_id)[0]
        data = list()
        columns = list()
        for item in expr['expression']:
            name = ' '.join(item['_id'].split('_')).title()
            data.append((name, item['value']))
            columns.append(name)
        ret = {'values': data, 'names': columns}
        ret['min'] = min([x[1] for x in data])
        ret['max'] = max([x[1] for x in data])
        logger.debug('data to return: %s' % ret)
        return ret
