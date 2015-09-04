import logging
import logging.handlers
import os
import time

# define logfile path
path = os.path.dirname(os.path.realpath(__file__))
_LOG_LEVELS = ['debug', 'info', 'error']

# check if debug folder structure exists
if not os.path.exists('%s/debug' % path):
    os.makedirs('%s/debug' % path)
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
warnings = logging.FileHandler('%s/error/log-%s' % (debug_path, date))
warnings.setLevel(logging.WARNING)
warnings.setFormatter(format_file)
# logs debugging to file
debug = logging.FileHandler('%s/debug/log-%s' % (debug_path, date))
debug.setLevel(logging.DEBUG)
debug.setFormatter(format_file)
# logs info to file
general = logging.FileHandler('%s/info/log-%s' % (debug_path, date))
general.setLevel(logging.INFO)
general.setFormatter(format_file)
# create and configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logger.addHandler(console)
logger.addHandler(warnings)
logger.addHandler(debug)
logger.addHandler(general)

logger.warning('application init complete')







"""for i in logger.handlers[1:4]:
   i.doRollover()"""

"""# logger used specifically for debugging errors
logExcept = logging.Logger(__name__ + '.error')
# sets filepath of debugger output file
path = os.path.abspath(__file__)
path = '/'.join(path.split('/')[:-1])
path += '/debug/exceptions.log'"""
