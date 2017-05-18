"""
Nsof OAuth2 plugin for HTTPie.

"""
import requests
import httpie


__version__ = '0.1'
__author__ = 'Alon Horowitz'
__licence__ = 'Apache 2.0'


class NsofAuth(object):
    NSOF_API_URL = "https://api.nsof.io"

    def __init__(self, org, username, password):
        self.org = org
        self.username = username
        self.password = password

    def __call__(self, r):
        tokens = self._get_tokens()
        r.headers['Authorization'] = 'Bearer %s' % tokens['access_token']
        return r

    def _get_tokens(self):
        request_data = {"grant_type": "password",
                        "username": self.username,
                        "password": self.password}
        url = "%s/v1/%s/oauth/token" % (self.NSOF_API_URL, self.org)
        response = requests.post(url=url, json=request_data)
        response.raise_for_status()
        return response.json()


class NsofAuthPlugin(httpie.plugins.AuthPlugin):
    name = 'Nsof OAuth 2'
    auth_type = 'nsof'
    description = ''

    def get_auth(self, username, password):
        org, username = username.split("/")
        return NsofAuth(org, username, password)
