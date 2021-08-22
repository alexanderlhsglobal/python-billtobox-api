import base64
import requests
import json
import time

from . import config
from .cachehandler import CacheHandler
from .authhandler import AuthHandler

class BillToBoxAPI:

    def __init__(self, clientId, clientSecret, demo=False):

        self.clientId = clientId
        self.clientSecret = clientSecret
        self.demo = demo
        self.headers = {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json',
        }

        self.baseUrl = config.DEMO_URL if demo else config.BASE_URL
        self.cacheHandler = CacheHandler()
        self.authHandler = AuthHandler(self, self.clientId, self.clientSecret)

    def doRequest(self, method, url, data=None, headers=None):

        if headers:
            mergedHeaders = self.headers
            mergedHeaders.update(headers)
            headers = mergedHeaders
        else: headers = self.headers

        reqUrl = '{base}/{url}'.format(base=self.baseUrl, url=url)

        if method == 'GET':
            response = requests.get(reqUrl, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(reqUrl, data=json.dumps(data), headers=headers)
        elif method == 'PUT':
            response = requests.put(reqUrl, data=json.dumps(data), headers=headers)
        
        return response

    def request(self, method, url, data=None, headers=None):

        self.authHandler.checkHeaderTokens()
        response = self.doRequest(method, url, data, headers)

        if 'json' in response.headers['Content-Type']:
            respContent = response.json()
        elif 'pdf' in response.headers['Content-Type']:
            respContent = response.content
        
        return response.status_code, response.headers, respContent
    
    def get(self, url, data=None, headers=None):
        status, headers, response = self.request('GET', url, data, headers)
        return status, headers, response
    
    def post(self, url, data=None, headers=None):
        status, headers, response = self.request('POST', url, data, headers)
        return status, headers, response
    
    def put(self, url, data=None, headers=None):
        status, headers, response = self.request('PUT', url, data, headers)
        return status, headers, response