from pymongo import MongoClient
import app.pipe
import logging
import pprint

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)
_ROUND_DECIMAL = 2


class Pipe(app.pipe.Pipe):
    """class handling connection and queries to mongo database"""
    cursor = None

    def __init__(self, config):
        """initializes variables"""
        logger.debug('initializing mongo pipe')
        super().__init__(config)
        self.settings = config
        self.mouse = Mouse(self)
        self.table = Table(self)

    def fixData(self, data, roundn=_ROUND_DECIMAL):
        """parses data to sync variable names and datatypes.
        Converts expression to from float to Decimal()
        Args:
            data: (dict) data from mysql
        Returns:
            dict: adjusted data
        """
        if type(data) is float:
            return round(data, roundn)
        elif type(data) is str:
            if not ('ENSMUSG' in data or 'ENSG' in data):
                return ' '.join(data.split('_')).title()
        elif type(data) is dict:
            for k, v in data.items():
                    data[k] = self.fixData(v)
            return data
        elif type(data) is list:
            for i, v in enumerate(data):
                data[i] = self.fixData(v)
            return data
        return data

    def getGene(self, ids):
        print('getting gene with id %s' % ids)
        return self.gene.getGene(ids)
        # self.connect()
        # result = self.db.expr_norm.find({'id': 'ENSMUSG00000042489.11'},
        #                                 {'expr_data': 1, '_id': 0})[0]
        # result = result['expr_data']
        # logger.debug('mongo result data %s' % result)
        # result = self.fixData(result)
        # return result

    def execute(self, db, **kwargs):
        self.connect()
        self.cursor = self.db[db].find(**kwargs)

    def count(self):
        if self.cursor is not None:
            return self.cursor.count()
        else:
            return -1

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


class Parent(object):

    def __init__(self, pipe):
        self.pipe = pipe

class Human(Parent):

    def getMice(self, human_id):
        pipe = self.pipe
        find = dict()
        find['filter'] = {'_id': human_id}
        find['projection'] = {'mouse_map': 1}
        pipe.connect()
        mice = pipe.db.human.find_one(**find)
        mice = mice['mouse_map']
        pipe.disconnect()
        logger.debug('found mice for human gene %s' % human_id)
        logger.debug('mice type %s' % type(mice))
        logger.debug(pprint.pformat(mice))
        for mouse in mice:
            del mouse['confidence']
        logger.debug(pprint.pformat(mice))
        return mice

    def getAllMouseExpression(self, human_id):
        logger.debug('id %s' % human_id)
        mice = self.getMice(human_id)
        logger.debug('mice %s' % mice)
        data = list()
        for mouse in mice:
            item = dict()
            mouse_id = mouse['mouse_id']
            expression = self.getMouseExpression(mouse_id)
            if expression == []:
                continue
            item['mouse_id'] = mouse_id
            item['expression'] = expression
            data.append(item)
        return data


class Mouse(Parent):

    def getGene(self, mouse_id):
        pipe = self.pipe
        pipe.connect()

        find = dict()
        find['filter'] = {'_id': mouse_id}

        find['projection'] = {'processed': 1}
        """{'expression': '$processed.expression',
                              'enrichment': '$processed.enrichment',
                              'human_id': '$processed.human_id',
                              'type': '$processed.type'}"""

        gene = pipe.db.mouse.find_one(**find)
        pipe.disconnect()

        if gene is None:
            logger.debug('no gene found with id %s' % id)
            return gene

        ret = dict()
        ret['_id'] = gene['_id']
        ret['expression'] = gene['processed']['expression']
        ret['enrichment'] = gene['processed']['enrichment']
        ret['human_id'] = gene['processed']['human_id']
        ret['type'] = gene['processed']['type']
        logger.debug('found gene data %s' % gene)
        return pipe.fixData(ret)

    def plotMouseExpression(self, mouse_id):
        logger.debug('getting gene expression for mouseid %s' % mouse_id)
        pipe = self.pipe
        pipe.connect()

        aggregate = [{'$match': {'_id': mouse_id}},
                     {'$unwind': '$expression'},
                     {'$unwind': '$expression.values'},
                     {'$project': {'_id': '$expression.name',
                                   'value': '$expression.values'}}]
        cursor = pipe.db.mouse.aggregate(aggregate)
        pipe.disconnect()
        data = list()
        for item in cursor:
            data.append(item)
        logger.debug(pprint.pformat(data))
        return data

    def compMouseExpression(self, mouse_id, data=None, fix=True):
        logger.debug('computing mouse gene expression')
        pipe = self.pipe
        pipe.connect()

        aggregate = [{'$match': {'_id': mouse_id}},
                     {'$unwind': '$expression'},
                     {'$unwind': '$expression.values'},
                     {'$group': {'_id': '$expression.name',
                                 'average': {'$avg': '$expression.values'}}},
                     {'$sort': {'average': -1}},
                     {'$limit': 2}]
        cursor = pipe.db.mouse.aggregate(aggregate)
        pipe.disconnect()
        data = list()
        for item in cursor:
            data.append(item)

        logger.debug('processing data %s' % pprint.pformat(data))

        ret = {'max': data[0]['average'], 'next': data[1]['average']}
        ret['fold'] = ret['max'] / ret['next']
        logger.debug('mouse gene expression computed %s' % pprint.pformat(ret))
        return self.pipe.fixData(ret)


class Table(Parent):

    def getTable(self, sort=('expression', -1), limit=10,
                 expression=None, enrichment=None, **kwargs):
        logger.debug('expression %s' % expression)
        logger.debug('enrichment %s' % enrichment)
        logger.debug('kwargs %s' % kwargs)
        pipe = self.pipe
        pipe.connect()
        logger.debug('starting aggregation')
        # cursor = pipe.db.mouse.aggregate([{'$unwind': '$expression'},
        #     {'$unwind': '$expression.values'},
        #     {'$group': {'_id': {'id': '$_id',
        #                         'cell': '$expression.name'},
        #                 'avg':
        #                 {'$avg': '$expression.values'}}},
        #     {'$sort': {'avg': -1}},
        #     {'$group': {'_id': '$_id.id',
        #                 'cell': {'$first': '$_id.cell'},
        #                 'value': {'$first': '$avg'}}},
        #     {'$sort': {'_id': 1}}, {'$limit': 100}],
        #     allowDiskUse=True)
        aggregate = dict()
        pipeline = list()
        match = {'processed': {'$exists': True}}
        if expression is not None or enrichment is not None:
            if type(expression) is list:
                match['processed.expression'] = {'$gt': expression[0], '$lt': expression[1]}
            if type(enrichment) is list:
                match['processed.enrichment'] = {'$gt': enrichment[0], '$lt': enrichment[1]}
        pipeline.append({'$match': match})
        pipeline.append(
            {'$project': {
                '_id': 1, 'cell': '$processed.type',
                'expression': '$processed.expression',
                'enrichment': '$processed.enrichment',
                'human_id': '$processed.human_id'}})

        if type(sort) is list or type(sort) is tuple:
            pipeline.append({'$sort': {sort[0]: sort[1]}})
        if limit is not None:
            limit = int(limit)
            pipeline.append({'$limit': limit})

        aggregate['pipeline'] = pipeline
        aggregate['allowDiskUse'] = True
        logger.debug('mongo aggregation:\n%s' % pprint.pformat(aggregate))
        cursor = pipe.db.mouse.aggregate(**aggregate)
        logger.debug('finish aggregation')
        data = list()
        for item in cursor:
            data.append(item)
        pipe.disconnect()
        logger.debug(pprint.pformat(data))
        return pipe.fixData(data)
