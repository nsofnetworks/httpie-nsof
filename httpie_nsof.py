"""
Nsof OAuth2 plugin for HTTPie.

"""
import requests
import urlparse
import httpie
import os


__version__ = '0.2'
__author__ = 'Alon Horowitz'
__licence__ = 'Apache 2.0'


class NsofAuth(object):
    def __init__(self, org, username, password):
        self.org = org
        self.username = username
        self.password = password

    def __call__(self, r):
        host_url = self._get_host_url(r)
        if self._is_auth_endpoint_exists(host_url):
            tokens = self._get_tokens(host_url)
            r.headers['Authorization'] = 'Bearer %s' % tokens['access_token']
        return r

    def _get_host_url(self, r):
        parsed_url = urlparse.urlparse(r.url)
        if parsed_url.scheme:
            return "%s://%s" % (parsed_url.scheme, parsed_url.netloc)
        return parsed_url.netloc

    def _is_auth_endpoint_exists(self, host_url):
        url = self._get_auth_url(host_url)
        response = requests.options(url=url)
        return response.status_code == 200

    def _get_tokens(self, host_url):
        request_data = {"grant_type": "password",
                        "username": self.username,
                        "password": self.password}
        eorg = os.environ.get('EORG')
        if eorg:
            request_data['scope'] = "org:%s" % eorg
        url = self._get_auth_url(host_url)
        response = requests.post(url=url, json=request_data)
        response.raise_for_status()
        return response.json()

    def _get_auth_url(self, host_url):
        return "%s/v1/%s/oauth/token" % (host_url, self.org)


class NsofAuthPlugin(httpie.plugins.AuthPlugin):
    name = 'Nsof OAuth 2'
    auth_type = 'nsof'
    description = ''

    def get_auth(self, username, password):
        org, username = username.split("/")
        return NsofAuth(org, username, password)
