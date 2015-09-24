import logging
import logging.handlers
import os
import time

# define logfile path
path = os.path.dirname(os.path.realpath(__file__))
_LOG_LEVELS = ['debug', 'info', 'error', 'cherry_access', 'cherry_error']
_Log_MAX_FILES = 5
_LOG_MAX_SIZE = 20000000

# check if debug folder structure exists
if not os.path.exists('%s/debug' % path):
    os.makedirs('%s/debug' % path)
if not os.path.exists('%s/session' % path):
    os.makedirs('%s/session' % path)
for level in _LOG_LEVELS:
    if not os.path.exists('%s/debug/%s' % (path, level)):
        os.makedirs('%s/debug/%s' % (path, level))

debug_path = '%s/debug' % path

# init formatters
# file logger format
format_file = logging.Formatter('%(asctime)s %(levelname)s::' +
                                '%(name)s:%(funcName)s()::%(message)s',
                                '%Y-%m-%d %H:%M:%S')

# screen logger format
format_screen = logging.Formatter('%(levelname)s::%(name)s: %(message)s')

# create and configure handlers
# logs warnings to screen
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(format_screen)

# logs warnings to file
date = str(time.strftime("%Y-%m-%d"))
warnings = logging.handlers.RotatingFileHandler('%s/error/warnings.log'
                                                % debug_path,
                                                'a',
                                                maxBytes=_LOG_MAX_SIZE,
                                                backupCount=_Log_MAX_FILES)
warnings.setLevel(logging.WARNING)
warnings.setFormatter(format_file)

# logs debugging to file
debug = logging.handlers.RotatingFileHandler('%s/debug/debug.log'
                                             % debug_path,
                                             'a',
                                             maxBytes=_LOG_MAX_SIZE,
                                             backupCount=_Log_MAX_FILES)
debug.setLevel(logging.DEBUG)
debug.setFormatter(format_file)

# logs info to file
general = logging.handlers.RotatingFileHandler('%s/info/info.log'
                                               % debug_path,
                                               'a',
                                               maxBytes=_LOG_MAX_SIZE,
                                               backupCount=_Log_MAX_FILES)
general.setLevel(logging.INFO)
general.setFormatter(format_file)

# create and configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# logger.addHandler(console)
logger.addHandler(warnings)
logger.addHandler(debug)
logger.addHandler(general)

error_file = '%s/cherry_error/error.log' % debug_path
access_file = '%s/cherry_access/access.log' % debug_path

from app.web import cherrypy

cherrypy.log.error_file = ""
cherrypy.log.access_file = ""

maxBytes = getattr(cherrypy.log, "rot_maxBytes", _LOG_MAX_SIZE)
backupCount = getattr(cherrypy.log, "rot_backupCount", _Log_MAX_FILES)

# Make a new RotatingFileHandler for the error log.
h = logging.handlers.RotatingFileHandler(error_file,
                                         'a', maxBytes, backupCount)
h.setLevel(logging.DEBUG)
h.setFormatter(cherrypy._cplogging.logfmt)
cherrypy.log.error_log.addHandler(h)

# Make a new RotatingFileHandler for the access log.
h = logging.handlers.RotatingFileHandler(access_file,
                                         'a', maxBytes, backupCount)
h.setLevel(logging.DEBUG)
h.setFormatter(cherrypy._cplogging.logfmt)
cherrypy.log.access_log.addHandler(h)

logger.warning('application init complete')







"""for i in logger.handlers[1:4]:
   i.doRollover()"""

"""# logger used specifically for debugging errors
logExcept = logging.Logger(__name__ + '.error')
# sets filepath of debugger output file
path = os.path.abspath(__file__)
path = '/'.join(path.split('/')[:-1])
path += '/debug/exceptions.log'"""
