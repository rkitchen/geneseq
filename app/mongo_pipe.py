from pymongo import MongoClient
import app.pipe
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
_ROUND_DECIMAL = 2


class Pipe(app.pipe.Pipe):
    """class handling connection and queries to mongo database"""

    def __init__(self, config):
        """initializes variables"""
        logger.debug('initializing mongo pipe')
        super().__init__(config)

    def fixData(self, data):
        """parses data to sync variable names and datatypes.
        Converts expression to from float to Decimal()
        Args:
            data: (dict) data from mysql
        Returns:
            dict: adjusted data
        """
        for k, v in data.items():
            if type(v) is list:
                for i, item in enumerate(v):
                    if type(item) is float:
                        logger.debug('converting float to decimal %s' % item)
                        v[i] = round(item, _ROUND_DECIMAL)
                data[k] = v
        return data

    def getGene(self, geneId):
        self.connect()
        result = self.db.expr_norm.find({'id': 'ENSMUSG00000042489.11'},
                                        {'expr_data': 1, '_id': 0})[0]
        result = result['expr_data']
        logger.debug('mongo result data %s' % result)
        result = self.fixData(result)
        result = self.roundData(result)
        return result

    def connect(self):
        """opens connection to mongo database"""
        logger.debug('connecting')
        self.client = MongoClient()
        self.db = self.client.gene_locale

    def disconnect(self):
        """disconnects from mongo database and cleans related variables"""
        logger.debug('disconnecting')
        self.db = None
        self.client.close()
