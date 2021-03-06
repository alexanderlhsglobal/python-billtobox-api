from pathlib import Path
from requests_oauthlib import OAuth2Session

from . import config
from .constants.errors import NotFoundError

class AuthHandler:

    def __init__(self, api, clientId, clientSecret):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.api = api
        self.cacheHandler = api.cacheHandler

        self.authUrl = config.UAT_AUTH_URL if api.demo else config.AUTH_URL
        self.tokenUrl = config.UAT_ACCESS_TOKEN_URL if api.demo else config.ACCESS_TOKEN_URL
        self.redirectUri = None

        self.state = None
        self.token = None

    def getAuthURL(self, redirectUri):
        self.redirectUri = redirectUri

        oauth = OAuth2Session(self.clientId, redirect_uri=self.redirectUri, scope='openid')
        authorizationUrl, self.state = oauth.authorization_url(self.authUrl)
        return authorizationUrl
    
    def retrieveToken(self, response, state=None, redirectUri=None):
        if not redirectUri: 
            if not self.redirectUri: raise NotFoundError('redirect uri is not found. init the auth flow first or give the uri as a parameter.')
            redirectUri = self.redirectUri
        
        if not state: 
            if not self.state: raise NotFoundError('state is not found. init the auth flow first or give the state as a parameter.')
            state = self.state

        oauth = OAuth2Session(self.clientId, state=state, redirect_uri=redirectUri)
        oauthToken = oauth.fetch_token(self.tokenUrl, client_secret=self.clientSecret, authorization_response=response)
        self.token = oauth._client.access_token

        self.cacheHandler.setCache(self.clientId, self.token)

        return self.token
    
    def getToken(self):

        if self.token: return self.token
        raise NotFoundError('token is not found. init the auth flow first.')
    
    def setTokenHeader(self, token):
        bearerStr = 'Bearer {token}'.format(token=token)
        self.api.headers.update({'Authorization' : bearerStr})
    
    def checkHeaderTokens(self):

        # If no authorization header is found, we need to include the token
        if 'Authorization' not in self.api.headers:
            
            # Check if we have a token stored in cache, if not, acquire one
            # If we do, set it in the header
            token = self.cacheHandler.getCache(self.clientId)
            if token is None: token = self.getToken()
            self.setTokenHeader(token)