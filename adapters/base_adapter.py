#!/usr/bin/python
import requests
from requests.exceptions import ConnectionError
import time
import logging

class BaseAdapter(object):
    """docstring for BaseAdapter"""

    def __init__(self, url, retry_count):
        super(BaseAdapter, self).__init__()
        self.url = url
        self.retry_count = int(retry_count)
        self.logger = logging.getLogger('root')

    def execute(self, session, data, headers):
        if session is None:
            session = requests.seesion()
        count = 0
        response = None
        while True:
            try:
                response = session.post(
                    url=self.url, data=data, headers=headers)
            except ConnectionError as e:
                self.logger.error(e)
                count = count + 1
                if(count < self.retry_count):
                    time.sleep(10)
                    continue
            break
        return response

