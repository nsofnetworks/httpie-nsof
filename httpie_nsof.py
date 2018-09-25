"""
Nsof OAuth2 plugin for HTTPie.

"""
from __future__ import print_function
from __future__ import absolute_import
import tempfile
import json
import time
import os
import requests
import httpie
import jwt
import sys

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

__version__ = '1.1'
__author__ = 'Alon Horowitz'
__licence__ = 'Apache 2.0'

# endpoints
EP_LOGIN = '/v1/login/auth'
EP_GET_AUTHCODE = '/v1/login/authorize'
EP_GET_TOKEN = '/v1/oauth/token'


class NsofAuth(object):
    def __init__(self, org, username, password):
        self.org = org
        self.username = username
        self.password = password
        self.eorg = os.getenv('EORG', org)
        self.verbose = bool(os.getenv('VERBOSE', False))
        self.host_url = None

    def __call__(self, r):
        self.host_url = self._get_host_url(r)
        access_token = self._load_token_if_valid('access_token')
        if not access_token:
            tokens = self._refresh_authentication()
            if not tokens:
                tokens = self._authenticate()
            if tokens:
                access_token = tokens['access_token']
                self._store_token('access_token',
                                  access_token,
                                  store_eorg=True)
                if 'refresh_token' in tokens:
                    self._store_token('refresh_token',
                                      tokens['refresh_token'])
        if access_token:
            r.headers['Authorization'] = 'Bearer %s' % access_token
        return r

    def _refresh_authentication(self):
        refresh_token = self._load_token_if_valid('refresh_token')
        if not refresh_token:
            return None
        json = {"grant_type": "refresh_token",
                "refresh_token": refresh_token}
        if self.eorg != self.org:
            json['scope'] = 'org:%s' % self.eorg
        return self._do_call(EP_GET_TOKEN, 'post', json=json)

    def _authenticate(self):
        if self.username.startswith("key-") and '@' not in self.username:
            return self._authenticate_api_key()
        else:
            return self._authenticate_user()

    def _authenticate_api_key(self):
        json = {"grant_type": "client_credentials",
                "client_id": self.username,
                "client_secret": self.password}
        return self._do_call(EP_GET_TOKEN, 'post', json=json)

    def _authenticate_user(self):
        json = {"username": self.username,
                "password": self.password,
                "org_shortname": self.org}
        response = self._do_call(EP_LOGIN, 'post', json=json)
        if response['status'] != 'authorized':
            raise Exception('Could not log in. Returned status: %s',
                            response['status'])

        params = {'response_type': 'code',
                  'client_id': 'api',
                  'session_token': response['session_token']}
        response = self._do_call(EP_GET_AUTHCODE, 'get', params=params)

        json = {'grant_type': 'authorization_code',
                'client_id': 'api',
                'code': response['code']}
        if self.eorg != self.org:
            json['scope'] = 'org:%s' % self.eorg
        return self._do_call(EP_GET_TOKEN, 'post', json=json)

    def _is_auth_endpoint_exists(self, url):
        response = requests.options(url=url)
        return response.status_code == 200

    def _do_call(self, ep, method, params=None, json=None):
        url = self.host_url + ep
        if not self._is_auth_endpoint_exists(url):
            print("target endpoint failed to respond (URL: %s)." % url)
            exit(1)
        msg = "httpie-nsof: [%s] url=%s" % (self.eorg, url)
        if params:
            msg += ", params=%s" % params
        if json:
            msg += ", body=%s" % json
        self._vprint(msg)
        response = requests.request(method, url, params=params, json=json)
        response.raise_for_status()
        ret = response.json()
        self._vprint("httpie-nsof: [%s] response=%s" % (self.eorg, ret))
        return ret

    def _get_host_url(self, r):
        parsed_url = urlparse.urlparse(r.url)
        netloc_no_port = parsed_url.netloc.split(':')[0]
        if parsed_url.scheme:
            return "%s://%s" % (parsed_url.scheme, netloc_no_port)
        return netloc_no_port

    def _load_token_if_valid(self, name):
        path = self._get_token_path(name)
        try:
            with open(path) as f:
                token_info = json.load(f)
        except:
            return None
        if token_info['host_url'] != self.host_url:
            return None
        if token_info.get('eorg', self.eorg) != self.eorg:
            return None
        payload = jwt.decode(token_info['token'], verify=False)
        if time.time() > (payload['exp'] - 30):
            return None
        return token_info['token']

    def _store_token(self, name, token, store_eorg=False):
        path = self._get_token_path(name)
        token_info = {'token': token, 'host_url': self.host_url}
        if store_eorg:
            token_info['eorg'] = self.eorg
        with open(path, 'w') as f:
            json.dump(token_info, f)

    def _get_token_path(self, name):
        tmpdir = tempfile.gettempdir()
        return os.path.join(tmpdir, "httpie-nsof.%s" % name)

    def _vprint(self, msg):
        if self.verbose:
            print(msg)


class NsofAuthPlugin(httpie.plugins.AuthPlugin):
    name = 'Nsof OAuth 2'
    auth_type = 'nsof'
    description = ''
    auth_require = False

    def get_auth(self, username=None, password=None):
        if username is None:
            org = os.getenv("HTTPIE_NSOF_ORG")
            username = os.getenv("HTTPIE_NSOF_USERNAME")
        else:
            if '/' not in username or \
                    ('@' not in username and '/key-' not in username):
                print("httpie-nsof error: invalid username format or invalid "
                      "API key ID format", file=sys.stderr)
                sys.exit(httpie.ExitStatus.PLUGIN_ERROR)
            org, username = username.split("/")
        password = password or os.getenv("HTTPIE_NSOF_PASSWORD")
        self._verify_input(org=org, username=username, password=password)
        return NsofAuth(org, username, password)

    def _verify_input(self, **input_params):
        missing = [k for k, v in input_params.items() if not v]
        if missing:
            print("httpie-nsof error: missing %s" % ', '.join(missing),
                  file=sys.stderr)
            sys.exit(httpie.ExitStatus.PLUGIN_ERROR)
