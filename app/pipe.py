import pymysql
import yaml
import os
from decimal import *


class Pipe:

    def __init__(self):
        # Pipe initializing
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.select = self.loadConfig()

    def buildQuery(self, ids=None, limit=10, **kwargs):
        print(kwargs)
        req = ["SELECT"]
        if ids is not None:
            if ids is list:
                req.append(','.join(ids))
            elif ids in self.select['SELECT']:
                req.append(','.join(self.select['SELECT'][ids]))
            else:
                req.append(ids)
        else:
            req.append('*')

        req.append('FROM processed')
        if 'ranges' in kwargs:
            req.append('WHERE')
            ranges = kwargs['ranges']
            for point in kwargs['ranges']:
                s = (point, ranges[point]['min'], point, ranges[point]['max'])
                req.append('%s > %s AND %s < %s' % s)
                req.append('AND')
            del req[-1]
        elif 'where' in kwargs:
            req.append('WHERE')
            req.append(kwargs['where'])

        req.append('LIMIT')
        req.append(str(limit))
        if 'order' in kwargs:
            req.append('ORDER BY')
            req.append(kwargs['order'])
        if 'extra' in kwargs:
            req.append(kwargs['extra'])

        print(req)
        return ' '.join(req)

    def getRange(self, column):
        self.connect()
        cur = self.cur_dict
        req = self.buildQuery(ids='max(%s),min(%s)' % (column, column))
        cur.execute(req)
        res = cur.fetchall()
        self.close()
        return res[0]

    def loadConfig(self):
        f = open("%s/select.yaml" % self.path, 'r')
        raw = f.read()
        f.close()
        return yaml.load(raw)

    def search_like(self, query):
        self.connect()
        # TODO sanitize query
        req = self.buildQuery('id', where='geneName LIKE %s' % query)
        # req = 'SELECT id FROM processed WHERE geneName LIKE "%s"' % query
        cur = self.cur
        cur.execute(req)
        res = cur.fetchall()
        print(res)
        self.close()
        data = list()
        for item in res:
            data.append(item[0])
        return data

#   gets rows from mysql that match certain filter requirements
#   TODO better query generation logic
    def getDataTable(self, start=1, limit=50, query=None, **kwargs):
        self.connect()
        cur = self.cur_dict

        # req = 'SELECT %s' % ",".join(self.select['table'])
        req = self.buildQuery('table', limit=limit, **kwargs)
        # req += ' FROM processed WHERE id > %d LIMIT %d' % (start, limit)
        # req += ';'
        print(req)

        cur.execute(req)
        d = cur.fetchall()
        self.close()

        data = list()
        for item in d:
            item = self.fixData(item)
            data.append(self.roundData(item))

        return data

    def getGene(self, id):
        self.connect()
        cur = self.cur_dict

        req = self.buildQuery('gene', where='id=%d' % id)
        # req = "SELECT id,celltype,expression,expression_next,"
        # req += "geneName,geneID,geneID_human,geneID_mouse,geneType "
        # req += "FROM processed WHERE id=%d;" % id
        cur.execute(req)
        data = cur.fetchall()
        data = data[0]

        data = self.fixData(data)

        self.close()
        return data

        try:
            cur.execute(req)
        except:
            # makes sure that request string gets logged.
            # Actual error doesn't print it
            # logger.warning('error with request: %s' % req)
            raise

        self.close()
        return data

    def fixData(self, data):
        if 'expression' in data:
            data['expr'] = Decimal(str(data['expression']))
            del data['expression']

        if 'expression_next' in data:
            data['expr_next'] = Decimal(str(data['expression_next']))
            del data['expression_next']

        if 'celltype' in data:
            data['cellType'] = data['celltype'].capitalize()
            del data['celltype']

        if 'geneType' in data:
            s = data['geneType']
            s = s.replace('_', ' ')
            s = s.title()
            data['geneType'] = s

        if 'expr_diff' not in data:
            data['expr_diff'] = data['expr'] - data['expr_next']

        return data

    def roundData(self, data):
        if 'expr' in data:
            data['expr'] = round(data['expr'], 3)
        if 'expr_next' in data:
            data['expr_next'] = round(data['expr_next'], 3)
        if 'expr_diff' in data:
            data['expr_diff'] = round(data['expr_diff'], 3)
        return data

    #  closes a mysql connection
    def close(self):
        # ogger.info('connection closing')
        self.cur.close()
        self.cur_dict.close()
        self.conn.close()

#  opens a mysql connection and creates cursors
    def connect(self):
        # logger.info('connection opening')
        self.conn = pymysql.connect(host='localhost',
                                    user='pipe',
                                    passwd='JcLAz2tpujdMnzsQ',
                                    db='gene_locale',
                                    charset='utf8',
                                    init_command="SET NAMES UTF8")
        self.cur_dict = self.conn.cursor(pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()
