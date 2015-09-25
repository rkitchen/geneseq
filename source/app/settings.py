import yaml
import os
import logging
import copy
import app.mongo_pipe

logger = logging.getLogger(__name__)
path = os.path.dirname(os.path.realpath(__file__))

config = None


def init(_cherrypy):
    """
    initializes singleton variables
    Args:
        _cherrypy: (cherrypy) common cherrypy object to manage sessions from any module
    """
    global config
    global pipe
    global SESSION_KEY
    global cherrypy

    config = loadConfig()
    pipe = app.mongo_pipe.Pipe()
    logger.debug(getConfig())
    SESSION_KEY = '_session_u'
    cherrypy = _cherrypy

    setCount()


def getConfig():
    """gets config dictionary
    Returns:
        dict: config dictionary
    """
    return copy.deepcopy(config)


def setCount():
    """
    Gets current database count of each collection and passes
        to setCurrentCount
    """
    setCurrentCount('human', pipe.human.count())
    setCurrentCount('mouse', pipe.mouse.count())


def setCurrentCount(name, count):
    """
    Sets current count of given collections
    to limit sliders and config dictionary
    Args:
        name: (string) name of collection in database
        count: (int) count
    """
    sliders = config['table_input'][name]
    config['count'] = count
    for slider in sliders:
        if slider['column'] == 'limit':
            logger.debug('found limit slider, changing max to %s' % count)
            slider['max'] = count
            slider['init'] = count


def setCellTypes(name, celltypes):
    """
    Sets sidebar option `celltype` to given celltype array
    Args:
        celltypes: (list(string)) list of celltypes
    """
    for filter in config['table_input'][name]:
        if filter['type'] == 'selection' and filter['column'] == 'celltype':
            filter['options'] = celltypes
            break


def loadConfig():
    """Loads config from yaml file"""
    logger.debug('loading config from file')
    f = open("%s/conf/settings.yaml" % path, 'r')
    raw = f.read()
    f.close()
    return yaml.load(raw)


def translate(key):
    """translates python var names to mysql column names

    Args:
        key (str): key to search in config
    Returns:
        str: translated key
        None: returns key if no match found
    """
    logger.debug('translating, key: %s' % key)
    if key in config['translate']:
        colName = config['translate'][key]
        logger.debug('key found, translated to: %s' % colName)
        return colName
    else:
        logger.debug('key not found')
        return key


def translate_readable(key):
    """translates variables names to their human readable form

    Args:
        key (str): key to search in config
    Returns:
        str: translated key
        None: returns key if no match found
    """
    logger.debug('translating key %s' % key)
    if key in config['readable']:
        name = config['readable'][key]
        logger.debug('key found, translated to %s' % name)
        return name
    else:
        logger.debug('key not found')
        return key


def getColumnNames(name):
    """Gets the visible and variable names of the columns
    displayed in the html data table

    Returns:
        list: data on a column
            list:
                [0] Human readable name
                [1] Variable name in condensed
    """
    return copy.deepcopy(config['table_columns'][name])


def getDefaultLimit(name):
    """finds default limit set in limit-slider config

    Returns:
        int: default query limit
    """
    for item in config['table_input'][name]:
            if item['column'] == 'limit':
                if item['init'] == 0:
                    setCount()
                    return getDefaultLimit(name)
                return copy.deepcopy(item['init'])


# returns set of SELECT column names in
# mysql syntax form
def parseIDs(ids):
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
    elif ids in config['SELECT']:
        return (','.join(config['SELECT'][ids]))
    else:
        return copy.deepcopy(ids)


def getTableSliders(name):
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
    sliders = list()
    input = config['table_input'][name]
    for item in input:
        if item['type'] == 'slider':
            sliders.append(item)
    return copy.deepcopy(sliders)


def getTableFilters(name):
    """
    gets all sliders of `name`. This contains both sliders and 
    checkbox options
    Args:
        name: (string) name of collection
    Returns:
        list: list of filters
    """
    return copy.deepcopy(config['table_input'][name])


def getOrder(name):
    """
    gets order of collection `name` from config
    Args:
        name: (string) name of collection
    Returns:
        list: ordered list of collection `name`
    """
    return copy.deepcopy(config['order'][name])


def getBrainspanRegions():
    """
    gets explicit brainspan's brain regions. All others
    will be grouped together as neocortex (NCX)
    Returns:
        list(string): explicit brainspan brain regions
    """
    return copy.deepcopy(config['brainspan']['regions'])
