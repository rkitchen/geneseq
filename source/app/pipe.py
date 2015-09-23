from decimal import *
import app.settings as settings
import logging

_ROUND_DECIMAL = 1
logger = logging.getLogger(__name__)


class Pipe(object):
    """class handling connection and queries to database"""

    def __init__(self, config):
        """initializes variables"""
        # Pipe initializing
        logger.debug('initializing pipe')
        if not isinstance(config, settings.Settings):
            raise ValueError

    def roundData(self, data, roundn=_ROUND_DECIMAL):
        """rounds expression, expression_next, and difference,
        default round value is _ROUND_DECIMAL
        Args:
            data: (dict) fixed mysql data
            roundn: (int) number of decimal places to round to
        Returns:
            dict: rounded data
        """
        for k, v in data.items():
            if isinstance(v, Decimal):
                data[k] = round(v, roundn)
        return data
