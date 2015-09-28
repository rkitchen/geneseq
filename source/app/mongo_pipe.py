from pymongo import MongoClient
from bcrypt import hashpw
from bcrypt import gensalt
import pymongo
import app.settings
import logging
import pprint
import re

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
        self.auth = Auth(self)

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

    def textSearch(self, query):
        mouse = self.mouse.textSearch(query)
        human = self.human.textSearch(query)

        logger.debug('mouse %s' % mouse)
        logger.debug('human %s' % human)

        mouse_names = list()
        for item in mouse:
            mouse_names.append(item['human_name'])

        for index, item in enumerate(human):
            if item['human_name'] not in mouse_names:
                mouse.append(item)

        return mouse



class Auth(object):
    def __init__(self, pipe):
        self.pipe = pipe

    def auth(self, username, password):
        pipe = self.pipe
        pipe.connect()
        record = pipe.db.users.find_one({'username': username})
        pipe.disconnect()

        if record is not None:
            digest = record['password']
            if digest == self.getDigest(password, digest):
                return True
        return False

    def getDigest(self, password, salt=None):
        if not salt:
            salt = gensalt(rounds=13)
        digest = hashpw(password.encode('utf8'), salt)
        return digest

    def register(self, username, password, email):
        pipe = self.pipe
        pipe.connect()

        exists = pipe.db.users.find_one({'username': username})
        logger.debug('username %s exists %s' % (username, exists))
        success = False
        if exists is None:
            success = True
            digest = self.getDigest(password)
            pipe.db.users.insert_one({'username': username,
                                      'password': digest,
                                      'super': False,
                                      'email': email})

        pipe.disconnect()
        return success

    def newPassword(self, username, old_password, new_password):
        if self.auth(username, old_password):
            digest = self.getDigest(new_password)

            pipe = self.pipe
            pipe.connect()
            pipe.db.users.update_one({'username': username}, {'$set': {'password': digest}})
            pipe.disconnect()

            return True

        return False

    def remove(self, username):
        pipe = self.pipe
        pipe.connect()

        pipe.db.users.remove({'username': username})
        pipe.disconnect()

    def isSuper(self, username):
        logger.debug('username: %s' % username)
        if username is None:
            return False
        pipe = self.pipe
        pipe.connect()

        record = pipe.db.users.find_one({'username': username})
        pipe.disconnect()

        if record is not None and record['super']:
            return True
        else:
            return False


class Parent(object):

    def __init__(self, pipe):
        self.pipe = pipe

    def getTable(self, **kwargs):
        logger.info('kwargs %s' % kwargs)
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
        if 'limit' in kwargs and kwargs['limit'] > 0:
            pipeline.append({'$limit': int(kwargs['limit'])})
        else:
            limit = app.settings.getDefaultLimit(self.name)
            pipeline.append({'$limit': int(limit)})

        aggregate = {'pipeline': pipeline, 'allowDiskUse': True}

        logger.info('mongo aggregation:\n%s' % pprint.pformat(aggregate))
        cursor = pipe.db[self.name].aggregate(**aggregate)

        logger.info('finish aggregation')
        data = list()
        for item in cursor:
            data.append(item)

        pipe.disconnect()
        return pipe.fixData(data)

    def count(self, field_exists=None):
        pipe = self.pipe
        pipe.connect()
        if field_exists is not None:
            count = pipe.db[self.name].count({field_exists: {'$exists': True}})
        else:
            count = pipe.db[self.name].count({})
        pipe.disconnect()
        logger.debug('current %s count %s type %s' % (self.name, count, type(count)))
        return count


class Human(Parent):
    name = 'human'

    def getGene(self, human_id):
        pipe = self.pipe
        pipe.connect()
        cursor = pipe.db.human.find_one({'_id': human_id})

        document = dict()
        document['human_id'] = cursor['_id']
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
        return data

    def brainspan_annotations(self):
        logger.debug('getting brainspan annotations')
        pipe = self.pipe
        pipe.connect()

        aggregate = [{'$project': {'days': 1}}]
        cursor = pipe.db.brainspan_annotation.aggregate(aggregate)
        annotations = dict()
        for item in cursor:
            annotations[item['_id']] = item['days']
        pipe.disconnect()

        logger.debug('annotations \n%s' % annotations)
        return annotations

    def plot_brainspan(self, human_id):
        pipe = self.pipe
        annotations = self.brainspan_annotations()

        aggregate = [{'$match': {'_id': human_id}},
                     {'$unwind': '$expression'},
                     {'$project': {'_id': 0,
                                   'brain': '$expression.brain',
                                   'region': '$expression.region',
                                   'value': '$expression.value'}}]
        pipe.connect()
        cursor = pipe.db.brainspan.aggregate(aggregate)
        data = list()
        for item in cursor:
            item['age'] = annotations[item['brain']]
            data.append(item)
        pipe.disconnect()
        return data

    def count(self):
        return super().count('bodymap')

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

        return data

    def textSearch(self, query):
        logger.debug('searching db for key %s' % query)
        query = '.*%s.*' % query
        logger.debug('regex query: %s' % query)
        regx = re.compile(query, re.IGNORECASE)

        projection = {'_id': 1, 'human_name': '$gene_name'}

        find = [{'$match': {'gene_name': regx}}, {'$project': projection}]

        pipe = self.pipe
        pipe.connect()
        cursor = pipe.db.human.aggregate(find)
        data = list()
        for item in cursor:
            item['expression'] = 'NA'
            item['enrichment'] = 'NA'
            item['cell'] = 'NA'
            data.append(item)
        pipe.disconnect()
        logger.debug('returning data %s' % pprint.pformat(data))
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
            logger.debug('no gene found with id %s' % mouse_id)
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

    def plotExpression(self, mouse_id, super=False):
        logger.debug('getting gene expression for mouseid %s' % mouse_id)

        pipe = self.pipe
        pipe.connect()

        celltypes = self.celltypeAnnotations(super)
        celltypes = list(celltypes.keys())

        aggregate = [{'$match': {'_id': mouse_id}},
                     {'$unwind': '$expression'},
                     {'$unwind': '$expression.regions'},
                     {'$unwind': '$expression.regions.values'},
                     {'$match': {'expression.name': {'$in': celltypes}}},
                     {'$project': {'_id': '$expression.name',
                                   'region': '$expression.regions.region',
                                   'value': '$expression.regions.values'}}]
        cursor = pipe.db.mouse.aggregate(aggregate)
        pipe.disconnect()
        data = list()
        for item in cursor:
            data.append(item)
        return data

    def celltypeAnnotations(self, super=False):
        logger.debug('getting mouse celltype annotation map')
        pipe = self.pipe
        pipe.connect()

        c = pipe.db.mouse_annotations
        find = {'projection': {'_id': 0, 'level2': 0, 'level4': 0}}
        if not super:
            find['filter'] = {'protected': False}
        cursor = c.find(**find)

        annotations = dict()
        for item in cursor:
            annotations[item['level1']] = item['level3']

        return annotations

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

    def count(self):
        return super().count('processed')

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
                'human_name': '$processed.human_name'}}]

        kwargs['match'] = match
        kwargs['pipeline'] = pipeline
        kwargs['sort'] = sort

        data = super().getTable(**kwargs)
        return data

    def textSearch(self, query):
        logger.debug('searching db for key %s' % query)
        query = '.*%s.*' % query
        logger.debug('regex query: %s' % query)
        regx = re.compile(query, re.IGNORECASE)

        projection = {'_id': 1, 'cell': '$processed.type',
                      'expression': '$processed.expression',
                      'enrichment': '$processed.enrichment',
                      'human_name': '$processed.human_name'}

        find = [{'$match': {'processed.human_name': regx}}, {'$project': projection}]

        pipe = self.pipe
        pipe.connect()
        cursor = pipe.db.mouse.aggregate(find)
        data = list()
        for item in cursor:
            data.append(item)
        pipe.disconnect()
        logger.debug('returning data %s' % pprint.pformat(data))
        return data
