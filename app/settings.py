import yaml
import os
import logging
import copy

logger = logging.getLogger(__name__)


class Settings(object):
    """handles access to settings stored in settings.yaml"""

    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.settings = self.loadConfig()

    def getConfig(self):
        """gets config dictionary
        Returns:
            dict: config dictionary
        """
        return copy.deepcopy(self.settings)

    def setCurrentCount(self, count):
        sliders = self.settings['table_sliders']
        self.settings['count'] = count
        for slider in sliders:
            if slider['column'] == 'limit':
                logger.debug('found limit slider, changing max to %s' % count)
                slider['max'] = count

    def loadConfig(self):
        """Loads config from yaml file"""
        logger.debug('loading config from file')
        f = open("%s/conf/settings.yaml" % self.path, 'r')
        raw = f.read()
        f.close()
        return yaml.load(raw)

    def translate(self, key):
        """translates python var names to mysql column names

        Args:
            key (str): key to search in config
        Returns:
            str: translated key
            None: returns key if no match found
        """
        logger.info('translating, key: %s' % key)
        if key in self.settings['translate']:
            colName = self.settings['translate'][key]
            logger.debug('key found, translated to: %s' % colName)
            return colName
        else:
            logger.debug('key not found')
            return key

    def translate_readable(self, key):
        """translates variables names to their human readable form

        Args:
            key (str): key to search in config
        Returns:
            str: translated key
            None: returns key if no match found
        """
        logger.info('translating key %s' % key)
        if key in self.settings['readable']:
            name = self.settings['readable'][key]
            logger.debug('key found, translated to %s' % name)
            return name
        else:
            logger.debug('key not found')
            return key

    def getColumnNames(self):
        """Gets the visible and variable names of the columns
        displayed in the html data table

        Returns:
            list: data on a column
                list:
                    [0] Human readable name
                    [1] Variable name in condensed
        """
        return copy.deepcopy(self.settings['table_columns'])

    def getDefaultLimit(self):
        """finds default limit set in limit-slider config

        Returns:
            int: default query limit
        """
        for item in self.settings['table_sliders']:
                if item['column'] == 'limit':
                    return copy.deepcopy(item['init'])

    # returns set of SELECT column names in
    # mysql syntax form
    def parseIDs(self, ids):
        """returns set of SELECT column names in
        mysql syntax

        Args:
            ids: (list, str)
                if type is list, joins list together and returns
                if type is str, searches for match in config
        Returns:
            str: mysql columns for SELECT
        """
        if ids is None:
            return '*'
        if type(ids) is list:
            return ','.join(ids)
        elif ids in self.settings['SELECT']:
            return (','.join(self.settings['SELECT'][ids]))
        else:
            return copy.deepcopy(ids)

    def getTableSliders(self):
        """gets list of sliders from configuration
        Returns:
            list: list of sliders and their config data
                -
                    name:     (str) Name of slider for viewing
                    column:   (str) var name associated with slider
                    scale:    (str) linear or logarithmic scale used for slider
                    min:      (int) min value of slider
                    max:      (int) max value of slider
                    init:(int,list) initial value/range of slider
        """
        return copy.deepcopy(self.settings['table_sliders'])
