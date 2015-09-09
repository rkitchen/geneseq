from pymongo import MongoClient
import app.pipe
import logging

logger = logging.getLogger(__name__)


class Pipe(app.pipe.Pipe):

    def __init__(self, config):
        super().__init__(config)

    def connect(self):
        self.client = MongoClient()
        self.db = self.client.gene_locale

    def disconnect(self):
        self.db = None
        self.client.close()
