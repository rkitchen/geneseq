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

    def serializeJSON(self, data):
        """changes Decimal() types to str for json
        Args:
            data: (dict)
        Returns:
            dict: data with Decimal() replaced
        """
        # TODO search for all unserializable
        # objects rather than specific
        for key, item in data.items():
            if isinstance(item, Decimal) | 1:
                logger.debug('converting decimal to string %s' % item)
                data[key] = str(item)
        return json.dumps(data)

    def GET(self, **kwargs):
        data = self.getData(kwargs['geneid'])
        return self.serializeJSON(data)

    def POST(self, **kwargs):
        pass

    def getData(self, geneId):
        gene = self._mongo.getGene(geneId)
        logger.debug('gene: %s' % gene)
        for k, v in gene.items():
            logger.debug('%s is type %s' % (v, type(v)))
        return gene
