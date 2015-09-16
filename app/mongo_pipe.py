from pymongo import MongoClient
import app.settings
import logging
import pprint

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)
_ROUND_DECIMAL = 2


class Pipe(object):
    """class handling connection and queries to mongo database"""
    cursor = None

    def __init__(self):
        """initializes variables"""
        logger.debug('initializing mongo pipe')
        self.mouse = Mouse(self)
        self.human = Human(self)

    def fixData(self, data, style='title', roundn=_ROUND_DECIMAL):
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
            if style == 'title':
                return ' '.join(data.split('_')).title()
            elif style == 'caps':
                return ' '.join(data.split('_')).upper()
        elif type(data) is dict:
            for k, v in data.items():
                if 'id' in k or k in ['source', 'human_name']:
                    style = 'caps'
                else:
                    style = 'title'
                data[k] = self.fixData(v, style)
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

    def getTable(self, **kwargs):
        logger.debug('kwargs %s' % kwargs)
        pipe = self.pipe
        pipe.connect()
        logger.debug('starting aggregation')

        aggregate = dict()
        pipeline = list()
        if 'match' in kwargs:
            pipeline.append({'$match': kwargs['match']})
        if 'pipeline' in kwargs:
            pipeline += kwargs['pipeline']
        if 'sort' in kwargs:
            sort = kwargs['sort']
            if type(sort) is list or type(sort) is tuple:
                pipeline.append({'$sort': {sort[0]: sort[1]}})
        if 'limit' in kwargs:
            pipeline.append({'$limit': int(kwargs['limit'])})
        else:
            limit = app.settings.getDefaultLimit(self.name)
            pipeline.append({'$limit': int(limit)})

        aggregate = {'pipeline': pipeline, 'allowDiskUse': True}

        logger.debug('mongo aggregation:\n%s' % pprint.pformat(aggregate))
        cursor = pipe.db[self.name].aggregate(**aggregate)

        logger.debug('finish aggregation')
        data = list()
        for item in cursor:
            data.append(item)

        pipe.disconnect()
        logger.debug(pprint.pformat(data))
        return pipe.fixData(data)


class Human(Parent):
    name = 'human'

    def getGene(self, human_id):
        pipe = self.pipe
        pipe.connect()
        cursor = pipe.db.human.find_one({'_id': human_id})

        document = dict()
        document['_id'] = cursor['_id']
        document['gene_name'] = cursor['gene_name']
        document['chr'] = cursor['gene_chr']
        document['source'] = cursor['source']
        return document

    def getName(self, human_id):
        pipe = self.pipe
        pipe.connect()
        document = pipe.db.human.find_one({'_id': human_id})
        pipe.disconnect()
        logger.debug('found entry for id %s \n%s' % (human_id, document['gene_name']))
        return document['gene_name']

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

    def plotBodymap(self, human_id):
        logger.debug('getting gene expression for humanid %s' % human_id)
        pipe = self.pipe
        pipe.connect()

        aggregate = [{'$match': {'_id': human_id}},
                     {'$unwind': '$bodymap'},
                     {'$project': {'name': '$bodymap.name',
                                   'value': '$bodymap.value'}}]
        cursor = pipe.db.human.aggregate(aggregate)
        pipe.disconnect()
        data = list()
        for item in cursor:
            data.append(item)
        logger.debug(pprint.pformat(data))
        return data

    def getTable(self, sort=('gene_name', -1), **kwargs):
        logger.debug('kwargs %s' % kwargs)
        pipe = self.pipe
        pipe.connect()
        logger.debug('starting aggregation')

        pipeline = [
            {'$project': {
                '_id': 1,
                'gene_name': 1,
                'source': 1,
                'gene_chr': 1}}]

        kwargs['match'] = {'bodymap': {'$exists': True}}
        kwargs['pipeline'] = pipeline
        kwargs['sort'] = sort

        data = super().getTable(**kwargs)

        for item in data:
            item['bodymap'] = 1

        logger.debug(pprint.pformat(data))
        return data


class Mouse(Parent):
    name = 'mouse'

    def getGene(self, mouse_id):
        pipe = self.pipe
        pipe.connect()

        find = dict()
        find['filter'] = {'_id': mouse_id}
        find['projection'] = {'processed': 1}

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
        ret['human_name'] = pipe.human.getName(ret['human_id'])
        ret['type'] = gene['processed']['type']
        logger.debug('found gene data %s' % gene)

        return pipe.fixData(ret)

    def plotExpression(self, mouse_id):
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

    def getCellTypes(self):
        pipe = self.pipe
        pipe.connect()
        pipeline = [{'$match': {'processed': {'$exists': True}}},
                    {'$group': {'_id': '$processed.type'}}]
        cursor = pipe.db.mouse.aggregate(pipeline)
        celltypes = list()
        for cell in cursor:
            celltypes.append(cell['_id'])
        return celltypes

    def getTable(self, sort=('expression', -1), **kwargs):
        logger.debug('kwargs %s' % pprint.pformat(kwargs))
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

        if 'celltype' in kwargs:
            celltype = kwargs['celltype']
            if type(celltype) is str:
                match['processed.type'] = celltype
            elif type(celltype) is list:
                match['processed.type'] = {'$nin': celltype}

        if 'expression' in kwargs and type(kwargs['expression']) is list:
            if type(kwargs['expression']) is list:
                value = kwargs['expression']
                match['processed.expression'] = {'$gt': value[0], '$lt': value[1]}

        if 'enrichment' in kwargs and type(kwargs['enrichment']) is list:
            value = kwargs['enrichment']
            match['processed.enrichment'] = {'$gt': value[0], '$lt': value[1]}

        pipeline = [
            {'$project': {
                '_id': 1, 'cell': '$processed.type',
                'expression': '$processed.expression',
                'enrichment': '$processed.enrichment',
                'human_id': '$processed.human_id'}}]

        kwargs['match'] = match
        kwargs['pipeline'] = pipeline
        kwargs['sort'] = sort

        data = super().getTable(**kwargs)
        return data
