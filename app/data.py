from app import mongo_pipe
import app.settings
import logging
import json
from decimal import Decimal

logger = logging.getLogger(__name__)


class Data(object):
    exposed = True
    _mongo = None
    _settings = None

    def __init__(self, config):
        self._settings = config
        self._mongo = mongo_pipe.Pipe(config)

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
        data = self.getData(kwargs['geneid'])
        return json.dumps(data)

    def POST(self, **kwargs):
        data = self.getData(kwargs['geneid'])
        return json.dumps(data)

    def getData(self, geneId):
        gene = self._mongo.getGene(geneId)
        logger.debug('gene: %s' % gene)
        for k, v in gene.items():
            logger.debug('%s is type %s' % (v, type(v)))
        columns = list()
        values = list()
        count = 1
        for k, v in gene.items():
            name = ' '.join(k.split('_')).title()
            columns.append((count, name))
            for number in v:
                values.append((count, number))
            count += 1
        ret = {'names': columns, 'values': values}
        ret['min'] = min([x[1] for x in values])
        ret['max'] = max([x[1] for x in values])
        logger.debug('data to return: %s' % ret)
        return ret
