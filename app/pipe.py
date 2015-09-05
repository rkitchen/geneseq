import pymysql
import os
from decimal import *
import app.settings as settings
import logging

_ROUND_DECIMAL = 1
logger = logging.getLogger(__name__)


class Pipe(settings.Settings):
    """class handling connection and queries to database"""

    def __init__(self):
        """initializes variables"""
        super().__init__()
        # Pipe initializing
        logger.debug('initializing pipe')
        self.path = os.path.dirname(os.path.realpath(__file__))

    def buildQuery(self, ids=None, limit=10, **kwargs):
        """builds a mysql query string from set of arguments

        Args:
            ids: (list,str) mysql column names for SELECT
                list: list of column names to be parsed
                str:  identifier for set of colnames
                      from config or string of colnames
            ranges: (dict) list of min/max ranges for expr/expr_next/expr_diff
                keys: column names
                values:
                    min: minimum
                    max: maximum
            where: (str) mysql conditional string
            order: (dict,str) ORDER BY
                dict:
                    by: value for ORDER BY
                    direction: ASC or DESC
                               True   False
                str: if passed as string direction should
                     accompany in kwargs
            extra: (str) anything extra to be appended
            limit: (int) LIMIT

        Returns:
            str: complete mysql query string
        """
        logger.info('building query')
        logger.debug('kwargs: %s' % kwargs)
        req = ["SELECT"]
        req.append(self.parseIDs(ids))

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

        if 'order' in kwargs:
            req.append('ORDER BY')
            if type(kwargs['order']) is dict:
                req.append(self.translate(kwargs['order']['by']))
                direction = kwargs['order']['direction']
                if direction:
                    direction = 'ASC'
                else:
                    direction = 'DESC'
                req.append(direction)
            else:
                req.append(self.translate(kwargs['order']))
                if 'direction' in kwargs:
                    direction = kwargs['direction']
                    if type(direction) is bool:
                        if kwargs['direction']:
                            direction = 'ASC'
                        else:
                            direction = 'DESC'
                    req.append(direction)
        if 'extra' in kwargs:
            if type(kwargs['extra']) is list:
                req += kwargs['extra']
            else:
                req.append(kwargs['extra'])

        req.append('LIMIT')
        req.append(str(limit))
        logger.info('query built: %s' % req)
        return ' '.join(req) + ';'

    def getRange(self, column):
        """gets range of values from database column

        Args:
            column: (str) name of column to be queried

        Returns:
            list: [min,max]
        """
        self.connect()
        cur = self.cur
        req = self.buildQuery(ids='max(%s),min(%s)' % (column, column))
        cur.execute(req)
        res = cur.fetchall()
        self.close()
        return res[0]

    def search_like(self, query):
        """searches for a row with geneName matching query
            Args:
                query: (str) genename to be searched
            Returns:
                list: list id numbers with matching names
        """
        logger.info('searching database for match, query: %s' % query)
        # TODO more robust searching
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
        logger.debug('search results: %s' % data)
        return data

    def getDataTable(self, start=1, limit=None, query=None, **kwargs):
        """gets multiple rows from database matching filter requirements

        Args:
            limit: (int) limit number of results
                   uses default if not specified
        Returns:
            list: list of rows matching criteria
                  each row contained in dictionary
        """
        logger.info('getting data table')
        logger.debug('limit: %s\n\t\tkwargs: %s' % (limit, kwargs))
        self.connect()
        cur = self.cur_dict

        if limit is None:
            limit = self.getDefaultLimit()

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
        """gets data for specific gene from database

        Args:
            id: (int) database id number for gene
        Returns:
            dict: gene data
        """
        logger.info('getting gene, id: %s' % str(id))
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
        data = self.roundData(data, roundn=2)

        self.close()
        return data

        try:
            cur.execute(req)
        except:
            # TODO makes sure that request string gets logged.
            # Actual error doesn't print it
            # logger.warning('error with request: %s' % req)
            raise

        self.close()
        logger.debug('gene data: %s' % data)
        return data

    def fixData(self, data):
        """parses data to sync variable names and datatypes.
        Converts expression to from float to Decimal()
        Args:
            data: (dict) data from mysql
        Returns:
            dict: adjusted data
        """
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

    def roundData(self, data, roundn=_ROUND_DECIMAL):
        """rounds expression, expression_next, and difference,
        default round value is _ROUND_DECIMAL
        Args:
            data: (dict) fixed mysql data
            roundn: (int) number of decimal places to round to
        Returns:
            dict: rounded data
        """
        if 'expr' in data:
            data['expr'] = round(data['expr'], roundn)
        if 'expr_next' in data:
            data['expr_next'] = round(data['expr_next'], roundn)
        if 'expr_diff' in data:
            data['expr_diff'] = round(data['expr_diff'], roundn)
        return data

    def close(self):
        """Closes database connection and cursors"""
        logger.info('connection closing')
        self.cur.close()
        self.cur_dict.close()
        self.conn.close()

    def connect(self):
        """Opens mysql connection
        and creates cursors and dict_cursor
        """
        logger.info('connection opening')
        self.conn = pymysql.connect(host='localhost',
                                    user='pipe',
                                    passwd='JcLAz2tpujdMnzsQ',
                                    db='gene_locale',
                                    charset='utf8',
                                    init_command="SET NAMES UTF8")
        self.cur_dict = self.conn.cursor(pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()
